#!/usr/bin/env python3
import argparse
import json
import os
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HISTORY_PATH = Path('/config/www/frigate-alert-history.json')
MAX_EVENTS = 300
FRIGATE_URL = os.environ.get('FRIGATE_URL', 'http://host.docker.internal:5001')


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')


def load_history():
    if not HISTORY_PATH.exists():
        return []
    try:
        data = json.loads(HISTORY_PATH.read_text(encoding='utf-8'))
        return data if isinstance(data, list) else []
    except Exception:
        backup = HISTORY_PATH.with_suffix('.json.broken')
        try:
            HISTORY_PATH.replace(backup)
        except Exception:
            pass
        return []


def atomic_write(data):
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix='.frigate-alert-history.', suffix='.json', dir=str(HISTORY_PATH.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
        os.replace(tmp_name, HISTORY_PATH)
    finally:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass


def fetch_event(event_id):
    if not event_id:
        return {}
    url = f"{FRIGATE_URL.rstrip('/')}/api/events/{urllib.request.quote(event_id, safe='')}"
    try:
        with urllib.request.urlopen(url, timeout=4) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
            return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def normalize_event_info(event):
    if not isinstance(event, dict):
        return {}
    return {
        'camera': event.get('camera') or '',
        'label': event.get('label') or '',
        'start_time': event.get('start_time'),
        'end_time': event.get('end_time'),
        'top_score': event.get('top_score'),
        'score': event.get('score'),
        'false_positive': event.get('false_positive'),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--event-id', required=True)
    parser.add_argument('--camera', default='')
    parser.add_argument('--label', default='person')
    parser.add_argument('--title', default='Frigate: Persona detectada')
    parser.add_argument('--message', default='')
    args = parser.parse_args()

    event_id = args.event_id.strip()
    if not event_id:
        return

    event_info = normalize_event_info(fetch_event(event_id))
    timestamp = now_iso()
    camera = args.camera or event_info.get('camera') or 'camara'
    label = args.label or event_info.get('label') or 'person'
    message = args.message or 'Alerta crítica enviada al iPhone.'

    entry = {
        'event_id': event_id,
        'created_at': timestamp,
        'updated_at': timestamp,
        'camera': camera,
        'label': label,
        'title': args.title,
        'message': message,
        'snapshot_url': f'/api/frigate/notifications/{event_id}/snapshot.jpg',
        'event_url': f'/local/frigate-event.html?event_id={event_id}',
    }
    for key, value in event_info.items():
        if value not in (None, '', []):
            entry[key] = value

    history = [item for item in load_history() if item.get('event_id') != event_id]
    history.insert(0, entry)
    atomic_write(history[:MAX_EVENTS])
    print(f'saved alert {event_id}')


if __name__ == '__main__':
    main()

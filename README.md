# Sentinel Home AI

Configuración doméstica de Frigate, Ring MQTT y Home Assistant para alertas de seguridad.

## Estado actual

- Frigate corre en Docker en la Mac.
- Ring MQTT expone el stream RTSP local en `127.0.0.1:8557`.
- Home Assistant envía una alerta crítica al iPhone cuando Frigate detecta una persona.
- Las zonas de Ring fueron eliminadas: la cámara usa un filtro medio único para `person`.
- La IA generativa/Ollama quedó desactivada porque esta Mac es de uso personal.
- Los bloques de GenAI quedan comentados en `frigate/config/config.yml` para reactivarlos si después hay una máquina dedicada.

## Archivos incluidos

- `frigate/config/config.yml`: configuración principal de Frigate.
- `frigate/docker-compose.yml`: contenedor Frigate.
- `ring-mqtt/docker-compose.yml`: Ring MQTT + Mosquitto local.
- `ring-mqtt/data/config.json`: configuración no secreta de ring-mqtt.
- `homeassistant/config/automations.yaml`: automatizaciones de modo fuera de casa y alertas críticas.
- `homeassistant/config/scripts.yaml`: scripts manuales de prueba.
- `homeassistant/config/www/frigate-event.html`: página local para abrir repeticiones desde notificaciones.

## No incluido por seguridad

- `ring-mqtt/data/ring-state.json` porque contiene token de Ring.
- Bases de datos, storage interno de Home Assistant, clips, snapshots y grabaciones.

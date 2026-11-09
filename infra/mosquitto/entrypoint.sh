#!/bin/sh
set -eu
umask 077
: "${MQTT_USER:?required}" "${MQTT_PASSWORD:?required}"
: "${NOTIFIER_USER:?required}" "${NOTIFIER_PASSWORD:?required}"
: "${EXPORTER_USER:?required}" "${EXPORTER_PASSWORD:?required}"
: "${MQTT_TOPIC:?required}"
if [ ${#MQTT_TOPIC} -gt 255 ] || ! printf '%s' "$MQTT_TOPIC" | grep -Eq '^[A-Za-z0-9_-]+(/[A-Za-z0-9_-]+)*$'; then
    echo 'MQTT_TOPIC must contain slash-separated letters, numbers, underscores or hyphens' >&2; exit 1
fi
if [ "$MQTT_USER" = "$NOTIFIER_USER" ] || [ "$MQTT_USER" = "$EXPORTER_USER" ] || [ "$NOTIFIER_USER" = "$EXPORTER_USER" ]; then
    echo 'MQTT service usernames must be distinct' >&2; exit 1
fi
mkdir -p /run/pico-mqtt
sed "s|__MQTT_TOPIC__|$MQTT_TOPIC|g" /mosquitto/config/mosquitto.conf > /run/pico-mqtt/mosquitto.conf
if grep -q '^connection ' /run/pico-mqtt/mosquitto.conf; then
    printf '\nremote_clientid pico-bridge-%s\n' "$(hostname)" >> /run/pico-mqtt/mosquitto.conf
fi
: > /run/pico-mqtt/passwd
: > /run/pico-mqtt/acl
for account in api notifier exporter; do
    case "$account" in
        api) username="$MQTT_USER"; password="$MQTT_PASSWORD" ;;
        notifier) username="$NOTIFIER_USER"; password="$NOTIFIER_PASSWORD" ;;
        exporter) username="$EXPORTER_USER"; password="$EXPORTER_PASSWORD" ;;
    esac
    case "$username" in *[!a-zA-Z0-9_-]*|'') echo 'MQTT usernames must use letters, numbers, _ or -' >&2; exit 1;; esac
    case "$password" in *'
'*) echo 'MQTT passwords must not contain newlines' >&2; exit 1;; esac
    printf '%s:%s\n' "$username" "$password" >> /run/pico-mqtt/passwd
    case "$account" in
        api) printf 'user %s\ntopic read %s\ntopic write %s/validated\ntopic write pico/health\n\n' "$username" "$MQTT_TOPIC" "$MQTT_TOPIC" ;;
        notifier) printf 'user %s\ntopic read %s\ntopic write %s/status\n\n' "$username" "$MQTT_TOPIC" "$MQTT_TOPIC" ;;
        exporter) printf 'user %s\ntopic read %s/validated\n\n' "$username" "$MQTT_TOPIC" ;;
    esac >> /run/pico-mqtt/acl
done
mosquitto_passwd -U /run/pico-mqtt/passwd
chown -R mosquitto:mosquitto /run/pico-mqtt
exec /docker-entrypoint.sh mosquitto -c /run/pico-mqtt/mosquitto.conf

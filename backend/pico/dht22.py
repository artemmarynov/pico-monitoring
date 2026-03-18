# dht22.py
import time
from machine import Pin
import dht

DHT_PIN = 28
MIN_INTERVAL_MS = 2500

_pin = Pin(DHT_PIN, Pin.IN, Pin.PULL_UP)
_sensor = dht.DHT22(_pin)

_last_good_temp = None
_last_good_hum = None
_last_measure_ms = 0
_ever_succeeded = False


def _is_valid(temp, hum):
    if temp is None or hum is None:
        return False
    if not (-40 <= temp <= 80):
        return False
    if not (0 <= hum <= 100):
        return False
    return True


def _looks_doubled(temp, hum):
    global _last_good_temp, _last_good_hum

    if _last_good_temp is None or _last_good_hum is None:
        return False

    temp_doubled = abs(temp - 2 * _last_good_temp) < 0.8
    hum_doubled = abs(hum - 2 * _last_good_hum) < 1.5

    return temp_doubled and hum_doubled


def _looks_like_unreal_jump(temp, hum):
    global _last_good_temp, _last_good_hum

    if _last_good_temp is None or _last_good_hum is None:
        return False

    if abs(temp - _last_good_temp) > 5:
        return True
    if abs(hum - _last_good_hum) > 20:
        return True

    return False


def _measure_once():
    _sensor.measure()
    time.sleep_ms(50)
    temp = _sensor.temperature()
    hum = _sensor.humidity()
    return temp, hum


def read_dht_once(force=False):
    global _last_good_temp, _last_good_hum, _last_measure_ms, _ever_succeeded

    now = time.ticks_ms()

    if (not force and _last_measure_ms != 0
            and time.ticks_diff(now, _last_measure_ms) < MIN_INTERVAL_MS):
        return _last_good_temp, _last_good_hum

    for _ in range(3):
        try:
            temp, hum = _measure_once()

            if not _is_valid(temp, hum):
                time.sleep_ms(100)
                continue

            temp = round(temp, 1)
            hum = round(hum, 1)

            if _looks_doubled(temp, hum):
                print("⚠️ DHT22 doubled values detected, ignoring:", temp, hum)
                time.sleep_ms(100)
                continue

            if _looks_like_unreal_jump(temp, hum):
                print("⚠️ DHT22 suspicious jump detected, ignoring:", temp, hum)
                time.sleep_ms(100)
                continue

            _last_good_temp = temp
            _last_good_hum = hum
            _last_measure_ms = time.ticks_ms()
            _ever_succeeded = True
            return _last_good_temp, _last_good_hum

        except Exception as e:
            print("⚠️ DHT22 read failed:", e)
            time.sleep_ms(100)

    if not _ever_succeeded:
        return None, None

    return _last_good_temp, _last_good_hum


def wait_for_first_valid_read(max_wait_sec=10):
    global _ever_succeeded

    start = time.ticks_ms()

    # DHT22 после подачи питания лучше дать немного времени
    time.sleep_ms(1500)

    while time.ticks_diff(time.ticks_ms(), start) < max_wait_sec * 1000:
        temp, hum = read_dht_once(force=True)
        if temp is not None and hum is not None:
            print("✅ First valid DHT22 reading:", temp, hum)
            return temp, hum
        time.sleep_ms(500)

    print("⚠️ DHT22 did not return valid data during startup")
    return None, None


def read_temperature_once():
    temp, _ = read_dht_once()
    return temp if temp is not None else -1


def read_humidity_once():
    _, hum = read_dht_once()
    return hum if hum is not None else -1
# dht22.py
import time
from machine import Pin

DHT_PIN = 28
pin = Pin(DHT_PIN, Pin.OUT, Pin.PULL_UP)

ATTEMPT_INTERVAL_MS = 200

_last_good_temp = None
_last_good_hum = None
_last_attempt_ms = 0
_ever_succeeded = False

def _read_raw():
    data = []

    pin.init(Pin.OUT)
    pin.value(0)
    time.sleep_ms(20)
    pin.value(1)
    time.sleep_us(40)
    pin.init(Pin.IN)

    t = time.ticks_us()
    while pin.value() == 1:
        if time.ticks_diff(time.ticks_us(), t) > 150:
            return None

    t = time.ticks_us()
    while pin.value() == 0:
        if time.ticks_diff(time.ticks_us(), t) > 150:
            return None

    t = time.ticks_us()
    while pin.value() == 1:
        if time.ticks_diff(time.ticks_us(), t) > 150:
            return None

    for _ in range(40):
        # LOW ~50 µs
        t = time.ticks_us()
        while pin.value() == 0:
            if time.ticks_diff(time.ticks_us(), t) > 100:
                return None

        t = time.ticks_us()
        while pin.value() == 1:
            if time.ticks_diff(time.ticks_us(), t) > 150:
                break

        bit = 1 if time.ticks_diff(time.ticks_us(), t) > 50 else 0
        data.append(bit)

    return data if len(data) == 40 else None

def _decode(bits):
    if bits is None:
        return None, None

    bytes_arr = []
    for i in range(5):
        byte = 0
        for b in bits[i * 8:(i + 1) * 8]:
            byte = (byte << 1) | b
        bytes_arr.append(byte)

    if bytes_arr[4] != ((bytes_arr[0] + bytes_arr[1] + bytes_arr[2] + bytes_arr[3]) & 0xFF):
        return None, None

    hum_raw = (bytes_arr[0] << 8) | bytes_arr[1]
    temp_raw = (bytes_arr[2] << 8) | bytes_arr[3]

    if temp_raw & 0x8000:
        temp_raw = -(temp_raw & 0x7FFF)

    hum = hum_raw / 10
    temp = temp_raw / 10

    if not (-40 <= temp <= 80):
        return None, None
    if not (0 <= hum <= 100):
        return None, None

    return temp, hum


def _read_sensor():
    for _ in range(3):
        bits = _read_raw()
        t, h = _decode(bits)
        if t is not None and h is not None:
            return t, h
        time.sleep_ms(100)
    return None, None

def _ensure_measurement():
    global _last_good_temp, _last_good_hum, _last_attempt_ms, _ever_succeeded

    now = time.ticks_ms()

    if _last_attempt_ms != 0 and time.ticks_diff(now, _last_attempt_ms) < ATTEMPT_INTERVAL_MS:
        return

    _last_attempt_ms = now

    t, h = _read_sensor()
    if t is None or h is None:
        if not _ever_succeeded:
            print("⚠️ DHT22 read failed")
        return

    _last_good_temp = t
    _last_good_hum = h
    _ever_succeeded = True

def read_temperature_once():
    _ensure_measurement()
    return _last_good_temp if _last_good_temp is not None else -1

def read_humidity_once():
    _ensure_measurement()
    return _last_good_hum if _last_good_hum is not None else -1

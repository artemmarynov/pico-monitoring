import time

import dht
from machine import Pin

DHT_PIN = 28
MIN_INTERVAL_MS = 2500
_sensor = dht.DHT22(Pin(DHT_PIN, Pin.IN, Pin.PULL_UP))
_last_measure_ms = None
_last_result = (None, None)


def _is_valid(temp, hum):
    return temp is not None and hum is not None and -40 <= temp <= 80 and 0 <= hum <= 100


def read_dht_once(force=False):
    global _last_measure_ms, _last_result
    now = time.ticks_ms()
    if _last_measure_ms is not None:
        remaining = MIN_INTERVAL_MS - time.ticks_diff(now, _last_measure_ms)
        if remaining > 0:
            if not force:
                return _last_result
            time.sleep_ms(remaining)
    for attempt in range(3):
        if attempt:
            time.sleep_ms(MIN_INTERVAL_MS)
        _last_measure_ms = time.ticks_ms()
        try:
            _sensor.measure()
            temp, hum = _sensor.temperature(), _sensor.humidity()
            if _is_valid(temp, hum):
                _last_result = (round(temp, 1), round(hum, 1))
                return _last_result
        except Exception as exc:
            print("DHT22 read failed:", exc)
        _last_result = (None, None)
    return _last_result


def wait_for_first_valid_read(max_wait_sec=10):
    start = time.ticks_ms()
    time.sleep_ms(1500)
    while time.ticks_diff(time.ticks_ms(), start) < max_wait_sec * 1000:
        result = read_dht_once(force=True)
        if result[0] is not None:
            return result
    return None, None

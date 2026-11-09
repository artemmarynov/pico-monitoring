import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

FIRMWARE = Path(__file__).resolve().parents[1] / "firmware"


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, FIRMWARE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def dht_module(monkeypatch):
    class Pin:
        IN = 0
        PULL_UP = 1

        def __init__(self, *args):
            pass

    sensor = Mock()
    monkeypatch.setitem(sys.modules, "machine", SimpleNamespace(Pin=Pin))
    monkeypatch.setitem(sys.modules, "dht", SimpleNamespace(DHT22=lambda pin: sensor))
    module = load("pico_dht_test", "dht22.py")
    clock = [10000]
    module.time = SimpleNamespace(
        ticks_ms=lambda: clock[0],
        ticks_diff=lambda a, b: a - b,
        sleep_ms=lambda ms: clock.__setitem__(0, clock[0] + ms),
    )
    return module, sensor, clock


def test_dht_failure_jump_and_recovery(dht_module):
    module, sensor, clock = dht_module
    sensor.temperature.return_value = 20
    sensor.humidity.return_value = 50
    assert module.read_dht_once() == (20, 50)
    clock[0] += 10000
    sensor.measure.side_effect = OSError("sensor failure")
    assert module.read_dht_once() == (None, None)
    assert module.read_dht_once() == (None, None)
    sensor.measure.side_effect = None
    sensor.temperature.return_value = 30
    clock[0] += 10000
    assert module.read_dht_once() == (30, 50)


def test_dht_enforces_minimum_interval(dht_module):
    module, sensor, clock = dht_module
    sensor.temperature.return_value = 20
    sensor.humidity.return_value = 50
    module.read_dht_once()
    module.read_dht_once()
    assert sensor.measure.call_count == 1
    module.read_dht_once(force=True)
    assert clock[0] == 12500
    assert sensor.measure.call_count == 2


def test_wifi_failure_is_explicit(monkeypatch):
    wlan = Mock()
    wlan.isconnected.return_value = False
    wlan.status.return_value = -1
    monkeypatch.setitem(sys.modules, "network", SimpleNamespace(STA_IF=0, WLAN=lambda _: wlan))
    module = load("pico_wifi_test", "wifi.py")
    with pytest.raises(OSError):
        module.connect_wifi("ssid", "password")


def test_publish_remaining_sensors_when_dht_fails(monkeypatch):
    stubs = {
        "ujson": json,
        "secrets": SimpleNamespace(secrets={"TOPIC_SENSOR": b"test"}),
        "wifi": SimpleNamespace(connect_wifi=Mock()),
        "mqtt": SimpleNamespace(connect_mqtt=Mock()),
        "rtc1302": SimpleNamespace(sync_time=Mock()),
        "bh1750": SimpleNamespace(read_lux_once=lambda: 100),
        "mh19": SimpleNamespace(read_co2_once=lambda: 600),
        "dht22": SimpleNamespace(read_dht_once=lambda: (None, None), wait_for_first_valid_read=Mock()),
    }
    for name, module in stubs.items():
        monkeypatch.setitem(sys.modules, name, module)
    module = load("pico_main_test", "main.py")
    client = Mock()
    module.do_measurement(client)
    assert json.loads(client.publish.call_args.args[1]) == dict(temp=None, hum=None, co2=600, lux=100)

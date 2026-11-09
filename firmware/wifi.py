import time

import network


def connect_wifi(ssid, password, retry_max=10):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    for _ in range(retry_max):
        if wlan.isconnected():
            return wlan
        if wlan.status() < 0:
            break
        time.sleep(1)
    raise OSError("Wi-Fi connection failed")

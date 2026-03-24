import time
import network

WIFI_RETRY_MAX = 10

def connect_wifi(ssid: str, password: str, retry_max: int = WIFI_RETRY_MAX):
    print("----------------------------------------------------------------------------------------------")
    print("Connecting to AP:", ssid)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    connected = False
    attempt = 0

    while not connected and attempt < retry_max:
        attempt += 1
        status = wlan.status()

        # status >= 3 -> connected / got IP; status < 0 -> error
        if status < 0 or status >= 3:
            connected = True
        else:
            print("Connection attempt failed:", attempt, "status:", status)
            time.sleep(1)

    if not connected or wlan.ifconfig()[0] == "0.0.0.0":
        print("Bad WiFi connection:", wlan.ifconfig())
    else:
        print("WiFi connected:", wlan.ifconfig())

    return wlan

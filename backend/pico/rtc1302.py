import time
import ntptime
from machine import Pin
from ds1302 import DS1302

TZ_OFFSET = 1 * 3600  # +1h

_rtc = DS1302(Pin(18), Pin(17), Pin(16))
_rtc_synced = False

def sync_time(tz_offset: int = TZ_OFFSET, ntp_host: str = "de.pool.ntp.org"):
    global _rtc_synced

    print("----------------------------------------------------------------------------------------------")
    print("Connecting to NTP:", ntp_host)
    ntptime.host = ntp_host

    try:
        ntptime.settime()
        t = time.localtime(time.time() + tz_offset)
        print("Current time:", t)

        if not _rtc_synced:
            weekday = (t[6] + 1) if t[6] < 6 else 7
            _rtc.date_time([t[0], t[1], t[2], weekday, t[3], t[4], t[5]])
            _rtc.start()
            _rtc_synced = True
            print("✅ DS1302 synced.")

    except Exception as e:
        print("NTP sync failed:", e)

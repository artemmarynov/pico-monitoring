from mhz19e import MHZ19E

ABC_ENABLED = True

_co2_sensor = MHZ19E(
    uart_id=1,
    tx=4,
    rx=5,
    retries=3,
    read_timeout_ms=300,
    inter_cmd_delay_ms=120,
)

def _init_co2_sensor():
    try:
        _co2_sensor.set_abc(ABC_ENABLED)
    except Exception as e:
        print("⚠️ set_abc failed:", e)

    try:
        _co2_sensor.set_range(5000)
    except Exception as e:
        print("⚠️ set_range failed:", e)

_init_co2_sensor()

def read_co2_once() -> int:
    try:
        data = _co2_sensor.read()
        return int(data.get("co2", -1))
    except Exception:
        return -1

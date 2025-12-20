from machine import Pin, I2C

BH1750_ADDR = 0x23

_i2c = I2C(0, scl=Pin(1), sda=Pin(0))

def _init_bh1750():
    try:
        # continuous high-res mode
        _i2c.writeto(BH1750_ADDR, b"\x10")
        print("✅ BH1750 init OK")
    except Exception as e:
        print("⚠️ BH1750 init failed:", e)

_init_bh1750()

def read_lux_once() -> float:
    try:
        data = _i2c.readfrom(BH1750_ADDR, 2)
        lux = round((data[0] << 8 | data[1]) / 1.2, 1)
        return lux
    except Exception:
        return -1

from machine import UART, Pin
import time

class MHZ19E:
    REQ_READ        = b'\xFF\x01\x86\x00\x00\x00\x00\x00\x79'
    CMD_ABC_ON      = b'\xFF\x01\x79\xA0\x00\x00\x00\x00\xE6'
    CMD_ABC_OFF     = b'\xFF\x01\x79\x00\x00\x00\x00\x00\x86'
    CMD_ZERO_CAL    = b'\xFF\x01\x87\x00\x00\x00\x00\x00\x78'
    CMD_RANGE_2000  = b'\xFF\x01\x99\x00\x00\x00\x07\xD0\x8F'
    CMD_RANGE_5000  = b'\xFF\x01\x99\x00\x00\x00\x13\x88\xCB'
    CMD_RANGE_10000 = b'\xFF\x01\x99\x00\x00\x00\x27\x10\x2F'

    def __init__(self, uart_id=1, tx=4, rx=5, baud=9600,
                 retries=3, read_timeout_ms=300, inter_cmd_delay_ms=120):
        self.uart = UART(uart_id, baudrate=baud, bits=8, parity=None, stop=1,
                         tx=Pin(tx), rx=Pin(rx))
        self.retries = int(retries)
        self.read_timeout_ms = int(read_timeout_ms)
        self.inter_cmd_delay_ms = int(inter_cmd_delay_ms)

    @staticmethod
    def _checksum(frame9):
        s = sum(frame9[1:8]) & 0xFF
        return (0xFF - s + 1) & 0xFF

    @staticmethod
    def _valid_frame(buf):
        return (
            buf and len(buf) == 9 and
            buf[0] == 0xFF and buf[1] == 0x86 and
            buf[8] == MHZ19E._checksum(buf)
        )

    def _flush_rx(self):
        while self.uart.any():
            self.uart.read()

    def _read_exact_9(self):
        start = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start) < self.read_timeout_ms:
            if self.uart.any() >= 9:
                return self.uart.read(9)
            time.sleep_ms(5)
        return None

    def read(self):
        for _ in range(self.retries):
            try:
                self._flush_rx()
                self.uart.write(self.REQ_READ)
                time.sleep_ms(self.inter_cmd_delay_ms)

                resp = self._read_exact_9()
                if self._valid_frame(resp):
                    co2 = resp[2] * 256 + resp[3]
                    temp = resp[4] - 40
                    status = resp[5]
                    return {'co2': co2, 'temp': temp, 'status': status}
            except Exception:
                pass
            time.sleep_ms(50)
        return {'co2': None, 'temp': None, 'status': None}

    def read_ppm(self):
        v = self.read()
        return v['co2'] if (v and v.get('co2') is not None) else -1

    # ----- Service commands -----
    def set_abc(self, enabled=True):
        self._flush_rx()
        self.uart.write(self.CMD_ABC_ON if enabled else self.CMD_ABC_OFF)
        time.sleep_ms(self.inter_cmd_delay_ms)

    def zero_point_calibration(self):
        """
        Zero calibration per vendor guide:
        place sensor in fresh air (~400 ppm), let stabilize ~20 min, then call this.
        """
        self._flush_rx()
        self.uart.write(self.CMD_ZERO_CAL)
        time.sleep_ms(self.inter_cmd_delay_ms)

    def span_point_calibration(self, span_ppm):
        """
        Span calibration to known reference (e.g., 2000 ppm).
        Frame: FF 01 88 [SPAN_H] [SPAN_L] 00 00 00 [CHK]
        """
        span_ppm = int(span_ppm)
        high = (span_ppm // 256) & 0xFF
        low  = span_ppm % 256
        frame = bytearray([0xFF,0x01,0x88,high,low,0x00,0x00,0x00,0x00])
        frame[8] = self._checksum(frame)
        self._flush_rx()
        self.uart.write(frame)
        time.sleep_ms(self.inter_cmd_delay_ms)

    def set_range(self, rng=5000):
        self._flush_rx()
        if rng == 2000:
            self.uart.write(self.CMD_RANGE_2000)
        elif rng == 10000:
            self.uart.write(self.CMD_RANGE_10000)
        else:
            self.uart.write(self.CMD_RANGE_5000)
        time.sleep_ms(self.inter_cmd_delay_ms)

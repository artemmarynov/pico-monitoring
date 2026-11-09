"""The MQTT wire format shared by ingestion and alerting."""

import json
import math
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Measurement:
    temp: float | None
    hum: float | None
    co2: float | None
    lux: float | None

    @classmethod
    def from_payload(cls, payload: bytes) -> "Measurement":
        if len(payload) > 16384:
            raise ValueError("MQTT payload exceeds 16 KiB")
        try:
            data = json.loads(payload)
        except (ValueError, UnicodeError, RecursionError) as exc:
            raise ValueError("Invalid MQTT JSON") from exc
        if not isinstance(data, dict):
            raise ValueError("MQTT JSON must be an object")

        def number(key, lower, upper=None):
            value = data.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return None
            try:
                value = float(value)
            except OverflowError:
                return None
            if not math.isfinite(value) or value < lower:
                return None
            if upper is not None and value > upper:
                return None
            return value

        result = cls(number("temp", -40, 80), number("hum", 0, 100), number("co2", 0, 5000), number("lux", 0))
        if all(value is None for value in asdict(result).values()):
            raise ValueError("MQTT message contains no valid measurements")
        return result

    def as_dict(self):
        return asdict(self)

    def db_values(self):
        return self.temp, self.hum, self.co2, self.lux

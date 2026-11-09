import time


class SensorWatch:
    """One outage alert, followed by one recovery alert; only valid messages reset the clock."""

    def __init__(self, stale_after_seconds=60, clock=time.monotonic):
        self.stale_after_seconds = stale_after_seconds
        self.clock = clock
        self.last_received = clock()
        self.alerted = False

    def received(self):
        self.last_received = self.clock()
        recovering = self.alerted
        self.alerted = False
        return "Sensor measurements resumed." if recovering else None

    def check(self):
        if not self.alerted and self.clock() - self.last_received > self.stale_after_seconds:
            self.alerted = True
            return f"Sensor offline: no valid measurements for more than {self.stale_after_seconds} seconds."
        return None

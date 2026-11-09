import logging
import queue
import threading
import time

log = logging.getLogger(__name__)


class AlertRules:
    def __init__(self, cooldown=300, clock=time.monotonic):
        self.cooldown = cooldown
        self.clock = clock
        self.active = set()
        self.last_attempt = None

    def evaluate(self, measurement):
        checks = {
            "co2": (measurement.co2, lambda v: v > 1500, "High CO?"),
            "temp": (measurement.temp, lambda v: v > 25 or v < 15, "Extreme temperature"),
            "hum": (measurement.hum, lambda v: v > 70 or v < 30, "Extreme humidity"),
        }
        reasons = []
        for name, (value, violates, description) in checks.items():
            # Missing readings must not clear an existing violation.
            if value is None:
                continue
            if violates(value):
                self.active.add(name)
                reasons.append(f"{description}: {value}")
            else:
                self.active.discard(name)
        if not self.active:
            self.last_attempt = None
            return None
        if not reasons:
            return None
        now = self.clock()
        if self.last_attempt is not None and now - self.last_attempt < self.cooldown:
            return None
        self.last_attempt = now
        return (
            "\n".join(reasons)
            + "\n\n"
            + "\n".join(
                f"{key}: {value if value is not None else 'unavailable'}"
                for key, value in measurement.as_dict().items()
            )
        )


class AlertWorker:
    """One sender thread; a slow provider cannot block the MQTT heartbeat."""

    def __init__(self, client):
        self.client = client
        self.pending = queue.Queue(maxsize=1)
        self.stopped = threading.Event()
        self.thread = threading.Thread(target=self.run, name="alert-sender", daemon=True)

    def start(self):
        self.thread.start()

    def submit(self, body):
        try:
            self.pending.put_nowait(body)
        except queue.Full:
            log.warning("Alert queue full; skipped notification")

    def deliver(self, body):
        if self.client is None:
            log.warning("Notification (provider not configured): %s", body)
            return False
        try:
            success = bool(self.client.notify(title="Pico Environment Alert", body=body))
            if success:
                log.info("Notification sent")
            else:
                log.error("Notification provider reported failure")
            return success
        except Exception:
            log.error("Notification provider failed")
            return False

    def run(self):
        while not self.stopped.is_set():
            try:
                body = self.pending.get(timeout=0.5)
            except queue.Empty:
                continue
            self.deliver(body)
            self.pending.task_done()

    def close(self):
        self.stopped.set()
        self.thread.join(timeout=5)

import sys
import time
from pathlib import Path

HEARTBEAT = Path("/tmp/notifier-heartbeat")


def healthy(path=HEARTBEAT, now=None):
    try:
        age = (time.monotonic() if now is None else now) - float(path.read_text())
        return 0 <= age < 30
    except (OSError, ValueError):
        return False


if __name__ == "__main__":
    sys.exit(0 if healthy() else 1)

"""Check a disposable stack: no public broker, production env or existing volumes."""

import base64
import json
import os
import secrets
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]


def run_stack(env_file, configuration):
    environment = {**os.environ, **configuration}
    project = "pico-monitoring-smoke-" + uuid4().hex[:8]
    compose = [
        "docker",
        "compose",
        "--project-name",
        project,
        "--env-file",
        str(env_file),
        "-f",
        "docker-compose.yml",
        "-f",
        "tests/compose.smoke.yml",
    ]

    def run(*args, capture=False):
        return subprocess.run(
            compose + list(args), cwd=ROOT, env=environment, check=True, text=True, capture_output=capture
        ).stdout

    def url(service, port):
        return "http://" + run("port", service, str(port), capture=True).strip()

    try:
        run("config", "--quiet")
        run(
            "up",
            "--build",
            "--wait",
            "--wait-timeout",
            "120",
            "frontend",
            "mqtt-exporter",
            "notifier",
            "prometheus",
            "grafana",
        )
        frontend, exporter = url("frontend", 80), url("mqtt-exporter", 9641)
        topic = configuration["MQTT_TOPIC"]
        opener = urllib.request.build_opener()
        assert isinstance(json.load(opener.open(frontend + "/api/history", timeout=5)), list)
        for path in ["/api/auth/me", "/api/auth/login"]:
            request = urllib.request.Request(
                frontend + path,
                data=b"{}" if path.endswith("login") else None,
                headers={"Content-Type": "application/json"},
            )
            try:
                opener.open(request, timeout=5)
                raise AssertionError("Removed account endpoint is still available")
            except urllib.error.HTTPError as exc:
                assert exc.code == 404
        # Broker access is authenticated; a rejected client must fail.
        rejected = subprocess.run(
            compose
            + [
                "exec",
                "-T",
                "mosquitto",
                "mosquitto_pub",
                "-h",
                "127.0.0.1",
                "-t",
                topic,
                "-m",
                "{}",
            ],
            cwd=ROOT,
            env=environment,
            capture_output=True,
        )
        assert rejected.returncode != 0
        for payload in ["[]", '{"co2":654,"temp":22.5,"hum":50,"lux":100}']:
            run(
                "exec",
                "-T",
                "mosquitto",
                "mosquitto_pub",
                "-h",
                "127.0.0.1",
                "-p",
                "1884",
                "-t",
                topic,
                "-q",
                "1",
                "-m",
                payload,
            )
        deadline = time.monotonic() + 15
        while True:
            rows = json.load(opener.open(frontend + "/api/history", timeout=5))
            metrics = urllib.request.urlopen(exporter + "/metrics", timeout=5).read().decode()
            if (
                rows
                and rows[-1]["co2"] == 654
                and any(
                    line.startswith("pico_co2{") and float(line.split()[1]) == 654
                    for line in metrics.splitlines()
                )
            ):
                break
            if time.monotonic() >= deadline:
                raise AssertionError(
                    f"MQTT path failed: rows={rows!r}, co2_metrics={[line for line in metrics.splitlines() if 'pico_co2' in line]!r}"
                )
            time.sleep(0.2)
        assert rows[-1]["time"].endswith("+00:00")
        snapshot = json.load(opener.open(frontend + "/api/status", timeout=5))
        assert snapshot["online"] and snapshot["last_received_at"]
        # Web clients cannot scrape the internal monitoring endpoint.
        try:
            opener.open(frontend + "/api/metrics", timeout=5)
            raise AssertionError("Monitoring endpoint must stay internal")
        except urllib.error.HTTPError as exc:
            assert exc.code == 404
        deadline = time.monotonic() + 10
        while json.load(opener.open(frontend + "/api/status", timeout=5))["online"]:
            if time.monotonic() > deadline:
                raise AssertionError("Stale sensor is still shown online")
            time.sleep(0.2)
        grafana = url("grafana", 3000)
        credentials = f"{configuration['GRAFANA_ADMIN_USER']}:{configuration['GRAFANA_ADMIN_PASSWORD']}"
        monitor = urllib.request.build_opener()
        monitor.addheaders = [("Authorization", "Basic " + base64.b64encode(credentials.encode()).decode())]
        dashboard = json.load(monitor.open(grafana + "/api/dashboards/uid/pico-environment", timeout=10))
        assert len(dashboard["dashboard"]["panels"]) == 10
        for uid in ["pico-prometheus", "pico-postgres"]:
            health = json.load(monitor.open(grafana + f"/api/datasources/uid/{uid}/health", timeout=10))
            assert health["status"].lower() == "ok", health
        query = {
            "from": str(int((time.time() - 600) * 1000)),
            "to": str(int(time.time() * 1000)),
            "queries": [
                {
                    "refId": "A",
                    "datasource": {"uid": "pico-postgres", "type": "grafana-postgresql-datasource"},
                    "rawQuery": True,
                    "format": "time_series",
                    "rawSql": "SELECT time, co2 FROM sensor_metrics ORDER BY time DESC LIMIT 1",
                    "intervalMs": 10000,
                    "maxDataPoints": 100,
                }
            ],
        }
        request = urllib.request.Request(
            grafana + "/api/ds/query",
            data=json.dumps(query).encode(),
            headers={"Content-Type": "application/json"},
        )
        result = json.load(monitor.open(request, timeout=10))["results"]["A"]
        assert not result.get("error") and result.get("frames"), result
        assert urllib.request.urlopen(frontend + "/", timeout=5).status == 200
        run("exec", "-T", "notifier", "python", "-m", "notifier.healthcheck")
        print(
            "Smoke passed: public metrics, removed account endpoints, custom MQTT topic, freshness, database, Grafana"
        )
    except Exception:
        run(
            "logs",
            "--tail",
            "30",
            "fastapi",
            "mqtt-exporter",
            "mosquitto",
            "notifier",
            "grafana",
            "prometheus",
        )
        raise
    finally:
        # Only the newly generated test project is stopped. PostgreSQL uses tmpfs.
        run("down", "--remove-orphans")


def main():
    configuration = {
        "PG_USER": "pico_test",
        "MQTT_TOPIC": "smoke/room_1/environment",
        "SENSOR_STALE_SECONDS": "3",
        "GRAFANA_DB_USER": "pico_grafana",
        "PG_DB": "pico_test",
        "MQTT_USER": "pico-api",
        "NOTIFIER_USER": "pico-notifier",
        "EXPORTER_USER": "pico-exporter",
        "GRAFANA_ADMIN_USER": "admin",
        "NOTIFIER_APPRISE_URL": "",
    }
    for key in (
        "PG_PASSWORD",
        "MQTT_PASSWORD",
        "NOTIFIER_PASSWORD",
        "EXPORTER_PASSWORD",
        "GRAFANA_ADMIN_PASSWORD",
        "GRAFANA_DB_PASSWORD",
    ):
        configuration[key] = secrets.token_urlsafe(36)
    with TemporaryDirectory(prefix="pico-smoke-") as directory:
        env_file = Path(directory) / "config.env"
        env_file.write_text("".join(f"{key}={value}\n" for key, value in configuration.items()))
        env_file.chmod(0o600)
        run_stack(env_file, configuration)


if __name__ == "__main__":
    main()

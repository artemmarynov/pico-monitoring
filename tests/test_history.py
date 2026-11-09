import pytest


@pytest.fixture
async def history_client(client, pool):
    async with pool.acquire() as connection:
        await connection.execute("""INSERT INTO sensor_metrics(time, temperature, humidity, co2, lighting)
            SELECT '2026-01-01T00:00:00Z'::timestamptz + i * interval '1 minute',
            20, 50, 500 + i, 100 FROM generate_series(0,179) i""")
    return client


async def test_latest_records_are_chronological_without_login(history_client):
    response = await history_client.get("/history")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 100
    assert data[0]["co2"] == 580
    assert data[-1]["co2"] == 679
    assert data[0]["time"] == "2026-01-01T01:20:00+00:00"


async def test_dates_apply_without_aggregation(history_client):
    response = await history_client.get(
        "/history", params={"start_date": "2026-01-01T02:00:00Z", "end_date": "2026-01-01T02:09:00Z"}
    )
    data = response.json()
    assert len(data) == 10
    assert data[0]["co2"] == 620 and data[-1]["co2"] == 629


async def test_latest_aggregate_buckets_are_chronological(history_client):
    response = await history_client.get("/history", params={"aggregate": "hour", "limit": 2})
    data = response.json()
    assert [row["co2"] for row in data] == [589.5, 649.5]
    assert [row["time"] for row in data] == ["2026-01-01T01:00:00+00:00", "2026-01-01T02:00:00+00:00"]


async def test_timezone_offsets_and_naive_dates(history_client):
    for start in ["2026-01-01T01:00:00+01:00", "2026-01-01T00:00:00"]:
        data = (
            await history_client.get(
                "/history", params={"start_date": start, "end_date": "2026-01-01T00:00:00Z"}
            )
        ).json()
        assert len(data) == 1 and data[0]["co2"] == 500
        assert data[0]["time"].endswith("+00:00")


@pytest.mark.parametrize(
    "params",
    [
        dict(limit=-1),
        dict(limit=0),
        dict(limit=1001),
        dict(aggregate="week"),
        dict(start_date="invalid"),
        dict(start_date="2026-02-01", end_date="2026-01-01"),
    ],
)
async def test_invalid_history_parameters(client, params):
    assert (await client.get("/history", params=params)).status_code == 422


async def test_user_management_endpoints_are_removed(client):
    for path in ["/auth/login", "/auth/logout", "/admin/bootstrap", "/admin/create"]:
        assert (await client.post(path, json={})).status_code == 404
    for path in ["/auth/me", "/admin/ping"]:
        assert (await client.get(path)).status_code == 404


@pytest.mark.parametrize("aggregate", [None, "hour"])
async def test_legacy_null_time_and_nonfinite_values_do_not_break_history(client, pool, aggregate):
    async with pool.acquire() as connection:
        await connection.execute(
            "INSERT INTO sensor_metrics(time, co2) VALUES (NULL, 600), (now(), 'NaN'::real)"
        )
    response = await client.get("/history", params={"aggregate": aggregate} if aggregate else {})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1 and data[0]["co2"] is None

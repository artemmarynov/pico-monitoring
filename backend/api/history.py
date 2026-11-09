import math
from datetime import datetime, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query, Request

router = APIRouter()


def utc(value):
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


@router.get("/history")
async def history(
    request: Request,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    aggregate: Literal["minute", "hour", "day", "month"] | None = None,
):
    start = utc(start_date) if start_date else None
    end = utc(end_date) if end_date else None
    if start and end and start > end:
        raise HTTPException(422, "start_date must not exceed end_date")
    params, conditions = [], ["time IS NOT NULL"]
    for value, operator in [(start, ">="), (end, "<=")]:
        if value is not None:
            params.append(value)
            conditions.append(f"time {operator} ${len(params)}")
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    if aggregate:
        # aggregate is constrained by Literal, not interpolated from arbitrary input.
        selection = f"""SELECT date_trunc('{aggregate}', time, 'UTC') AS time,
            ROUND(AVG(temperature)::numeric, 2)::float AS temperature,
            ROUND(AVG(humidity)::numeric, 2)::float AS humidity,
            ROUND(AVG(co2)::numeric, 2)::float AS co2,
            ROUND(AVG(lighting)::numeric, 2)::float AS lighting
            FROM sensor_metrics{where} GROUP BY 1"""
    else:
        selection = f"SELECT time, temperature, humidity, co2, lighting FROM sensor_metrics{where}"
    params.append(limit)
    query = f"SELECT * FROM ({selection} ORDER BY time DESC LIMIT ${len(params)}) AS recent ORDER BY time ASC"
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
    result = []
    for row in rows:
        item = dict(row)
        item["time"] = row["time"].astimezone(timezone.utc).isoformat()
        for key in ("temperature", "humidity", "co2", "lighting"):
            if item[key] is not None and not math.isfinite(item[key]):
                item[key] = None
        result.append(item)
    return result

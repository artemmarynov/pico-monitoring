import os
import asyncio
import json
from contextlib import asynccontextmanager
import asyncpg
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from aiomqtt import Client as MQTTClient
from datetime import datetime, timezone
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Query
from datetime import datetime
from typing import Optional
# CONFIGURATION
MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")

DATABASE_CONFIG = {
    "host": os.getenv("PG_HOST", "postgres"),
    "port": int(os.getenv("PG_PORT", "5432")),
    "user": os.getenv("PG_USER", "postgres"),
    "password": os.getenv("PG_PASSWORD", "admin"),
    "database": os.getenv("PG_DB", "metrics")
}


# --- WEBSOCKET MANAGER ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # If the connection is already dead and we hadn't disconnected it yet.
                pass

manager = ConnectionManager()

# --- MQTT BRIDGE TASK ---
async def mqtt_bridge(app: FastAPI):
    """Listens to MQTT, and writes the data into the database and sends it to websockets."""
    while True:
        try:
            async with MQTTClient(MQTT_BROKER) as client:
                await client.subscribe("pico/env")
                async for message in client.messages:
                    data = json.loads(message.payload.decode()) # type: ignore
                    
                    # 1. Save to database
                    async with app.state.pool.acquire() as conn:
                        await conn.execute(
                                """
                                INSERT INTO sensor_metrics (time, temperature, humidity, co2, lighting) 
                                VALUES (NOW(), $1, $2, $3, $4)
                                """,
                                data.get("temp"), 
                                data.get("hum"), 
                                data.get("co2"), 
                                data.get("lux")
                        )
                    # 2. Send to websockets for real-time data for web.
                    await manager.broadcast(data)
        except Exception as e:
            print(f"MQTT Error: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)

# --- LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"DEBUG: Connecting to DB with config: {DATABASE_CONFIG}")
    # Create a connection pool at the start of the server
    app.state.pool = await asyncpg.create_pool(**DATABASE_CONFIG)    

    # 2) Create table if not exists
    async with app.state.pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS sensor_metrics (
                time TIMESTAMP,
                temperature REAL,
                humidity REAL,
                co2 REAL,
                lighting REAL
            );
        """)
        print("DEBUG: sensor_metrics table ensured")

    # Запускаем MQTT мост фоном
    mqtt_task = asyncio.create_task(mqtt_bridge(app))

    yield
    
    # Close everything after shuting down
    mqtt_task.cancel()
    await app.state.pool.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API ENDPOINTS ---

@app.get("/history")
async def get_history(
    limit: int = 100, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    aggregate: Optional[str] = None
):
    print(f"DEBUG: Received request with aggregate='{aggregate}'")

    async with app.state.pool.acquire() as conn:
        allowed = ["minute", "hour", "day", "month"]
        
        if aggregate and aggregate in allowed:
            query = f"""
                SELECT 
                    date_trunc('{aggregate}', time)::timestamp AS bucket, 
                    ROUND(AVG(temperature)::numeric, 2)::float AS temperature, 
                    ROUND(AVG(humidity)::numeric, 2)::float AS humidity, 
                    ROUND(AVG(co2)::numeric, 2)::float AS co2
                FROM sensor_metrics
            """
            params = []
            where_clauses = []
            
            if start_date:
                where_clauses.append(f"time >= ${len(params)+1}")
                params.append(datetime.fromisoformat(start_date))
            if end_date:
                where_clauses.append(f"time <= ${len(params)+1}")
                params.append(datetime.fromisoformat(end_date))
                
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            query += " GROUP BY bucket ORDER BY bucket ASC"
            
            print(f"DEBUG: Executing Aggregated SQL: {query}", flush=True)
            rows = await conn.fetch(query, *params)
            
            return [
                {
                    "time": row["bucket"].isoformat(), 
                    "temperature": row["temperature"], 
                    "humidity": row["humidity"], 
                    "co2": row["co2"]
                } for row in rows
            ]  
        else:
            print("DEBUG: Performing RAW SELECT (Realtime)")
            query = """
                SELECT time, temperature, humidity, co2 
                FROM sensor_metrics 
                ORDER BY time DESC LIMIT $1
            """
            rows = await conn.fetch(query, limit)
            rows = list(reversed(rows))

    return [dict(row) for row in rows]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Just holding the connection
    except WebSocketDisconnect:
        manager.disconnect(websocket)



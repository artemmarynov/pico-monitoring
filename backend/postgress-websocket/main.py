import os
import asyncio
import json
from contextlib import asynccontextmanager
import asyncpg
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from aiomqtt import Client as MQTTClient
from datetime import datetime, timezone
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Response, Cookie, Depends
from passlib.context import CryptContext


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
                await client.subscribe("artem/pico2wh/env")
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

    async with app.state.pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGSERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'USER',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """)
        print("DEBUG: users table ensured")

    # Запускаем MQTT мост фоном
    mqtt_task = asyncio.create_task(mqtt_bridge(app))

    yield
    
    # Close everything after shuting down
    mqtt_task.cancel()
    await app.state.pool.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # твой React origin(ы)
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



pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME_LONG_RANDOM_SECRET")
JWT_ALG = "HS256"
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "60"))
COOKIE_NAME = "access_token"

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(p: str, hashed: str) -> bool:
    return pwd_context.verify(p, hashed)

def create_access_token(user_id: int, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# --- dependencies ---
async def get_current_user(token: str | None = Cookie(default=None, alias=COOKIE_NAME)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return decode_token(token)

def require_admin(user_claims: dict = Depends(get_current_user)) -> dict:
    if user_claims.get("role") != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin only")
    return user_claims

from pydantic import BaseModel, EmailStr

class LoginReq(BaseModel):
    email: EmailStr
    password: str

@app.post("/auth/login")
async def auth_login(payload: LoginReq, response: Response):
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, password_hash, role, is_active FROM users WHERE email=$1",
            str(payload.email)
        )

    if not row or not row["is_active"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(row["id"], row["role"])

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
        max_age=ACCESS_TOKEN_MINUTES * 60,
    )
    return {"ok": True, "role": row["role"]}

@app.post("/auth/logout")
async def auth_logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"ok": True}

@app.get("/auth/me")
async def auth_me(user_claims: dict = Depends(get_current_user)):
    return {"user_id": user_claims["sub"], "role": user_claims["role"]}

@app.get("/admin/ping")
async def admin_ping(_: dict = Depends(require_admin)):
    return {"ok": True, "msg": "Admin access granted"}

class BootstrapAdminReq(BaseModel):
    email: EmailStr
    password: str
    secret: str

BOOTSTRAP_SECRET = os.getenv("BOOTSTRAP_SECRET", "")

@app.post("/admin/bootstrap")
async def bootstrap_admin(payload: BootstrapAdminReq):
    if not BOOTSTRAP_SECRET or payload.secret != BOOTSTRAP_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    pw_hash = hash_password(payload.password)

    async with app.state.pool.acquire() as conn:
        existing = await conn.fetchval("SELECT 1 FROM users WHERE email=$1", str(payload.email))
        if existing:
            raise HTTPException(status_code=409, detail="User already exists")

        await conn.execute(
            "INSERT INTO users(email, password_hash, role, is_active) VALUES ($1, $2, 'ADMIN', TRUE)",
            str(payload.email),
            pw_hash
        )
    return {"ok": True}


from pydantic import BaseModel, EmailStr

class CreateAdminReq(BaseModel):
    email: EmailStr
    password: str

@app.post("/admin/create")
async def create_admin(payload: CreateAdminReq, _: dict = Depends(require_admin)):
    pw_hash = hash_password(payload.password)

    async with app.state.pool.acquire() as conn:
        exists = await conn.fetchval("SELECT 1 FROM users WHERE email=$1", str(payload.email))
        if exists:
            raise HTTPException(status_code=409, detail="User already exists")

        await conn.execute(
            """
            INSERT INTO users (email, password_hash, role, is_active)
            VALUES ($1, $2, 'ADMIN', TRUE)
            """,
            str(payload.email),
            pw_hash
        )

    return {"ok": True}
@app.get("/test")
def test():
    return {"message": "new code is live"}
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from pydantic import BaseModel
import bcrypt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "postgresql+psycopg://postgres.vzypnsvsmggemyjleuic:BrivioSecure2026!%23@aws-1-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require"
engine = create_engine(DATABASE_URL)

class UserAuth(BaseModel):
    email: str
    password: str

@app.get("/health")
def health():
    return {"status": "online"}

@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as conn:
            return {"database": "connected"}
    except Exception as e:
        return {"database": str(e)}

@app.post("/create-user")
def create_user(data: dict):
    email = data.get("email", "").strip()

    if not email:
        return {"error": "email is required"}

    if "@" not in email:
        return {"error": "invalid email"}

    with engine.connect() as conn:
        existing = conn.execute(
            text("select * from users where email = :email"),
            {"email": email}
        ).fetchone()

    if existing:
        return {"error": "email already exists"}

    with engine.begin() as conn:
        conn.execute(
            text("insert into users (email) values (:email)"),
            {"email": email}
        )

    return {"status": "user created"}

@app.get("/users")
def get_users():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("select * from users"))
            users = [dict(row._mapping) for row in result]
        return users
    except Exception as e:
        return {"error": str(e)}

@app.post("/register")
def register(user: UserAuth):
    hashed = bcrypt.hashpw(
        user.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    with engine.connect() as conn:
        existing = conn.execute(
            text("select * from users where email = :email"),
            {"email": user.email}
        ).fetchone()

    if existing:
        return {"error": "user already exists"}

    with engine.begin() as conn:
        conn.execute(
            text("insert into users (email, password) values (:email, :password)"),
            {"email": user.email, "password": hashed}
        )

    return {"status": "registered"}

@app.post("/login")
def login(user: UserAuth):
    with engine.connect() as conn:
        existing = conn.execute(
            text("select * from users where email = :email"),
            {"email": user.email}
        ).fetchone()

    if not existing:
        return {"error": "user not found"}

    stored_password = existing._mapping.get("password")

    if not stored_password:
        return {"error": "no password set"}

    if not bcrypt.checkpw(
        user.password.encode("utf-8"),
        stored_password.encode("utf-8")
    ):
        return {"error": "invalid password"}

    return {"status": "logged in"}

# 🔴 WEBSOCKET CHAT

active_connections = []

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            message = await websocket.receive_text()

            for connection in active_connections:
                await connection.send_text(message)

    except WebSocketDisconnect:
        active_connections.remove(websocket)
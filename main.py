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

@app.get("/test")
def test():
    return {"message": "backend live"}

# ---------- USERS ----------

@app.post("/create-user")
def create_user(data: dict):
    email = data.get("email", "").strip()

    if not email:
        return {"error": "email required"}

    with engine.begin() as conn:
        conn.execute(
            text("insert into users (email) values (:email)"),
            {"email": email}
        )

    return {"status": "user created"}

@app.get("/users")
def get_users():
    with engine.connect() as conn:
        result = conn.execute(text("select * from users"))
        return [dict(row._mapping) for row in result]

# ---------- AUTH ----------

@app.post("/register")
def register(user: UserAuth):
    hashed = bcrypt.hashpw(
        user.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

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

    stored = existing._mapping.get("password")

    if not bcrypt.checkpw(user.password.encode(), stored.encode()):
        return {"error": "invalid password"}

    return {"status": "logged in"}

# ---------- WEBSOCKET (STABLE TEST VERSION) ----------

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"echo: {data}")
    except WebSocketDisconnect:
        print("client disconnected")
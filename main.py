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
    hashed
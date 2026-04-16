from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from sqlalchemy import create_engine, text
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ HEALTH CHECK
@app.get("/health")
def health():
    return {"status": "online"}


# 🔗 DATABASE CONNECTION
DATABASE_URL = "postgresql+psycopg://postgres.vzypnsvsmggemyjleuic:BrivioSecure2026!%23@aws-1-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require"

engine = create_engine(DATABASE_URL)


# 🧪 TEST CONNECTION
@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as conn:
            return {"database": "connected"}
    except Exception as e:
        return {"database": str(e)}


# 📦 REQUEST BODY MODEL (THIS IS NEW)
class UserCreate(BaseModel):
    email: str


# ✅ CREATE USER (REAL API - POST)
@app.post("/create-user")
def create_user(user: UserCreate):
    try:
        with engine.begin() as conn:
            conn.execute(
                text("insert into users (email) values (:email)"),
                {"email": user.email}
            )
        return {"status": "user created"}
    except Exception as e:
        return {"error": str(e)}
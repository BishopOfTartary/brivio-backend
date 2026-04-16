from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from sqlalchemy import create_engine, text

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "online"}

DATABASE_URL = "postgresql+psycopg://postgres.vzypnsvsmggemyjleuic:BrivioSecure2026!%23@aws-1-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require"

engine = create_engine(DATABASE_URL)

@app.get("/db-test")
def db_test():
    with engine.connect() as conn:
        return {"database": "connected"}

@app.post("/create-user")
def create_user(data: dict):
    email = data["email"]
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
        users = [dict(row._mapping) for row in result]
    return users
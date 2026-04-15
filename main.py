from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

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
from sqlalchemy import create_engine
DATABASE_URL = "postgresql+psycopg://postgres.vzypnsvsmggemyjleuic:BrivioSecure2026!%23@aws-1-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require"
engine = create_engine(DATABASE_URL)

@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as conn:
            return {"database": "connected"}
    except Exception as e:
        return {"database": str(e)}


# 👇 ADD THIS PART HERE (new)
@app.post("/create-user")
def create_user(email: str):
    with engine.connect() as conn:
        conn.execute(
            f"insert into users (email) values ('{email}')"
        )
    return {"status": "user created"}
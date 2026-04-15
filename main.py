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

DATABASE_URL = "postgresql://postgres:Damiennaes7%24@db.rkorxkgqnavnlgirrbvp.supabase.co:5432/postgres"
engine = create_engine(DATABASE_URL)

@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as conn:
            return {"database": "connected"}
    except:
        return {"database": "failed"}
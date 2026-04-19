print("DATABASE WORKING VERSION")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from pydantic import BaseModel

app = FastAPI()

# 🔥 CORS (required)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 DATABASE
DATABASE_URL = "postgresql+psycopg://postgres.vzypnsvsmggemyjleuic:BrivioSecure2026!%23@aws-1-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require"
engine = create_engine(DATABASE_URL)

# 🔥 MODELS
class ArtItem(BaseModel):
    title: str
    price: str
    image: str

class BusinessItem(BaseModel):
    title: str
    price: str

# 🔥 TEST
@app.get("/")
def root():
    return {"status": "backend live"}

# 🔥 ADD ART
@app.post("/add-art")
def add_art(item: ArtItem):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO art (title, price, image) VALUES (:title, :price, :image)"),
            item.dict()
        )
    return {"status": "saved"}

# 🔥 GET ART
@app.get("/art")
def get_art():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM art ORDER BY id DESC"))
        return [dict(row._mapping) for row in result]

# 🔥 ADD BUSINESS
@app.post("/add-business")
def add_business(item: BusinessItem):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO business (title, price) VALUES (:title, :price)"),
            item.dict()
        )
    return {"status": "saved"}

# 🔥 GET BUSINESS
@app.get("/business")
def get_business():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM business ORDER BY id DESC"))
        return [dict(row._mapping) for row in result]
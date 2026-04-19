print("LOGIN SYSTEM LIVE")

from fastapi import FastAPI
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

# ---------- MODELS ----------
class User(BaseModel):
    email: str
    password: str

class ArtItem(BaseModel):
    title: str
    price: str
    image: str

# ---------- ROOT ----------
@app.get("/")
def root():
    return {"status": "login backend running"}

# ---------- REGISTER ----------
@app.post("/register")
def register(user: User):
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()

    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO users (email, password) VALUES (:email, :password)"),
            {"email": user.email, "password": hashed}
        )

    return {"status": "registered"}

# ---------- LOGIN ----------
@app.post("/login")
def login(user: User):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": user.email}
        ).fetchone()

    if not result:
        return {"error": "user not found"}

    stored = result._mapping["password"]

    if not bcrypt.checkpw(user.password.encode(), stored.encode()):
        return {"error": "wrong password"}

    return {"status": "success", "email": user.email}

# ---------- ART ----------
@app.post("/add-art")
def add_art(item: ArtItem):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO art (title, price, image) VALUES (:title, :price, :image)"),
            item.dict()
        )
    return {"status": "saved"}

@app.get("/art")
def get_art():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM art ORDER BY id DESC"))
        return [dict(row._mapping) for row in result]
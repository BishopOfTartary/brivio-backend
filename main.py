print("PROFILES + OWNERSHIP LIVE")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from pydantic import BaseModel
import bcrypt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "postgresql+psycopg://postgres.vzypnsvsmggemyjleuic:BrivioSecure2026!%23@aws-1-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require"
engine = create_engine(DATABASE_URL)

# ---------- MODELS ----------
class User(BaseModel):
    email: str
    password: str

class Post(BaseModel):
    user_email: str
    type: str
    title: str
    content_url: str
    price: str = ""

class Save(BaseModel):
    user_email: str
    post_id: int

# ---------- ROOT ----------
@app.get("/")
def root():
    return {"status": "profiles backend running"}

# ---------- AUTH ----------
@app.post("/register")
def register(user: User):
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()

    with engine.begin() as conn:
        conn.execute(
            text("insert into users (email, password) values (:email, :password)"),
            {"email": user.email, "password": hashed}
        )

    return {"status": "registered"}

@app.post("/login")
def login(user: User):
    with engine.connect() as conn:
        result = conn.execute(
            text("select * from users where email = :email"),
            {"email": user.email}
        ).fetchone()

    if not result:
        return {"error": "user not found"}

    stored = result._mapping["password"]

    if not bcrypt.checkpw(user.password.encode(), stored.encode()):
        return {"error": "wrong password"}

    return {"status": "success", "email": user.email}

# ---------- POSTS ----------
@app.post("/create-post")
def create_post(post: Post):
    with engine.begin() as conn:
        conn.execute(
            text("""
            insert into posts (user_email, type, title, content_url, price)
            values (:user_email, :type, :title, :content_url, :price)
            """),
            post.dict()
        )
    return {"status": "posted"}

@app.get("/posts")
def get_posts():
    with engine.connect() as conn:
        result = conn.execute(text("select * from posts order by id desc"))
        return [dict(row._mapping) for row in result]

# ---------- USER POSTS (PROFILE) ----------
@app.get("/user-posts/{email}")
def user_posts(email: str):
    with engine.connect() as conn:
        result = conn.execute(
            text("select * from posts where user_email = :email order by id desc"),
            {"email": email}
        )
        return [dict(row._mapping) for row in result]

# ---------- SAVES ----------
@app.post("/save")
def save_post(data: Save):
    with engine.begin() as conn:
        conn.execute(
            text("insert into saves (user_email, post_id) values (:user_email, :post_id)"),
            data.dict()
        )
    return {"status": "saved"}

@app.get("/saved/{email}")
def get_saved(email: str):
    with engine.connect() as conn:
        result = conn.execute(text("""
            select p.* from posts p
            join saves s on p.id = s.post_id
            where s.user_email = :email
        """), {"email": email})
        return [dict(row._mapping) for row in result]
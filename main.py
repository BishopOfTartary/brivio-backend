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

DATABASE_URL = "YOUR_SUPABASE_URL"
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

class Interaction(BaseModel):
    user_email: str
    post_id: int

class Comment(BaseModel):
    user_email: str
    post_id: int
    text: str

class Follow(BaseModel):
    follower: str
    following: str

# ---------- AUTH ----------
@app.post("/register")
def register(user: User):
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    with engine.begin() as conn:
        conn.execute(
            text("insert into users (email,password) values (:e,:p)"),
            {"e": user.email, "p": hashed}
        )
    return {"status": "registered"}

@app.post("/login")
def login(user: User):
    with engine.connect() as conn:
        u = conn.execute(
            text("select * from users where email=:e"),
            {"e": user.email}
        ).fetchone()

    if not u:
        return {"error": "not found"}

    if not bcrypt.checkpw(user.password.encode(), u.password.encode()):
        return {"error": "wrong password"}

    return {"status": "success", "email": user.email}

# ---------- POSTS ----------
@app.post("/post")
def post(p: Post):
    with engine.begin() as conn:
        conn.execute(text("""
            insert into posts (user_email,type,title,content_url)
            values (:u,:t,:ti,:c)
        """), {"u":p.user_email,"t":p.type,"ti":p.title,"c":p.content_url})
    return {"status":"posted"}

# 🔥 POSTS WITH LIKE COUNTS
@app.get("/posts")
def posts():
    with engine.connect() as conn:
        r = conn.execute(text("""
            select p.*, count(l.id) as likes
            from posts p
            left join likes l on p.id = l.post_id
            group by p.id
            order by p.id desc
        """))
        return [dict(x._mapping) for x in r]

# ---------- LIKE ----------
@app.post("/like")
def like(i: Interaction):
    with engine.begin() as conn:
        conn.execute(text("""
            insert into likes (user_email,post_id)
            values (:u,:p)
        """), {"u":i.user_email,"p":i.post_id})
    return {"status":"liked"}

# ---------- COMMENTS ----------
@app.post("/comment")
def comment(c: Comment):
    with engine.begin() as conn:
        conn.execute(text("""
            insert into comments (user_email,post_id,text)
            values (:u,:p,:t)
        """), {"u":c.user_email,"p":c.post_id,"t":c.text})
    return {"status":"commented"}

@app.get("/comments/{post_id}")
def get_comments(post_id:int):
    with engine.connect() as conn:
        r = conn.execute(text("""
            select * from comments where post_id=:p
        """), {"p":post_id})
        return [dict(x._mapping) for x in r]

# ---------- FOLLOW ----------
@app.post("/follow")
def follow(f: Follow):
    with engine.begin() as conn:
        conn.execute(text("""
            insert into follows (follower,following)
            values (:f,:g)
        """), {"f":f.follower,"g":f.following})
    return {"status":"followed"}
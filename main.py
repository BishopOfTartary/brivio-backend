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

class Interaction(BaseModel):
    user_email: str
    post_id: int

class Comment(BaseModel):
    user_email: str
    post_id: int
    text: str

# ---------- AUTH ----------
@app.post("/register")
def register(user: User):
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    with engine.begin() as conn:
        conn.execute(text("insert into users (email,password) values (:e,:p)"),
                     {"e":user.email,"p":hashed})
    return {"status":"registered"}

@app.post("/login")
def login(user: User):
    with engine.connect() as conn:
        u = conn.execute(text("select * from users where email=:e"),
                         {"e":user.email}).fetchone()

    if not u:
        return {"error":"not found"}

    if not bcrypt.checkpw(user.password.encode(), u.password.encode()):
        return {"error":"wrong password"}

    return {"status":"success","email":user.email}

# ---------- TRACK ACTIVITY ----------
@app.post("/activity")
def activity(data: dict):
    with engine.begin() as conn:
        conn.execute(text("""
            insert into user_activity (user_email, post_id, type)
            values (:u,:p,:t)
        """), data)
    return {"status":"tracked"}

# ---------- LIKE ----------
@app.post("/like")
def like(i: Interaction):
    with engine.begin() as conn:
        conn.execute(text("insert into likes (user_email,post_id) values (:u,:p)"),
                     {"u":i.user_email,"p":i.post_id})

        conn.execute(text("""
            insert into user_activity (user_email,post_id,type)
            values (:u,:p,'like')
        """), {"u":i.user_email,"p":i.post_id})

    return {"status":"liked"}

# ---------- COMMENT ----------
@app.post("/comment")
def comment(c: Comment):
    with engine.begin() as conn:
        conn.execute(text("""
            insert into comments (user_email,post_id,text)
            values (:u,:p,:t)
        """), {"u":c.user_email,"p":c.post_id,"t":c.text})

        conn.execute(text("""
            insert into user_activity (user_email,post_id,type)
            values (:u,:p,'comment')
        """), {"u":c.user_email,"p":c.post_id})

    return {"status":"commented"}

# ---------- PERSONALIZED FEED ----------
@app.get("/feed/{email}")
def personalized_feed(email:str):
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT 
                p.*,
                COUNT(DISTINCT l.id) AS likes,
                COUNT(DISTINCT c.id) AS comments,

                (
                    COUNT(DISTINCT l.id) * 2 +
                    COUNT(DISTINCT c.id) * 3 +

                    -- PERSONAL BOOST
                    (
                        SELECT COUNT(*) 
                        FROM user_activity ua 
                        WHERE ua.user_email = :email 
                        AND ua.post_id = p.id
                    ) * 5 +

                    -- TYPE PREFERENCE BOOST
                    (
                        SELECT COUNT(*) 
                        FROM user_activity ua 
                        JOIN posts px ON px.id = ua.post_id
                        WHERE ua.user_email = :email 
                        AND px.type = p.type
                    ) * 1.5

                ) AS score

            FROM posts p
            LEFT JOIN likes l ON p.id = l.post_id
            LEFT JOIN comments c ON p.id = c.post_id

            GROUP BY p.id
            ORDER BY score DESC
        """), {"email": email})

        return [dict(x._mapping) for x in r]
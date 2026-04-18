print("NEW VERSION DEPLOYED")

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from pydantic import BaseModel
import bcrypt
import stripe
import os
import json

# -------------------- STRIPE --------------------
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# -------------------- APP --------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- DATABASE --------------------
DATABASE_URL = "postgresql+psycopg://postgres.vzypnsvsmggemyjleuic:BrivioSecure2026!%23@aws-1-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require"
engine = create_engine(DATABASE_URL)

# -------------------- MODELS --------------------
class UserAuth(BaseModel):
    email: str
    password: str

class CheckoutItem(BaseModel):
    name: str
    price: int

# -------------------- HEALTH --------------------
@app.get("/")
def root():
    return {"status": "backend running"}

@app.get("/test")
def test():
    return {"message": "backend live"}

# -------------------- USERS --------------------
@app.post("/create-user")
def create_user(data: dict):
    email = data.get("email", "").strip()

    if not email:
        return {"error": "email required"}

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
        return [dict(row._mapping) for row in result]

# -------------------- AUTH --------------------
@app.post("/register")
def register(user: UserAuth):
    hashed = bcrypt.hashpw(
        user.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    with engine.begin() as conn:
        conn.execute(
            text("insert into users (email, password) values (:email, :password)"),
            {"email": user.email, "password": hashed}
        )

    return {"status": "registered"}

@app.post("/login")
def login(user: UserAuth):
    with engine.connect() as conn:
        existing = conn.execute(
            text("select * from users where email = :email"),
            {"email": user.email}
        ).fetchone()

    if not existing:
        return {"error": "user not found"}

    stored = existing._mapping.get("password")

    if not bcrypt.checkpw(user.password.encode(), stored.encode()):
        return {"error": "invalid password"}

    return {"status": "logged in"}

# -------------------- STRIPE CHECKOUT --------------------
@app.post("/create-checkout-session")
def create_checkout(item: CheckoutItem):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": item.name,
                    },
                    "unit_amount": item.price,
                },
                "quantity": 1,
            }
        ],
        success_url="http://localhost:5173/success",
        cancel_url="http://localhost:5173/cancel",
    )

    return {"url": session.url}

# -------------------- CHAT SOCKET --------------------
active_chat = []

@app.websocket("/ws/chat")
async def chat_socket(ws: WebSocket):
    await ws.accept()
    active_chat.append(ws)

    try:
        while True:
            msg = await ws.receive_text()
            for conn in active_chat:
                await conn.send_text(msg)
    except WebSocketDisconnect:
        active_chat.remove(ws)

# -------------------- RTC SOCKET --------------------
active_rtc = []

@app.websocket("/ws/rtc")
async def rtc_socket(ws: WebSocket):
    await ws.accept()
    active_rtc.append(ws)

    try:
        while True:
            data = await ws.receive_text()

            for conn in active_rtc:
                if conn != ws:
                    await conn.send_text(data)

    except WebSocketDisconnect:
        active_rtc.remove(ws)
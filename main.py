print("CORS FIX DEPLOYED")

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from pydantic import BaseModel
import bcrypt
import stripe
import os

# -------------------- STRIPE --------------------
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# -------------------- APP --------------------
app = FastAPI()

# ✅ FIXED CORS (THIS IS THE KEY CHANGE)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://brivio-frontend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- DATABASE --------------------
DATABASE_URL = "postgresql+psycopg://postgres.vzypnsvsmggemyjleuic:BrivioSecure2026!%23@aws-1-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require"
engine = create_engine(DATABASE_URL)

# -------------------- MODELS --------------------
class CheckoutItem(BaseModel):
    name: str
    price: int

# -------------------- ROOT --------------------
@app.get("/")
def root():
    return {"status": "backend running"}

# -------------------- STRIPE --------------------
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

# -------------------- CHAT --------------------
active_chat = []

@app.websocket("/ws/chat")
async def chat(ws: WebSocket):
    await ws.accept()
    active_chat.append(ws)

    try:
        while True:
            msg = await ws.receive_text()
            for c in active_chat:
                await c.send_text(msg)
    except WebSocketDisconnect:
        active_chat.remove(ws)
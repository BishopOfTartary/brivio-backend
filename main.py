print("FINAL REAL FIX")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app = FastAPI()

# 🔥 HARD CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class CheckoutItem(BaseModel):
    name: str
    price: int

@app.get("/")
def root():
    return {"status": "backend running"}

@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return {}

@app.post("/create-checkout-session")
def create_checkout(item: CheckoutItem):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": item.name},
                "unit_amount": item.price,
            },
            "quantity": 1,
        }],
        success_url="http://localhost:5173/success",
        cancel_url="http://localhost:5173/cancel",
    )

    return {"url": session.url}
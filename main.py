print("FINAL CORS FIX")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import stripe
import os

# -------------------- STRIPE --------------------
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# -------------------- APP --------------------
app = FastAPI()

# 🔥 FORCE CORS FIX (this is what fixes your issue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow everything for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- MODEL --------------------
class CheckoutItem(BaseModel):
    name: str
    price: int

# -------------------- ROOT --------------------
@app.get("/")
def root():
    return {"status": "backend running"}

# -------------------- CHECKOUT --------------------
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
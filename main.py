print("NEW VERSION DEPLOYED")

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from pydantic import BaseModel
import bcrypt
import json

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

class UserAuth(BaseModel):
    email: str
    password: str

@app.get("/health")
def health():
    return {"status": "online"}

# ---------- CHAT ----------
chat_connections = []

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    chat_connections.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            for conn in chat_connections:
                await conn.send_text(data)
    except WebSocketDisconnect:
        chat_connections.remove(websocket)

# ---------- WEBRTC SIGNALING ----------
rtc_connections = []

@app.websocket("/ws/rtc")
async def websocket_rtc(websocket: WebSocket):
    await websocket.accept()
    rtc_connections.append(websocket)

    try:
        while True:
            message = await websocket.receive_text()

            # broadcast signaling to others
            for conn in rtc_connections:
                if conn != websocket:
                    await conn.send_text(message)

    except WebSocketDisconnect:
        rtc_connections.remove(websocket)
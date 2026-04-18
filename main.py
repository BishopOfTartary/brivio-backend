print("BACKEND FINAL LOADED")

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- HEALTH ----------
@app.get("/")
def root():
    return {"status": "backend running"}

@app.get("/health")
def health():
    return {"status": "online"}

# ---------- CHAT ----------
chat_clients = []

@app.websocket("/ws/chat")
async def chat(ws: WebSocket):
    await ws.accept()
    chat_clients.append(ws)
    try:
        while True:
            msg = await ws.receive_text()
            for c in chat_clients:
                await c.send_text(msg)
    except WebSocketDisconnect:
        chat_clients.remove(ws)

# ---------- RTC SIGNALING ----------
rtc_clients = []

@app.websocket("/ws/rtc")
async def rtc(ws: WebSocket):
    await ws.accept()
    rtc_clients.append(ws)
    try:
        while True:
            msg = await ws.receive_text()
            for c in rtc_clients:
                if c != ws:
                    await c.send_text(msg)
    except WebSocketDisconnect:
        rtc_clients.remove(ws)
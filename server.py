print("SERVER ACTIVE")

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

@app.get("/")
def root():
    return {"status": "backend running"}

@app.get("/health")
def health():
    return {"status": "online"}

# --- RTC signaling ---
clients = []

@app.websocket("/ws/rtc")
async def rtc(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    try:
        while True:
            msg = await ws.receive_text()
            for c in clients:
                if c != ws:
                    await c.send_text(msg)
    except WebSocketDisconnect:
        clients.remove(ws)
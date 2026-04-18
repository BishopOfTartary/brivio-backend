from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.get("/")
def root():
    return {"status": "backend running"}

@app.get("/health")
def health():
    return {"status": "online"}

clients = []

@app.websocket("/ws/rtc")
async def rtc(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    try:
        while True:
            data = await ws.receive_text()
            for c in clients:
                if c != ws:
                    await c.send_text(data)
    finally:
        clients.remove(ws)
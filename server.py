from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

# ---- PROOF ROUTE ----
@app.get("/")
def root():
    return {"message": "SERVER.PY ACTIVE"}

@app.get("/health")
def health():
    return {"status": "online"}

# ---- USERS TEST (so frontend stops 404) ----
@app.get("/users")
def users():
    return [{"id": 1, "email": "test@brivio.com"}]

# ---- WEBSOCKET ----
connections = []

@app.websocket("/ws/chat")
async def chat(ws: WebSocket):
    await ws.accept()
    connections.append(ws)
    try:
        while True:
            msg = await ws.receive_text()
            for c in connections:
                await c.send_text(msg)
    except WebSocketDisconnect:
        connections.remove(ws)
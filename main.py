from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
import aioredis

app = FastAPI()
client_id_counter = 0

# Configuração do Redis
redis = None

@app.on_event("startup")
async def startup():
    global redis
    redis = await aioredis.create_redis_pool("redis://localhost")

@app.on_event("shutdown")
async def shutdown():
    redis.close()
    await redis.wait_closed()

# Rota para lidar com conexões WebSocket
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    await redis.sadd("active_connections", client_id)
    await redis.set(f"connection:{client_id}", websocket)
    
    try:
        while True:
            message = await websocket.receive_text()
            await broadcast(message, client_id)
    except WebSocketDisconnect:
        await redis.srem("active_connections", client_id)
        await redis.delete(f"connection:{client_id}")

# Função para enviar mensagens para todos os clientes conectados
async def broadcast(message: str, client_id: int):
    active_connections = await redis.smembers("active_connections")
    for connection_id in active_connections:
        connection_websocket = await redis.get(f"connection:{connection_id}")
        if connection_websocket:
            await connection_websocket.send_text(f"Client {client_id}: {message}")

# Rota para servir o arquivo HTML
@app.get("/")
async def get():
    with open("index.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)

# Configurar o servidor para servir arquivos estáticos (CSS e JavaScript)
app.mount("/static", StaticFiles(directory="static"), name="static")

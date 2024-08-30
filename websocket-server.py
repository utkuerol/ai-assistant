from fastapi import FastAPI, WebSocket
import uvicorn
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

TRANSCRIPTION_TOPIC = "transcription"
AI_MESSAGE_TOPIC = "ai-message"

connections = {
    TRANSCRIPTION_TOPIC: set(),
    AI_MESSAGE_TOPIC: set()
}

@app.websocket("/ws/{topic}")
async def websocket_endpoint(websocket: WebSocket, topic: str):
    if topic not in connections:
        raise ValueError("topic unknown")
    
    await websocket.accept()
    connections[topic].add(websocket)
    
    try:
        while True:
            message = await websocket.receive_text()
            print(f"topic: {topic}, message received: {message}")
            await broadcast_message(topic, message)
    except:
        connections[topic].remove(websocket)

async def broadcast_message(topic: str, message: str):
    for connection in connections[topic]:
        try:
            await connection.send_text(message)
        except:
            connections.remove(connection)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

import asyncio
from websockets import serve, broadcast
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

HOST = "0.0.0.0"
PORT = 8000

connections = {
    "transcription": set(),
    "ai-message": set()
}

async def handle(websocket, path):
    topic = path.lstrip("/ws/")
    if topic not in connections:
        print(f"Error: unknown topic {topic}")
        return
    
    connections[topic].add(websocket)
    print(f"New connection on topic: {topic}, total connections: {len(connections[topic])}")

    try:
        async for message in websocket:
            print(f"Received message on topic {topic}: {message}")
            try:
                broadcast(connections[topic], message)
            except Exception as e:
                print(f"Error during broadcast: {e}")
    except ConnectionClosedOK:
        print(f"Connection closed normally on topic: {topic}")
    except ConnectionClosedError as e:
        print(f"Connection closed with error on topic {topic}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        connections[topic].remove(websocket)
        print(f"Connection removed on topic: {topic}, total connections: {len(connections[topic])}")

async def main():
    try:
        async with serve(handle,
                        HOST, 
                        PORT,  
                        ping_interval=60,   # Time between pings (in seconds)
                        ping_timeout=60,    # Time to wait for a ping response before considering the connection closed
                        close_timeout=60    # Time to wait for the client to close the connection before closing it forcefully
                    ):
            print(f"WebSocket server started on ws://{HOST}:{PORT}")
            await asyncio.Future()
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

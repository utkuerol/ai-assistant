import sys
from config import *
from service.chat_service import ChatService
import asyncio

async def shutdown():
    print("Exiting chat. Goodbye!")
    try:
        await service.transcription_ws.close()
        await service.ai_message_ws.close()
    except Exception as e:
        print(e)
    sys.exit(0)
    
if __name__ == "__main__":
    try:
        service = ChatService(VOICE_ENABLED)
        asyncio.run(service.run())
    except KeyboardInterrupt:
        pass
    asyncio.run(shutdown())

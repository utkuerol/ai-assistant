import websockets
from config import *
from modules.stt import SpeechToText
from modules.tts import TextToSpeech
from modules.device_manager import DeviceManager
from modules.llm import LLM
import asyncio

STOP = "___stop___"
START = "___start___"

class ChatService:
    def __init__(self, voice_enabled=True):
        if not voice_enabled:
            raise ValueError("API supports only voice chat. Text chat not supported yet!")
        self.llm = LLM(
            base_url=LLM_API_ENDPOINT,
            api_key=LLM_API_KEY,
            model=LLM_MODEL,
            on_response_generated=self.handle_llm_response_text,
            verbose=False
        )
        self.llm_config = self.llm.get_config("dev")
        
        self.voice_enabled = voice_enabled
        self.message_queue = asyncio.Queue()
        
        if self.voice_enabled:
            self.device_manager = DeviceManager(voice_enabled=voice_enabled)
            self.stt: SpeechToText = SpeechToText()
            self.tts: TextToSpeech = TextToSpeech()
        
    async def enqueue_message(self, ws, message):
        await self.message_queue.put((ws, message))
        asyncio.create_task(self.send_message_from_queue())

    async def send_message_from_queue(self):
        while not self.message_queue.empty():
            ws, message = await self.message_queue.get()
            try:
                await ws.send(message)
            except Exception as e:
                print(f"Failed to send message: {e}")
                await self.message_queue.put((ws, message))  # Re-enqueue the message
                await self.connect_websockets()  # Attempt to reconnect WebSocket

    async def on_speech_detected(self, text) -> None:
        await self.enqueue_message(self.transcription_ws, text)

    async def on_recording_started(self) -> None:
        await self.enqueue_message(self.transcription_ws, START)

    async def on_recording_stopped(self) -> None:
        await self.enqueue_message(self.transcription_ws, STOP)

    async def handle_llm_response_text(self, text) -> None:
        await self.enqueue_message(self.ai_message_ws, text)

    async def handle_llm_response_audio(self, text_stream) -> None:
        if self.voice_enabled:
            await self.tts.speak(text_stream)
        
    async def connect_websockets(self):
        while True:
            try:
                self.transcription_ws = await websockets.connect("ws://localhost:8000/ws/transcription")
                self.ai_message_ws = await websockets.connect("ws://localhost:8000/ws/ai-message")
                print("WebSocket connections established.")
                break
            except (websockets.exceptions.ConnectionClosedError, 
                    websockets.exceptions.InvalidStatusCode, 
                    ConnectionRefusedError) as e:
                print(f"WebSocket connection failed: {e}")
                await asyncio.sleep(0.1)
        
    async def run(self) -> None:
        await self.connect_websockets()

        print("Chat started!")
        while True:
            user_input = ""
            async for input in self.stt.listen():
                if input == START:
                    await self.on_recording_started()
                else:
                    user_input += f" {input}"
                    await self.on_speech_detected(user_input)
            await self.on_recording_stopped()
            
            if user_input.strip():
                complete_response = ""
                await self.handle_llm_response_text(START)
                async for response in self.llm.get_response(user_input, self.llm_config):
                    complete_response += response
                    await self.handle_llm_response_text(response)
                await self.handle_llm_response_text(STOP)
                self.tts.speak(complete_response)

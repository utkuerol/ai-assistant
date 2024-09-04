import websockets
from config import *
from modules.stt import SpeechToText
from modules.tts import TextToSpeech
from modules.device_manager import DeviceManager
from modules.llm import LLM
import asyncio

STOP = "___stop___"
START = "___start___"
EXIT_COMMAND = "bye"

class ChatService:
    def __init__(self, voice_enabled=True):
        if not voice_enabled:
            raise ValueError("Text only chat not supported yet!")
        self.llm = LLM(
            base_url=LLM_API_ENDPOINT,
            api_key=LLM_API_KEY,
            model=LLM_MODEL,
            verbose=False
        )
        self.llm_config = self.llm.get_config("dev")
        
        self.voice_enabled = voice_enabled
        self.speak_lock = asyncio.Lock()
        
        if self.voice_enabled:
            self.device_manager = DeviceManager(voice_enabled=voice_enabled)
            self.stt: SpeechToText = SpeechToText()
            self.tts: TextToSpeech = TextToSpeech()
        

    def handle_llm_response_audio(self, text_stream) -> None:
        if self.voice_enabled:
            self.tts.speak(text_stream)
        
    async def run(self) -> None:
        print("Chat connected!")
        while True:
            try:
                user_input = ""
                async with self.speak_lock, websockets.connect("ws://localhost:8000/ws/transcription") as ws:
                    async for input in self.stt.listen():
                        if input == START:
                            await ws.send(START)
                        else:
                            user_input += f" {input}"
                            await ws.send(user_input)
                    await ws.send(STOP)
                    user_input = user_input.strip()

                if EXIT_COMMAND in user_input:
                    break
                                            
                if user_input:
                    complete_response = ""
                    async with self.speak_lock, websockets.connect("ws://localhost:8000/ws/ai-message") as ws:
                        await ws.send(START)
                        async for response in self.llm.get_response(user_input, self.llm_config):
                            complete_response += response
                            await ws.send(response)
                        await ws.send(STOP)
                        self.handle_llm_response_audio(complete_response)
                                        
            except Exception as e:
                print(f"Unexpected error: {e}")
                continue
    
        print("Exit command received, exiting chat...")

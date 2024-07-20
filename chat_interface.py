from config import *
from abc import ABC, abstractmethod
from modules.stt import SpeechToText
from modules.tts import TextToSpeech
from modules.device_manager import DeviceManager
from modules.llm import LLM

class ChatInterface(ABC):
    @abstractmethod
    def __init__(self, voice_enabled=True) -> None:
        self.llm = LLM(
            base_url=LLM_API_ENDPOINT,
            api_key=LLM_API_KEY,
            model=LLM_MODEL,
            on_response_generated=self.handle_llm_response_text,
            verbose=False
        )
        self.llm_config = self.llm.get_config("dev")
        
        self.voice_enabled = voice_enabled
        self.detected_speech = ""
        
        if self.voice_enabled:
            self.device_manager = DeviceManager(voice_enabled=voice_enabled)
            self.stt: SpeechToText = SpeechToText(input_device_index=self.device_manager.mic_device, on_speech_detected=self.on_speech_detected)
            self.tts: TextToSpeech = TextToSpeech()
    
    @abstractmethod
    def on_speech_detected(self, text) -> None:
        pass
    
    @abstractmethod
    def handle_llm_response_text(self, text) -> None:
        pass
    
    @abstractmethod
    def handle_llm_response_audio(self, text_stream) -> None:
        pass
    
    @abstractmethod
    def run(self) -> None:
        pass
    
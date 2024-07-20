from chat_interface import ChatInterface

class ChatCLI(ChatInterface):
    def __init__(self, voice_enabled=True) -> None:
        super().__init__(voice_enabled)
    
    def on_speech_detected(self, text) -> None:
        text = f"You: {text.strip()}"
        diff = len(self.detected_speech) - len(text)
        if diff > 0:
            text += " " * diff
        print(text, end='\r', flush=True)
        self.detected_speech = text

    def handle_llm_response_text(self, text):
        print(text, end="", flush=True)
        
    def handle_llm_response_audio(self, text_stream) -> None:
        if self.voice_enabled:
            self.tts.speak(text_stream)
        
    def run(self) -> None:
        if self.voice_enabled:
            print("Voice chat started with the AI assistant (say 'goodbye' to stop):")
            while True:
                user_input = self.stt.listen()
                if 'bye' in user_input.lower():
                    break
                if user_input.strip():
                    print("\nAI: ", end='', flush=True)
                    response_stream = self.llm.get_response(user_input, self.llm_config)
                    self.handle_llm_response_audio(response_stream)
        else:
            print("Text chat started with the AI assistant (type 'bye' to stop):")
            while True:
                user_input = input("\nYou: ")
                if 'bye' in user_input.lower():
                    break
                if user_input.strip():
                    print("\nAI: ", end='', flush=True)
                    # cast to list in order to wait until generator is exhausted
                    list(self.llm.get_response(user_input, self.llm_config)) 
            
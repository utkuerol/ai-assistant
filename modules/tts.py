import logging
from RealtimeTTS import TextToAudioStream, CoquiEngine

class TextToSpeech:
    def __init__(self, speed=1.2, language="en", voice="Abrahan Mack"):
        self.text_to_speech_stream = self._init_stream(speed, language, voice)
    
    def speak(self, response_stream):
        self.text_to_speech_stream.feed(response_stream)
        self.text_to_speech_stream.play()
    
    def _init_stream(self, speed=1.2, language="en", voice="Abrahan Mack"):
        print("Initializing text-to-speech...")
        text_to_speech_engine = CoquiEngine(
            speed=speed,
            language=language,
            voice=voice,
            device="cuda",
            level=logging.ERROR
        )
        stream = TextToAudioStream(
            engine=text_to_speech_engine
        )
        print("text-to-speech is ready!")
        return stream
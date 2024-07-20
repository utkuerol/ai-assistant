from RealtimeSTT import AudioToTextRecorder
from pathlib import Path
from modules.utils import play_audio
import logging

class SpeechToText:
    def __init__(self, model="medium", language="en", device="cuda", input_device_index=0, on_speech_detected=None):
        self._on_speech_detected = on_speech_detected
        self._set_sounds()
        self.recorder = self._init_recorder(model, language, device, input_device_index)
    
    def listen(self):
        play_audio(self.record_start_sound)
        user_input = self.recorder.text()
        play_audio(file_path=self.record_stop_sound)
        return user_input.strip()
        
    def _init_recorder(self, model="medium", language="en", device="cuda", input_device_index=0):
        print("Initializing speech-to-text...")
        recorder = AudioToTextRecorder(
            spinner=False, 
            model=model, 
            language=language, 
            input_device_index=input_device_index, 
            device=device,
            enable_realtime_transcription=True,
            on_realtime_transcription_update=self._on_speech_detected,
            level=logging.ERROR
        )
        print("Speech-to-text is ready!")
        return recorder
    
    def _set_sounds(self):
        script_path = Path(__file__).resolve()
        base_path = script_path.parents[1]
        self.record_start_sound = base_path / "resources/active.wav"
        self.record_stop_sound = base_path / "resources/inactive.wav"
    
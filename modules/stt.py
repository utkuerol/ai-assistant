import numpy as np
import speech_recognition as sr
from faster_whisper import WhisperModel
from queue import Queue
import asyncio
from datetime import datetime
import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

class SpeechToText:
    def __init__(self, model_size="medium", language="en", device="cuda", input_device_index=0):
        print("Initializing speech-to-text")
        self.model_size = model_size
        self.language = language
        self.device = device
        self.input_device_index = input_device_index
        
        self.model = WhisperModel(self.model_size, device=self.device, compute_type="int8_float16")
        
        self.data_queue = Queue()
        self.mic_lock = asyncio.Lock()
        print("speech-to-text is ready")
                
    def _record_callback(self, _, audio: sr.AudioData) -> None:
        data = audio.get_raw_data()
        self.data_queue.put(data)

    async def listen(self):
        async with self.mic_lock: 
            stop_listening = None
            
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 1500
            recognizer.dynamic_energy_threshold = False
            microphone = sr.Microphone(device_index=self.input_device_index, sample_rate=16000)

            try:
                with microphone as source:
                    recognizer.adjust_for_ambient_noise(source)

                stop_listening = recognizer.listen_in_background(
                    microphone, self._record_callback, phrase_time_limit=2
                )

                speak_start = None
                while True:
                    if not self.data_queue.empty():
                        if speak_start is None:
                            yield "___start___"
                        speak_start = datetime.now()
                        audio_data = b''.join(list(self.data_queue.queue))
                        self.data_queue.queue.clear()

                        # Convert to the format faster-whisper expects
                        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                        segments, _ = self.model.transcribe(audio_np, language=self.language, beam_size=5)
                        for segment in segments:
                            if segment.text.strip() != "":
                                yield segment.text
                    else:
                        if speak_start is not None and (datetime.now() - speak_start).total_seconds() >= 3:
                            break
                        await asyncio.sleep(0.1)
            finally:
                if stop_listening is not None:
                    stop_listening(wait_for_stop=False)

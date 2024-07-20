from chat_interface import ChatInterface
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from threading import Thread

class ChatGUI(ChatInterface):
    def __init__(self, voice_enabled=True):
        ChatInterface.__init__(self, voice_enabled)
        self.init_ui()

    def init_ui(self):
        self.app = QApplication([])
        self.window = QWidget()
        self.layout = QVBoxLayout()
        self.text_area = QTextEdit(self.window)
        self.text_area.setReadOnly(True)
        self.layout.addWidget(self.text_area)
        
        self.window.setLayout(self.layout)
        self.window.setWindowTitle("Voice Assistant")
        self.window.setGeometry(100, 100, 600, 400)
        self.window.show()
                
        self.emit_new_message = ThreadUtil().run_in_main_thread(self._new_message)
        self.emit_continue_message = ThreadUtil().run_in_main_thread(self._continue_message)
        self.emit_overwrite_existing_message = ThreadUtil().run_in_main_thread(self._overwrite_existing_message)        
    
    def on_speech_detected(self, text) -> None:
        text = f"\nYou: {text.strip()}"
        if self.detected_speech:
            self.emit_overwrite_existing_message(text)
        else:
            self.emit_new_message(text)
        self.detected_speech = text

    def handle_llm_response_text(self, text) -> None:
        self.emit_continue_message(text)
        
    def handle_llm_response_audio(self, text_stream) -> None:
        if self.voice_enabled:
            self.tts.speak(text_stream)

    def run(self) -> None:
        thread = Thread(target=self._dialog, daemon=True)
        thread.start()
        self.app.exec()
            
    def _dialog(self):
        while True:
            user_input = self.stt.listen() if self.voice_enabled else input("\nYou: ")
            if 'bye' in user_input.lower():
                break
            if user_input:
                self.emit_new_message("\nAI: ")
                # reset detected speech (required for handling overwriting of text until stt is stabilized)
                self.detected_speech = "" 
                response_stream = self.llm.get_response(user_input, self.llm_config)
                if self.voice_enabled:
                    self.handle_llm_response_audio(response_stream)

    def _new_message(self, text):
        self.text_area.append(text)
        
    def _continue_message(self, text):
        self.text_area.moveCursor(QTextCursor.MoveOperation.End)
        self.text_area.insertPlainText(text)
        self.text_area.moveCursor(QTextCursor.MoveOperation.End)
        
    def _overwrite_existing_message(self, text):
        self.text_area.undo()
        self.text_area.append(text)

class ThreadUtil(QObject):
    _on_execute = pyqtSignal(object, tuple, dict)

    def __init__(self):
        super(QObject, self).__init__()
        self._on_execute.connect(self._execute_in_thread)

    def execute(self, f, args, kwargs):
        self._on_execute.emit(f, args, kwargs)

    def _execute_in_thread(self, f, args, kwargs):
        f(*args, **kwargs)

    def run_in_main_thread(self, f):
        def result(*args, **kwargs):
            self.execute(f, args, kwargs)
        return result
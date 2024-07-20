import simpleaudio as audioplayer

def play_audio(file_path, play_async=False):
    try:
        wave_obj = audioplayer.WaveObject.from_wave_file(str(file_path))
        play_obj = wave_obj.play()
        if not play_async:
            play_obj.wait_done()
            
    except Exception as e:
        print(f"An error occurred while playing the sound: {e}")
import pyaudio

class DeviceManager:
    def __init__(self, voice_enabled=True):
        if voice_enabled:
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            numdevices = info.get('deviceCount')

            for i in range(0, numdevices):
                if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
            
            selection = input("\nChoose your mic device index: ")
            selecting = True
            index = 0
            while selecting:
                if not selection.isdigit():
                    print("Invalid index (not a digit)!")
                    selection = input("\nChoose your mic device index: ")
                    continue
                index = int(selection)
                if index not in range(0, numdevices):
                    print("Invalid index (not an existing device)!")
                    selection = input("\nChoose your mic device index: ")
                    continue
                print("Mic is successfully selected!")
                selecting = False
            
            self.mic_device = index

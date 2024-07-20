import sys
from interfaces.chat_cli import ChatCLI
from interfaces.chat_gui import ChatGUI
from enum import Enum

class InterfaceType(str, Enum):
    GUI = "gui"
    CLI = "cli"

class Chat:
    def __init__(self, interface_type: InterfaceType = InterfaceType.GUI, voice_enabled=True):
        self.running = True
        self.voice_enabled = voice_enabled
        
        if interface_type is InterfaceType.GUI:
            self.interface = ChatGUI(self.voice_enabled)
        else:
            self.interface = ChatCLI(self.voice_enabled)
            
    def run(self):
        self.interface.run()
        if hasattr(self, 'app'):
            sys.exit(self.app.exec_())

def shutdown():
    print("Exiting chat. Goodbye!")
    sys.exit(0)
    
def extract_args(args: list[str]) -> tuple[InterfaceType, bool]:
    interface_type: InterfaceType = None
    voice_enabled: bool = None
    
    if len(args) != 3:
            print("you need to provide arguments:\n--interface=<gui/cli>\n--voice=<true/false>")
            sys.exit(1)
        
    for arg in args[1:]:
        arg_splitted = arg.split("=")
        if len(arg_splitted) != 2:
            print(f"argument {arg} unknown")
            sys.exit(1)
        key = arg_splitted[0]
        val = arg_splitted[1]
        if key == "--interface":
            try:
                interface_type = InterfaceType(val)
            except ValueError:
                print(f"invalid value for argument {arg}: {val}")
                sys.exit(1)
                
        if key == "--voice":
            if val.lower() == "true":
                voice_enabled = True
            elif val.lower() == "false":
                voice_enabled = False
            else:
                print(f"invalid value for argument {arg}: {val}")
                sys.exit(1)
    
    return interface_type, voice_enabled
    
if __name__ == "__main__":
    try:
        interface_type, voice_enabled = extract_args(sys.argv)
        chat = Chat(interface_type, voice_enabled)
        chat.run()
    except KeyboardInterrupt:
        pass
    shutdown()

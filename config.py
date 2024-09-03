import os
import sys
from dotenv import dotenv_values

config = {
    **dotenv_values(".env"), 
    **dotenv_values(".env.secret"),  # load sensitive variables
    **os.environ,  # override loaded values with environment variables
}

VOICE_ENABLED: bool = config.get("VOICE_ENABLED", True)
LLM_API_ENDPOINT: str = config.get("LLM_API_ENDPOINT", None)
LLM_API_KEY: str = config.get("LLM_API_KEY", "no-key")
LLM_MODEL: str = config.get("LLM_MODEL", None)

if None in [LLM_API_ENDPOINT, LLM_MODEL]:
    print("missing env variables, exiting...")
    sys.exit(1)
    
print(f"using LLM server: {LLM_API_ENDPOINT}")

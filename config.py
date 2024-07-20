import os
import sys
from dotenv import dotenv_values

config = {
    **dotenv_values(".env"), 
    **dotenv_values(".env.secret"),  # load sensitive variables
    **os.environ,  # override loaded values with environment variables
}

LLM_API_ENDPOINT = config.get("LLM_API_ENDPOINT", None)
LLM_API_KEY = config.get("LLM_API_KEY", "no-key")
LLM_MODEL = config.get("LLM_MODEL", None)

if None in [LLM_API_ENDPOINT, LLM_MODEL]:
    print("missing env variables, exiting...")
    sys.exit(1)

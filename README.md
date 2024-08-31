# AI Assistant

PoC for realtime voice-to-voice AI chat using opensource AI models 

## How to run

- Setup virtual env:
  -  ```conda create -n ai-assistant python=3.10```
  - ```conda activate ai-assistant```
  
- Install requirements
  - ```pip install -r requirements.txt```
  - ```pip install -r requirements-torch-cuda.txt```

- Start backend
  - ```python websocket-server.py``` 
  - ```python main.py``` 

- Start web ui
  - inside ui folder: ```npm run dev```
    
- Go to ```localhost:3000```


## Roadmap

- Dockerize STT and TTS or ideally find ready to use docker images
- RAG support
- Persistence
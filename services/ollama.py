import requests
import json
from config import OLLAMA_BASE_URL

import subprocess
import time

def get_installed_models():
    """Fetch installed models from local Ollama instance."""
    def fetch():
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
            response.raise_for_status()
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        except requests.exceptions.RequestException:
            return None

    models = fetch()
    if models is not None:
        return models
        
    # If connection fails, attempt to auto-start Ollama silently on Windows
    try:
        # 0x08000000 is CREATE_NO_WINDOW in Windows, prevents cmd popup
        subprocess.Popen(["ollama", "serve"], creationflags=0x08000000)
        time.sleep(2) # Give it 2 seconds to boot up
        
        # Try fetching again
        models = fetch()
        if models is not None:
            return models
    except Exception:
        pass
        
    return []

def stream_chat(model, messages, temperature=0.7, max_tokens=2048):
    """Stream chat responses from local Ollama instance."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    
    try:
        with requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if "message" in chunk and "content" in chunk["message"]:
                        yield chunk["message"]["content"]
    except requests.exceptions.RequestException as e:
        yield f"\n\n**Error connecting to Ollama:** {str(e)}\n\nPlease ensure Ollama is running (`ollama serve`) and the model '{model}' is installed."

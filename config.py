import os

# Application Settings
APP_TITLE = "Local AI ChatBot"
APP_ICON = "🤖"

# Ollama Settings
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3"

# Local Storage
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHATS_DIR = os.path.join(BASE_DIR, "chats")

# Create chats dir if it doesn't exist
os.makedirs(CHATS_DIR, exist_ok=True)

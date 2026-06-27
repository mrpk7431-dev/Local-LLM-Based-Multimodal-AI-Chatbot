import os
import json
import uuid
from datetime import datetime
from config import CHATS_DIR

def get_all_chats():
    """Returns a list of all chat sessions sorted by last modified."""
    chats = []
    for filename in os.listdir(CHATS_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(CHATS_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    chats.append({
                        "id": data.get("id"),
                        "title": data.get("title", "New Chat"),
                        "updated_at": os.path.getmtime(filepath),
                        "filepath": filepath
                    })
            except (json.JSONDecodeError, IOError):
                continue
    
    return sorted(chats, key=lambda x: x["updated_at"], reverse=True)

def load_chat(chat_id):
    """Loads a specific chat session by ID."""
    filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    return None

def save_chat(chat_data):
    """Saves a chat session to disk."""
    if not chat_data.get("id"):
        chat_data["id"] = str(uuid.uuid4())
        
    if not chat_data.get("title") and chat_data.get("messages"):
        # Auto-generate title from first user message
        first_msg = next((m["content"] for m in chat_data.get("messages", []) if m["role"] == "user"), "New Chat")
        chat_data["title"] = first_msg[:30] + "..." if len(first_msg) > 30 else first_msg
        
    filepath = os.path.join(CHATS_DIR, f"{chat_data['id']}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(chat_data, f, indent=4)
        
    return chat_data

def delete_chat(chat_id):
    """Deletes a chat session from disk."""
    filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

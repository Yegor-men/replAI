import json

def load_json_chat(
    json_chat_filename: str,
    ai_class_instance,
):
    try:
        with open(json_chat_filename, "r") as f:
            chat = json.load(f)
            
            # If already in OpenAI format, return as is
            if all(isinstance(msg, dict) and "role" in msg for msg in chat):
                return chat
                
            # Otherwise convert from old format
            return [
                {
                    "role": "assistant" if msg["sender"] == ai_class_instance.name else "user",
                    "content": f'[{msg["timestamp"]}] - {msg["sender"]}: {msg["message"]}'
                }
                for msg in chat
            ]
    except (json.JSONDecodeError, FileNotFoundError):
        return []
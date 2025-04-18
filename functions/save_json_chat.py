import json

def save_json_chat(
    loaded_json_chat, 
    json_chat_filename: str,
    ai_class_instance=None
):
    formatted_chat = []
    for msg in loaded_json_chat:
        if "role" in msg:  # Already in OpenAI format
            formatted_chat.append(msg)
        else:  # Old format that needs conversion
            role = "assistant" if ai_class_instance and msg["sender"] == ai_class_instance.name else "user"
            formatted_chat.append({
                "role": role,
                "content": f'[{msg["timestamp"]}] - {msg["sender"]}: {msg["message"]}'
            })
    
    with open(json_chat_filename, "w") as f:
        json.dump(formatted_chat, f, indent=4)
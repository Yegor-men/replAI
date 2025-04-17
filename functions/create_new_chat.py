import os
import json


def create_new_chat(filename):
    os.makedirs("chats", exist_ok=True)

    filepath = f"chats/{filename}.json"
    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            json.dump([], f, indent=4)
    return filepath

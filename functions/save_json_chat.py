import json


def save_json_chat(
    loaded_json_chat,
    json_chat_filename: str,
):
    with open(json_chat_filename, "w") as f:
        json.dump(loaded_json_chat, f, indent=4)

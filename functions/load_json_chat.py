import json


def load_json_chat(
    json_chat_filename: str,
):
    try:
        with open(json_chat_filename, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

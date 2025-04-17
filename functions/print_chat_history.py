import json


def print_chat_history(
    json_chat_filepath,
):
    try:
        with open(json_chat_filepath, "r") as f:
            chat_history = json.load(f)

        print("\n======== Chat History ========")
        for message in chat_history:
            sender = message["sender"]
            timestamp = message["timestamp"]
            content = message["message"].replace("~", "\n")

            print(f"\n[{timestamp}] - {sender}:")
            print(f"{content}")
        # print("\n=================")
    except FileNotFoundError:
        print(f"No chat history found")

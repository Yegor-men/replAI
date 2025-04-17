from functions.save_json_chat import save_json_chat
from functions.load_json_chat import load_json_chat
import datetime


def user_send_message(
    json_chat_filepath: str,
    user_class_instance,
    message: str,
):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%d/%m/%Y, %H:%M")

    chat_history = load_json_chat(json_chat_filepath)
    chat_history.append(
        {"sender": user_class_instance.name, "timestamp": timestamp, "message": message}
    )
    save_json_chat(
        loaded_json_chat=chat_history,
        json_chat_filename=json_chat_filepath,
    )

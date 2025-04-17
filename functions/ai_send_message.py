from functions.load_json_chat import load_json_chat
from functions.format_chat import format_chat
from functions.save_json_chat import save_json_chat
import ollama
import datetime


def ai_send_message(
    json_chat_filepath,
    system_prompt_function,
    model_name,
    ai_class_instance,
    user_class_instance,
):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%d/%m/%Y, %H:%M")

    chat_history = load_json_chat(json_chat_filepath)

    formatted_messages = format_chat(
        loaded_json_chat=chat_history,
        ai_class_instance=ai_class_instance,
    )
    formatted_messages += [
        {
            "role": "system",
            "content": system_prompt_function(
                ai_class_instance, user_class_instance, timestamp
            ),
        }
    ]

    response = ""
    stream = ollama.chat(
        model=model_name,
        messages=formatted_messages,
        stream=True,
    )

    for chunk in stream:
        content = chunk["message"]["content"]
        content = content.replace("~", "\n")
        print(content, end="", flush=True)
        response += chunk["message"]["content"]

    chat_history.append(
        {"sender": ai_class_instance.name, "timestamp": timestamp, "message": response}
    )

    save_json_chat(
        loaded_json_chat=chat_history,
        json_chat_filename=json_chat_filepath,
    )

from system_prompts.test_sys_prompt import sys_prompt
from personalities.personality_class import Personality
import ollama
import datetime
import json


def load_chat_history():
    try:
        with open("chats/test.json", "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_chat_history(chat_history):
    with open("chats/test.json", "w") as f:
        json.dump(chat_history, f, indent=4)


modelname = "gemma3:12b"


def ai_send_message(
    chat_format_function,
    model_name,
    ai_class_instance,
    user_class_instance,
):
    # Load chat history from JSON
    chat_history = load_chat_history()

    # Format messages for the model
    formatted_messages = chat_format_function(chat_history)
    formatted_messages += [
        {
            "role": "system",
            "content": sys_prompt(ai_class_instance, user_class_instance),
        }
    ]

    # Get response from model
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

    # Create timestamp
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%d/%m/%Y, %H:%M")

    # Add response to chat history
    chat_history.append(
        {"sender": ai_class_instance.name, "timestamp": timestamp, "message": response}
    )

    save_chat_history(chat_history)


joe_biden = Personality(name="joe biden", description="mistah rizzident")
ai_assist = Personality(name="replAI", description="super smart AI assistant")


def format_chat_history(chat_history):
    formatted_messages = []
    for message in chat_history:
        if message["sender"] == ai_assist.name:
            role = "assistant"
        else:
            role = "user"
        formatted_messages.append(
            {
                "role": role,
                "content": f'{message["sender"]}-{message["timestamp"]}: {message["message"]}',
            }
        )
    return formatted_messages


# ai_send_message(
#     chat_format_function=format_chat_history,
#     model_name=modelname,
#     ai_class_instance=ai_assist,
#     user_class_instance=joe_biden,
# )


def user_send_message(
    user_class_instance,
    message: str,
):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%d/%m/%Y, %H:%M")

    chat_history = load_chat_history()
    chat_history.append(
        {"sender": user_class_instance.name, "timestamp": timestamp, "message": message}
    )
    save_chat_history(chat_history)


while True:
    message = input()
    user_send_message(joe_biden, message)

    ai_send_message(
        chat_format_function=format_chat_history,
        model_name=modelname,
        ai_class_instance=ai_assist,
        user_class_instance=joe_biden,
    )

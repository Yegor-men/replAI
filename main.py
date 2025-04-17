from functions.create_new_chat import create_new_chat
from functions.load_json_chat import load_json_chat
from functions.save_json_chat import save_json_chat
from functions.ai_send_message import ai_send_message
from functions.user_send_message import user_send_message

from system_prompts.system_prompt import system_prompt

from characters.character import Character
from characters.character_cards import joe
from characters.character_cards import replAI

import datetime

should_create_new_chat = True
chat_name = "test_5"

if should_create_new_chat:
    create_new_chat(chat_name)


ai_class_instance = Character(character_card=replAI)

user_class_instance = Character(character_card=joe)


modelname = "gemma3:12b"
filepath = f"chats/{chat_name}.json"

from functions.print_chat_history import print_chat_history

print_chat_history(filepath)

while True:
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%d/%m/%Y, %H:%M")
    print(f"\n\n[{timestamp}] - {user_class_instance.name}:")
    user_message = input()
    if user_message == "/q":
        break
    user_send_message(
        json_chat_filepath=filepath,
        user_class_instance=user_class_instance,
        message=user_message,
    )
    
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%d/%m/%Y, %H:%M")
    print(f"\n\n[{timestamp}] - {ai_class_instance.name}:\n")
    
    ai_send_message(
        json_chat_filepath=filepath,
        system_prompt_function=system_prompt,
        model_name=modelname,
        ai_class_instance=ai_class_instance,
        user_class_instance=user_class_instance,
    )

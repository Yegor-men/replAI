def format_chat(
    loaded_json_chat,
    ai_class_instance,
):
    formatted_messages = []
    for message in loaded_json_chat[-1000:]:
        if message["sender"] == ai_class_instance.name:
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

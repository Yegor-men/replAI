def format_chat(loaded_json_chat, ai_class_instance):
    """Format chat history for model consumption"""
    # Take last 1000 messages
    return loaded_json_chat[-1000:]
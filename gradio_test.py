import gradio as gr
import glob
import os
from functions.create_new_chat import create_new_chat
import ollama

import datetime
from functions.ai_send_message import ai_send_message
from functions.load_json_chat import load_json_chat
from system_prompts.system_prompt import system_prompt
from characters.character import Character


def get_available_models():
    """Get list of installed Ollama models"""
    try:
        response = ollama.list()
        # print("Debug - Ollama response:", response)

        # The response directly contains a 'models' list
        if hasattr(response, "models") and isinstance(response.models, list):
            model_names = []
            for model in response.models:
                # Each model is now an object with a 'model' attribute
                if hasattr(model, "model"):
                    model_names.append(model.model)
            return model_names if model_names else ["no models found"]
        else:
            print("Debug - Unexpected response structure:", response)
            return ["no models found"]

    except Exception as e:
        print(f"Error getting models: {str(e)}")
        print(f"Error type: {type(e)}")
        return ["error loading models"]


def update_model_selection(model_name):
    """Update the global model name"""
    global current_model
    current_model = model_name
    return gr.update(value=f"Current model: {model_name}")


def get_available_chats():
    """Get list of existing chat files"""
    # Ensure chats directory exists
    os.makedirs("chats", exist_ok=True)
    chat_files = glob.glob("chats/*.json")
    return [os.path.splitext(os.path.basename(f))[0] for f in chat_files]


from gradio.components import ChatMessage


def load_chat_history(chat_name, ai_char_name=None):
    """Load chat history and format for Gradio chatbot"""
    if not chat_name:
        return []

    # Create a default AI instance if none specified
    if ai_char_name:
        try:
            ai_module = __import__(
                f"characters.character_cards.{ai_char_name}", fromlist=[""]
            )
            ai_class_instance = Character(character_card=ai_module)
        except ImportError:
            print(f"Warning: Could not load AI character {ai_char_name}")
            return []
    else:
        return []

    chat = load_json_chat(f"chats/{chat_name}.json", ai_class_instance)
    if not chat:
        return []

    # Format messages for Gradio chatbot
    formatted_chat = []
    for msg in chat:
        content = msg.get("content", "")
        role = msg.get("role", "")

        # Create ChatMessage objects
        if role == "user":
            formatted_chat.append(ChatMessage(content=content, role="user"))
        else:
            formatted_chat.append(ChatMessage(content=content, role="assistant"))

    return formatted_chat


def send_message(message, history, chat_name, user_character, ai_character):
    """Handle sending messages and getting AI response"""
    if not message or not chat_name or not user_character or not ai_character:
        return "", history

    try:
        user_module = __import__(
            f"characters.character_cards.{user_character}", fromlist=[""]
        )
        ai_module = __import__(
            f"characters.character_cards.{ai_character}", fromlist=[""]
        )

        user_class_instance = Character(character_card=user_module)
        ai_class_instance = Character(character_card=ai_module)

        if not user_class_instance.name or not ai_class_instance.name:
            raise ValueError("Character instances not properly initialized")

    except (ImportError, ValueError) as e:
        error_msg = f"Error with character modules: {e}"
        print(error_msg)
        history.append(ChatMessage(content=error_msg, role="assistant"))
        return "", history

    current_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M")

    # Handle user messages
    user_messages = message.split("~")
    for submsg in user_messages:
        if submsg.strip():
            from functions.user_send_message import user_send_message

            user_send_message(
                json_chat_filepath=f"chats/{chat_name}.json",
                user_class_instance=user_class_instance,
                message=submsg.strip(),
            )

            formatted_msg = (
                f"[{current_time}] - {user_class_instance.name}: {submsg.strip()}"
            )
            history.append(ChatMessage(content=formatted_msg, role="user"))

    try:
        # Get AI response
        ai_response = ai_send_message(
            json_chat_filepath=f"chats/{chat_name}.json",
            system_prompt_function=system_prompt,
            model_name=current_model,
            ai_class_instance=ai_class_instance,
            user_class_instance=user_class_instance,
        )

        if ai_response:
            ai_messages = ai_response.split("~")
            for submsg in ai_messages:
                if submsg.strip():
                    formatted_msg = (
                        f"[{current_time}] - {ai_class_instance.name}: {submsg.strip()}"
                    )
                    history.append(ChatMessage(content=formatted_msg, role="assistant"))
        else:
            history.append(
                ChatMessage(content="No response received from AI", role="assistant")
            )

    except Exception as e:
        error_msg = f"Error processing AI response: {e}"
        print(error_msg)
        history.append(ChatMessage(content=error_msg, role="assistant"))

    return "", history


# Update the chat selection handler
def on_chat_select(chat_name, ai_char_name):
    """Handle chat selection"""
    if chat_name:
        history = load_chat_history(chat_name, ai_char_name)
        return gr.update(value=chat_name), gr.update(value=history)
    return gr.update(), gr.update(value=[])


def get_available_characters():
    """Get list of character cards"""
    char_files = glob.glob("characters/character_cards/*.py")
    return [
        os.path.splitext(os.path.basename(f))[0]
        for f in char_files
        if not f.endswith("__init__.py")
    ]


def create_new_chat_and_refresh(chat_name):
    """Create new chat and refresh the chat list"""
    if not chat_name.strip():
        return gr.update(choices=[]), gr.update(value="")

    # Ensure directory exists
    os.makedirs("chats", exist_ok=True)

    create_new_chat(chat_name)

    # Get updated list of chats
    updated_chats = get_available_chats()

    # Return updates using gr.update()
    return gr.update(choices=updated_chats, value=chat_name), gr.update(value="")


def load_character_info(character_name):
    """Load and display character info"""
    try:
        with open(f"characters/character_cards/{character_name}.py", "r") as f:
            return f.read()
    except:
        return "Character info not available"


with gr.Blocks() as demo:
    # Initialize components that need to be referenced across tabs
    # chatbot = gr.Chatbot([], elem_id="chatbot", height=600, type="messages")
    current_chatbot = None
    chat_list = None
    msg = None

    with gr.Tabs():
        # Chat Tab
        with gr.Tab("Chat Interface"):
            with gr.Row():
                # Left column - Chat list and creation
                with gr.Column(scale=1):
                    gr.Markdown("### Available Chats")
                    chat_list = gr.Radio(
                        choices=get_available_chats(),
                        label="Select Chat",
                        interactive=True,
                    )

                    # Add chat creation section
                    gr.Markdown("### Create New Chat")
                    new_chat_name = gr.Textbox(
                        label="New Chat Name", placeholder="Enter chat name..."
                    )
                    create_chat_btn = gr.Button("Create Chat")

                # Middle column - Chat history
                with gr.Column(scale=2):
                    gr.Markdown("### Chat History")
                    chatbot = gr.Chatbot(
                        [], elem_id="chatbot", height=600, type="messages"
                    )
                    msg = gr.Textbox(
                        show_label=False,
                        placeholder="Type your message here...",
                        container=False,
                    )

                # Right column - Character selection (fixed indentation)
                with gr.Column(scale=1):
                    gr.Markdown("### Character Selection")

                    # User character section
                    gr.Markdown("#### User Character")
                    user_char = gr.Dropdown(
                        choices=get_available_characters(),
                        label="Select User Character",
                        interactive=True,
                        value=None,
                    )
                    user_info = gr.TextArea(
                        label="User Character Info", interactive=False, lines=10
                    )

                    # AI character section
                    gr.Markdown("#### AI Character")
                    ai_char = gr.Dropdown(
                        choices=get_available_characters(),
                        label="Select AI Character",
                        interactive=True,
                        value=None,
                    )
                    ai_info = gr.TextArea(
                        label="AI Character Info", interactive=False, lines=10
                    )

                    # Connect the dropdowns to their info displays
                    user_char.change(
                        fn=load_character_info, inputs=[user_char], outputs=[user_info]
                    )
                    ai_char.change(
                        fn=load_character_info, inputs=[ai_char], outputs=[ai_info]
                    )

        # ...existing code for Settings Tab...

        # Settings Tab
        with gr.Tab("Model Settings"):
            with gr.Row():
                # Left column
                with gr.Column():
                    gr.Markdown("### Model Configuration")
                    available_models = get_available_models()
                    model_name = gr.Dropdown(
                        choices=available_models,
                        label="Select Model",
                        value=available_models[0] if available_models else None,
                    )
                    model_status = gr.Markdown("Current model: None")

                    # Update global model when selection changes
                    model_name.change(
                        fn=update_model_selection,
                        inputs=[model_name],
                        outputs=[model_status],
                    )

                    temperature = gr.Slider(
                        minimum=0.0, maximum=2.0, value=0.7, label="Temperature"
                    )

                # Right column
                with gr.Column():
                    gr.Markdown("### Other Settings")
                    max_tokens = gr.Number(value=2000, label="Max Tokens")
                    context_length = gr.Number(value=4000, label="Context Length")

    create_chat_btn.click(
        fn=create_new_chat_and_refresh,
        inputs=[new_chat_name],
        outputs=[chat_list, new_chat_name],
    )

    chat_list.change(
        fn=on_chat_select,
        inputs=[chat_list, ai_char],  # Add ai_char as input
        outputs=[chat_list, chatbot],
    )

    msg.submit(
        fn=send_message,
        inputs=[msg, chatbot, chat_list, user_char, ai_char],
        outputs=[msg, chatbot],
    )

    # Initialize model on startup
    available_models = get_available_models()
    if available_models:
        current_model = available_models[0]


if __name__ == "__main__":
    # Initialize global model with first available model
    # print(ollama.list())
    available_models = get_available_models()
    if available_models:
        current_model = available_models[0]
    demo.launch()

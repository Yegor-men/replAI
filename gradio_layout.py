import gradio as gr
import ollama
import os
import json
import re

chats_filepath = "chats"
sys_prompts_filepath = "system_prompts"
character_cards_filepath = "character_cards"
model_templates_filepath = "model_templates"


def list_files_in_filepath(filepath):
    directory = os.listdir(filepath)
    files = [file for file in directory]
    return files


def list_ollama_models():
    ollama_list = ollama.list()
    models = [model.model for model in ollama_list.models]
    return models


def load_ndjson(json_filepath: str) -> list[dict]:
    """
    Read a newline-delimited JSON file and return a list of dicts.
    """
    history = []
    with open(json_filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                history.append(json.loads(line))
    return history


def sanitize_ndjson_into_history(
    ndjson_filepath: str,
    user_name: str,
) -> list[dict]:
    """
    Convert raw NDJSON entries with arbitrary 'sender' names into Gradio Chatbot format:
    - role: "user" or "assistant"
    - content: "[date time] sender: message"
    """
    raw = load_ndjson(ndjson_filepath)
    history = []
    for entry in raw:
        sender = entry["sender"]
        role = "user" if sender == user_name else "assistant"
        timestamp = f"{entry['date']} at {entry['time']}"
        content = f"[{timestamp}] {sender}\n\n{entry['content']}"
        history.append({"role": role, "content": content})
    return history


def append_ndjson_entry(entry: dict, json_filepath: str) -> None:
    """
    Append one JSON object as a new line to the NDJSON file.
    """
    with open(json_filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False))
        f.write("\n")


from datetime import datetime


def sanitize_sender_message(
    sender: str,
    content: str,
):
    safe_content = content.replace("\n", " ").strip()

    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    time_str = now.strftime("%H:%M")

    return {
        "sender": sender,
        "content": safe_content,
        "date": date_str,
        "time": time_str,
    }


def render_chat(chat_filename, user_name):
    """Loads the NDJSON and returns a Gradio‑ready history list."""
    path = os.path.join(chats_filepath, chat_filename)
    return sanitize_ndjson_into_history(path, user_name[:-3])


def on_send(chat_filename, user_name, message):
    """Sanitize + append the user message, then re-render the chat."""
    path = os.path.join(chats_filepath, chat_filename)
    # 1) sanitize and append
    entry = sanitize_sender_message(user_name[:-3], message)
    append_ndjson_entry(entry, path)
    # 2) return updated history and clear the textbox
    history = sanitize_ndjson_into_history(path, user_name[:-3])
    return gr.update(value=history), gr.update(value="")


sample_history = sanitize_ndjson_into_history(
    ndjson_filepath="chats/ndjson_history_sample.ndjson",
    user_name="alice",
)


# https://huggingface.co/spaces/gradio/theme-gallery

with gr.Blocks(
    theme="JohnSmith9982/small_and_pretty", fill_width=True, title="replAI"
) as demo:
    with gr.Tabs():
        with gr.Tab("Model Settings"):
            with gr.Row():
                with gr.Column(scale=1):
                    model_dropdown = gr.Dropdown(
                        choices=list_ollama_models(),
                        label="Model",
                        info="Select the Ollama model to use. Heavier models are recommended for both quality and more realistic speed (slower).",
                        interactive=True,
                    )
                    with gr.Column():
                        gr.Dropdown(
                            choices=list_files_in_filepath(model_templates_filepath),
                            label="Load Template",
                            info='Select to load a saved template for a model to use. Make sure to check the "Override Defaults" button in the bottom right for the changes to take effect.',
                            interactive=True,
                        )
                    with gr.Column():
                        gr.Textbox(
                            label="Filename",
                            info="Filename for the model template. This is how the template is/will be saved/deleted in the model_templates/ folder.",
                            interactive=True,
                        )
                    gr.Button(value="Save Model Template", interactive=True)
                    gr.Button(value="Delete Model Template", interactive=True)

                with gr.Column(scale=1):
                    temperature = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        step=0.01,
                        value=0.8,
                        label="Temperature",
                        info="Controls randomness: 0 is completely deterministic, higher values are more creative.",
                        interactive=True,
                    )

                    with gr.Column():
                        top_p = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            step=0.01,
                            value=0.9,
                            label="Top-p",
                            info="Keep the smallest set of tokens whose cumulative probability ≥ p.",
                            interactive=True,
                        )
                        top_k = gr.Slider(
                            minimum=1,
                            maximum=200,
                            step=1,
                            value=40,
                            label="Top-k",
                            info="Limit sampling to the top-k most likely tokens.",
                            interactive=True,
                        )

                    with gr.Column():
                        tfc_z = gr.Slider(
                            minimum=1.0,
                            maximum=5.0,
                            step=0.1,
                            value=1.0,
                            label="tfs_z",
                            info="Tail-free sampling filter. A value of 1.0 disables it; higher values have stronger filtering.",
                            interactive=True,
                        )

                with gr.Column(scale=1):
                    mirostat = gr.Slider(
                        minimum=0,
                        maximum=2,
                        step=1,
                        value=0,
                        label="Mirostat Mode",
                        info="0=off, 1=Mirostat v1, 2=Mirostat v2 (auto perplexity control).",
                        interactive=True,
                    )
                    mirostat_tau = gr.Slider(
                        minimum=1.0,
                        maximum=10.0,
                        step=0.5,
                        value=5.0,
                        label="Mirostat tau (τ)",
                        info="Target entropy for Mirostat; lower values have more focused output.",
                        interactive=True,
                    )
                    mirostat_eta = gr.Slider(
                        minimum=0.01,
                        maximum=1.0,
                        step=0.01,
                        value=0.1,
                        label="Mirostat eta (η)",
                        info="Learning rate for Mirostat adjustments; lower values equate to slower responses.",
                        interactive=True,
                    )

                with gr.Column(scale=1):
                    num_predict = gr.Slider(
                        minimum=1,
                        maximum=512,
                        step=1,
                        value=128,
                        label="Maximum Generated Tokens",
                        info="Maximum number of tokens the model will generate in one message.",
                        interactive=True,
                    )
                    with gr.Column():
                        num_ctx = gr.Slider(
                            minimum=512,
                            maximum=8192,
                            step=1,
                            value=2048,
                            label="Context Window",
                            info="How many tokens of history the model can attend to.",
                            interactive=True,
                        )
                    with gr.Column():
                        repeat_last_n = gr.Slider(
                            minimum=0,
                            maximum=512,
                            step=8,
                            value=64,
                            label="Repeat-Last-N",
                            info="How many tokens to look back on to penalize repetition.",
                            interactive=True,
                        )
                        repeat_penalty = gr.Slider(
                            minimum=0.5,
                            maximum=2,
                            step=0.1,
                            value=1.1,
                            label="Repeat Penalty",
                            info="Higher values more strongly penalize repeated tokens.",
                            interactive=True,
                        )
                    with gr.Column():
                        gr.Checkbox(
                            label="Override Defaults",
                            info="Check this box to override defaults with the changes above. Otherwise, Ollama model file defaults will be used instead. Recommended to keep this off unless you know what you are doing.",
                        )

        with gr.Tab("Character Cards"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Dropdown(
                        choices=list_files_in_filepath(character_cards_filepath),
                        label="Load",
                        info="Select the character card to load and modify it.",
                        interactive=True,
                    )
                    with gr.Column():
                        gr.Textbox(
                            label="Filename",
                            info="Filename for the character card. This is how the character card is/will be saved/deleted in the characters/character_cards/ folder.",
                            interactive=True,
                        )
                        gr.Button(value="Save Character Card", interactive=True)
                        gr.Button(value="Delete Character Card", interactive=True)

                with gr.Column(scale=3):

                    # TODO MAKE THIS THING JUST A COUPLE SELECTABLE BOXES NOT THE WHOLE SCRIPT

                    gr.TextArea(
                        label="Character Card",
                        info="The raw python file of the character card. replAI pulls data from these character cards to instantiate characters (instances of the Character class) and then uses these class instances later in the system prompt. Recommended to not modify this much (for now), unless if you are willing to dig in some extra code.",
                    )

        with gr.Tab("System Prompts"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Dropdown(
                        choices=list_files_in_filepath(sys_prompts_filepath),
                        label="Load",
                        info="Select the system prompt to load and modify it.",
                        interactive=True,
                    )
                    with gr.Column():
                        gr.Textbox(
                            label="Filename",
                            info="Filename for the system prompt. This is how the system prompt is/will be saved/deleted in the system_prompts/ folder.",
                            interactive=True,
                        )
                        gr.Button(value="Save System Prompt", interactive=True)
                        gr.Button(value="Delete System Prompt", interactive=True)

                with gr.Column(scale=3):
                    gr.TextArea(
                        label="System Prompt",
                        info="The raw python file of the system prompt. replAI pulls attributes from characters (instances of the Character class) and uses them for the system prompt. Recommended to not modify this much (for now), unless if you are willing to dig in some extra code.",
                        interactive=True,
                    )

        with gr.Tab("Human to AI chat"):
            with gr.Row():
                with gr.Column(scale=1):
                    with gr.Column():
                        current_chat = gr.Dropdown(
                            choices=list_files_in_filepath(chats_filepath),
                            label="Load",
                            info="Load an existing chat.",
                            interactive=True,
                        )
                    with gr.Column():
                        current_chat_filename = gr.Textbox(
                            label="Filename",
                            info="Filename for the chat. This is how the chat is/will be saved/deleted in the chats/ folder.",
                            interactive=True,
                        )
                        gr.Button(value="Create New Chat", interactive=True)
                        gr.Button(value="Delete Selected Chat", interactive=True)

                with gr.Column(scale=2):
                    with gr.Group():
                        chatbox = gr.Chatbot(
                            elem_id="chatbox",
                            value=sample_history,
                            type="messages",
                            show_label=False,
                            resizable=True,
                            show_copy_button=True,
                            layout="bubble",
                            group_consecutive_messages=False,
                            placeholder="The chat history will appear here",
                        )
                        user_message = gr.Textbox(
                            elem_id="user_message",
                            show_label=False,
                            placeholder="Type your message here...",
                            container=True,
                            submit_btn=False,
                        )

                with gr.Column(scale=1):
                    with gr.Column():
                        user_character = gr.Dropdown(
                            choices=list_files_in_filepath(character_cards_filepath),
                            label="User Character",
                            info="Info about the character that the human is roleplaying.",
                            interactive=True,
                        )
                        gr.TextArea(
                            label="user character details",
                            interactive=False,
                        )
                    with gr.Column():
                        ai_character = gr.Dropdown(
                            choices=list_files_in_filepath(character_cards_filepath),
                            label="AI Character",
                            info="Info about the character that the AI is roleplaying",
                            interactive=True,
                        )
                        gr.TextArea(
                            label="AI character details",
                            interactive=False,
                        )

    for inp in (current_chat, user_character, ai_character):
        inp.change(
            fn=render_chat, inputs=[current_chat, user_character], outputs=chatbox
        )

    # — Bind Enter in textbox to send flow —
    user_message.submit(
        fn=on_send,
        inputs=[current_chat, user_character, user_message],
        outputs=[chatbox, user_message],
        queue=False,
    )

demo.launch(favicon_path="misc/replAI_favicon_rounded.ico")

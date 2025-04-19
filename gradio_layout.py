import gradio as gr
import ollama
import os
import json
import re
from datetime import datetime
import yaml
from jinja2 import Template

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


def load_and_display_file(filepath: str, filename: str):
    """Fetch a file and render it in a textbox"""
    path = os.path.join(filepath, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error loading file: {str(e)}"


def load_ndjson_into_memory(
    ndjson_filename: str,
    max_entries: int = None,
) -> list[dict]:
    path = os.path.join(chats_filepath, ndjson_filename)

    entries = []
    with open(path, "r", encoding="utf-8") as f:
        entries = [json.loads(line) for line in f if line.strip()]
    max_entries = min(len(entries), max_entries)
    return entries[-max_entries:] if max_entries else entries


def sanitize_loaded_ndjson_into_history(
    loaded_ndjson: list[dict],
    chara_card_filename: str,
) -> list[dict]:
    chara_card_path = os.path.join(character_cards_filepath, chara_card_filename)
    with open(chara_card_path) as f:
        chara_card = yaml.safe_load(f)
        user_name = chara_card.get("name")

    history = []
    for entry in loaded_ndjson:
        sender = entry["sender"]
        role = "user" if sender == user_name else "assistant"
        timestamp = f"{entry['date']} at {entry['time']}"
        content = f"[{timestamp}] {sender}\n\n{entry['content']}"
        history.append({"role": role, "content": content})
    return history


def sanitize_and_send_message(
    ndjson_filename,
    sender_chara_card_filename,
    content: str,
):
    chara_card_path = os.path.join(character_cards_filepath, sender_chara_card_filename)
    with open(chara_card_path) as f:
        chara_card = yaml.safe_load(f)
        chara_name = chara_card.get("name")

    safe_content = content.replace("\n", " ").strip()

    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    time_str = now.strftime("%H:%M")

    message = {
        "sender": chara_name,
        "content": safe_content,
        "date": date_str,
        "time": time_str,
    }

    path = os.path.join(chats_filepath, ndjson_filename)

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(message, ensure_ascii=False) + "\n")


def ollama_generate_message(
    model_name: str,
    ndjson_filename: str,
    user_chara_card_filename: str,
    ai_chara_card_filename: str,
    sys_prompt_filename: str,
    num_messages: int = 1000,
):
    sys_prompt_path = os.path.join(sys_prompts_filepath, sys_prompt_filename)
    ai_chara_card_path = os.path.join(character_cards_filepath, ai_chara_card_filename)
    user_chara_card_path = os.path.join(
        character_cards_filepath, user_chara_card_filename
    )

    with open(ai_chara_card_path) as f:
        ai_card = yaml.safe_load(f)
    with open(user_chara_card_path) as f:
        user_card = yaml.safe_load(f)
    with open(sys_prompt_path) as f:
        tpl_text = f.read()
    system_message = Template(tpl_text).render(
        ai={
            "name": ai_card["name"],
            "description": ai_card["description"],
        },
        user={"name": user_card["name"], "description": user_card["description"]},
    )
    system_msg = {"role": "system", "content": system_message}
    in_mem = load_ndjson_into_memory(ndjson_filename, num_messages)
    curated = sanitize_loaded_ndjson_into_history(in_mem, user_chara_card_filename)

    messages = [system_msg, *curated]

    response = ollama.chat(model_name, messages=messages)
    model_message = response["message"]["content"]

    sanitize_and_send_message(ndjson_filename, ai_chara_card_filename, model_message)


def render_chat(
    ndjson_filename,
    user_chara_card_filename,
    last_n_messages_to_render: int = 1000,
):
    chat_path = os.path.join(chats_filepath, ndjson_filename)
    in_mem = load_ndjson_into_memory(ndjson_filename, last_n_messages_to_render)
    cleaned = sanitize_loaded_ndjson_into_history(in_mem, user_chara_card_filename)
    return cleaned


# https://huggingface.co/spaces/gradio/theme-gallery

with gr.Blocks(
    theme="JohnSmith9982/small_and_pretty", fill_width=True, title="replAI"
) as demo:
    with gr.Tabs():
        with gr.Tab("Model Settings"):
            with gr.Row():
                with gr.Column(scale=1):
                    model_name = gr.Dropdown(
                        choices=list_ollama_models(),
                        label="Model Editor",
                        info="Select the Ollama model to use. Heavier models are recommended for both quality and more realistic speed (slower).",
                        interactive=True,
                    )
                    with gr.Column():
                        model_template = gr.Dropdown(
                            choices=list_files_in_filepath(model_templates_filepath),
                            label="Load Template",
                            info='Select to load a saved template for a model to use. Make sure to check the "Override Defaults" button in the bottom right for the changes to take effect.',
                            interactive=True,
                        )
                    with gr.Column():
                        model_template_filename = gr.Textbox(
                            label="Filename",
                            info="Filename for the model template. This is how the template is/will be saved/deleted in the model_templates/ folder.",
                            interactive=True,
                        )
                    save_model_template = gr.Button(
                        value="Save Model Template", interactive=True
                    )
                    delete_model_template = gr.Button(
                        value="Delete Model Template", interactive=True
                    )

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

        with gr.Tab("Character Card Editor"):
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
                    gr.TextArea(
                        label="Character Card",
                        info="The raw yaml file of the character card. replAI pulls data from these character cards to instantiate characters (instances of the Character class) and then uses these class instances later in the system prompt. Recommended to not modify this much (for now), unless if you are willing to dig in some extra code.",
                    )

        with gr.Tab("System Prompt Editor"):
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

        with gr.Tab("1 on 1 chat"):
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
                    with gr.Column():
                        ollama_model = gr.Dropdown(
                            choices=list_ollama_models(),
                            label="Load Model",
                            info="Select the model to use.",
                            interactive=True,
                        )

                with gr.Column(scale=2):
                    with gr.Group():
                        chatbox = gr.Chatbot(
                            elem_id="chatbox",
                            label=None,
                            value=None,
                            show_label=False,
                            placeholder="The chat history will appear here.",
                            type="messages",
                            resizable=True,
                            show_copy_button=True,
                            layout="bubble",
                            group_consecutive_messages=False,
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
                            info="Select the character you will be roleplaying.",
                            interactive=True,
                        )
                        user_character_description = gr.TextArea(
                            label=None,
                            show_label=False,
                            value=None,
                            placeholder="Your character's description will appear here.",
                            interactive=False,
                        )
                        ai_character = gr.Dropdown(
                            choices=list_files_in_filepath(character_cards_filepath),
                            label="AI Character",
                            info="Select the character that the AI will be roleplaying.",
                            interactive=True,
                        )
                        ai_character_description = gr.TextArea(
                            label=None,
                            show_label=False,
                            value=None,
                            placeholder="The AI's character description will appear here.",
                            interactive=False,
                        )
                    with gr.Column():
                        system_prompt = gr.Dropdown(
                            choices=list_files_in_filepath(sys_prompts_filepath),
                            label="System Prompt",
                            info="Select the system prompt that the AI will use.",
                            interactive=True,
                        )
                        system_prompt_description = gr.TextArea(
                            label=None,
                            show_label=False,
                            value=None,
                            placeholder="System prompt description will appear here.",
                            interactive=False,
                        )

    current_chat.select(
        fn=lambda x: x, inputs=current_chat, outputs=current_chat_filename
    ).then(fn=render_chat, inputs=[current_chat, user_character], outputs=chatbox)

    user_character.select(
        fn=lambda f: load_and_display_file(character_cards_filepath, f),
        inputs=user_character,
        outputs=user_character_description,
    ).then(fn=render_chat, inputs=[current_chat, user_character], outputs=chatbox)

    ai_character.select(
        fn=lambda f: load_and_display_file(character_cards_filepath, f),
        inputs=ai_character,
        outputs=ai_character_description,
    ).then(fn=render_chat, inputs=[current_chat, user_character], outputs=chatbox)

    system_prompt.select(
        fn=lambda f: load_and_display_file(sys_prompts_filepath, f),
        inputs=system_prompt,
        outputs=system_prompt_description,
    )

    user_message.submit(
        fn=sanitize_and_send_message,
        inputs=[current_chat, user_character, user_message],
        outputs=None,
    ).then(
        fn=lambda: "",
        inputs=None,
        outputs=user_message,
    ).then(
        fn=render_chat,
        inputs=[current_chat, user_character],
        outputs=chatbox,
    ).then(
        fn=lambda a, b, c, d, e: ollama_generate_message(
            model_name=a,
            ndjson_filename=b,
            user_chara_card_filename=c,
            ai_chara_card_filename=d,
            sys_prompt_filename=e,
            num_messages=1000,
        ),
        inputs=[
            ollama_model,
            current_chat,
            user_character,
            ai_character,
            system_prompt,
        ],
        outputs=None,
    ).then(
        fn=render_chat,
        inputs=[current_chat, user_character],
        outputs=chatbox,
    )

    demo.load(
        fn=lambda: (
            current_chat.value if current_chat.value else None,
            (
                load_and_display_file(character_cards_filepath, user_character.value)
                if user_character.value
                else None
            ),
            (
                load_and_display_file(character_cards_filepath, ai_character.value)
                if ai_character.value
                else None
            ),
            (
                load_and_display_file(sys_prompts_filepath, system_prompt.value)
                if system_prompt.value
                else None
            ),
            (
                render_chat(current_chat.value, user_character.value)
                if current_chat.value and user_character.value
                else None
            ),
        ),
        outputs=[
            current_chat_filename,
            user_character_description,
            ai_character_description,
            system_prompt_description,
            chatbox,
        ],
    )

demo.launch(favicon_path="misc/replAI_favicon_rounded.ico")

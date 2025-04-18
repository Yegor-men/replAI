import gradio as gr
import ollama


# https://huggingface.co/spaces/gradio/theme-gallery

with gr.Blocks(theme="JohnSmith9982/small_and_pretty", fill_width=True, title="replAI") as demo:
    with gr.Tabs():
        with gr.Tab("Model Settings"):
            with gr.Row():
                with gr.Column(scale=1):
                    ollama_list = ollama.list()
                    model_names = []
                    for model in ollama_list.models:
                        model_names.append(model.model)

                    model_dropdown = gr.Dropdown(
                        choices=model_names,
                        label="Model",
                        info="Select the Ollama model to use. Heavier models are recommended for both quality and more realistic speed (slower).",
                        interactive=True,
                    )
                    gr.Markdown()
                    gr.Dropdown(
                        choices=[1, 2, 3, 4, 5],
                        label="Load Template",
                        info='Select to load a saved template for a model to use. Make sure to check the "Override Defaults" button in the bottom right for the changes to take effect.',
                        interactive=True,
                    )
                    gr.Markdown()
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
                    gr.Markdown()
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
                    gr.Markdown()
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
                    gr.Markdown()
                    num_ctx = gr.Slider(
                        minimum=512,
                        maximum=8192,
                        step=1,
                        value=2048,
                        label="Context Window",
                        info="How many tokens of history the model can attend to.",
                        interactive=True,
                    )
                    gr.Markdown()
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
                    gr.Markdown()
                    gr.Checkbox(
                        label="Override Defaults",
                        info="Check this box to override defaults with the changes above. Otherwise, Ollama model file defaults will be used instead. Recommended to keep this off unless you know what you are doing.",
                    )

        with gr.Tab("Character Cards"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Dropdown(
                        choices=[1, 2, 3],
                        label="Load",
                        info="Select the character card to load and modify it.",
                        interactive=True,
                    )
                    gr.Markdown()
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

        with gr.Tab("Prompt Templates"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Dropdown(
                        choices=[1, 2, 3],
                        label="Load",
                        info="Select the system prompt to load and modify it.",
                        interactive=True,
                    )
                    gr.Markdown()
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
                    gr.Dropdown(
                        choices=[1, 2, 3],
                        label="Load",
                        info="Load an existing chat.",
                        interactive=True,
                    )
                    gr.Markdown()
                    gr.Textbox(
                        label="Filename",
                        info="Filename for the chat. This is how the chat is/will be saved/deleted in the chats/ folder.",
                        interactive=True,
                    )
                    gr.Button(value="Create New Chat", interactive=True)
                    gr.Button(value="Delete Selected Chat", interactive=True)

                with gr.Column(scale=2):
                    gr.Markdown("area where chat is read")
                    gr.Markdown("cell to enter text and send")

                with gr.Column(scale=1):
                    gr.Dropdown(
                        choices=[1, 2, 3, 4, 5, 6, 7],
                        label="User Character",
                        info="Info about the character that the human is roleplaying.",
                        interactive=True,
                    )
                    gr.TextArea(
                        label="user character details",
                        interactive=False,
                    )
                    gr.Markdown()
                    gr.Dropdown(
                        choices=[1, 2, 3, 4, 5, 6, 7],
                        label="AI Character",
                        info="Info about the character that the AI is roleplaying",
                        interactive=True,
                    )
                    gr.TextArea(
                        label="AI character details",
                        interactive=False,
                    )

demo.launch(favicon_path="misc/replAI_favicon_rounded.ico")

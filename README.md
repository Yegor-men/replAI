
![Logo](https://github.com/Yegor-men/replAI/blob/main/misc/replAI_banner.png)


# replAI

## Another textgen webui? Why?

Most, if not all of today's webui's are chat based. You send one message to the AI, and it sends one back. If you want to chain messages like you would in DMs, you have to either delete the AI responses, or use some other hacky workaround. Worse yet, AI's aren't allowed to chain messages. What results is a clunky, shallow and unimmersive texting experience.

Point is, **there is no easy way to text message an AI as you would in real life**

replAI (pronounced [/ɹɪˈplaɪ/](https://en.wiktionary.org/wiki/reply)) aims to fix that. Both you and the AI of your choice converse via text messages. Naturally presented, naturally flowing. Send one message or send many. replAI aims to recreate the feeling of texting like on any other app.
## Features

- Uses Ollama as the local backend
- Shared personality feature, both the AI and human can play the same persona
- Allows for multiple channels with different personas
- Does NOT rely on tool calling. Any model can be used
- AI is aware of the time that the messages were sent at
- Allows both the user and the AI to send messages whenever, like in real texting
## Roadmap

- Create chats, personas, etc from within the webui
- Make the AI sometimes initiate conversations by itself
- Add memory embedding
- Implement image uploads and image recognition
- Create "servers" where multiple AIs can interact
- Allow the AI to generate images
- Implement support for other local backends
- Implement support for online providers

## Installation

This assumes that you have the backend (Ollama for now) installed.

Simply clone the repo, install the python requirements and run main.py

FOR NOW: make sure you download a "v" version, not a "uf" version. Simply clone the latest v version while I don't have branches yet.

```bash
git clone https://github.com/Yegor-men/replAI
# pip install -r requirements.txt
python main.py
```
and then visit [http://localhost:7860]() to open the frontend.
    
## Documentation

The wiki includes everything about the project. It explains what replAI does behind the scenes, so that you know what to (and what not to) expect of it, and how you can modify the code to better suit your needs.

[wiki](https://github.com/Yegor-men/replAI/wiki)


## Contributing

Contributions are always welcome!

Feel free to fork the repo, submit pull requests, report issues. I'll occasionally check in on them.

For more advanced/niche stuff, you can email me at yegor.mn@gmail.com

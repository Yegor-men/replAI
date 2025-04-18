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

    try:
        chat_history = load_json_chat(json_chat_filepath, ai_class_instance)

        messages = [
            {
                "role": "system",
                "content": system_prompt_function(
                    ai_class_instance, user_class_instance, timestamp
                ),
            }
        ]
        messages.extend(chat_history)

        # Make the API call
        stream = ollama.chat(
            model=model_name,
            messages=messages,
            stream=True,
        )

        # Collect the raw response
        response = ""
        for chunk in stream:
            if chunk and "message" in chunk and "content" in chunk["message"]:
                content = chunk["message"]["content"]
                # Don't print timestamps/names that might be in the response
                print(
                    content.replace(
                        "[" + timestamp + "] - " + ai_class_instance.name + ": ", ""
                    ),
                    end="",
                    flush=True,
                )
                response += content

        if not response:
            response = "I apologize, but I couldn't generate a response."

        # Clean up potential timestamp prefixes from the model's response
        clean_response = response.replace(
            "[" + timestamp + "] - " + ai_class_instance.name + ": ", ""
        )

        # Add to chat history with single timestamp prefix
        chat_history.append(
            {
                "role": "assistant",
                "content": f"[{timestamp}] - {ai_class_instance.name}: {clean_response}",
            }
        )

        save_json_chat(
            loaded_json_chat=chat_history,
            json_chat_filename=json_chat_filepath,
            ai_class_instance=ai_class_instance,
        )

        return clean_response

    except Exception as e:
        print(f"Error in ai_send_message: {e}")
        return "I encountered an error while trying to respond."

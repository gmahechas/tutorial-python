from helper import add_user_message, add_assistant_message, stream_chat

messages = []
add_user_message(messages, "generate a very short event bridge rule as json")
add_assistant_message(messages, "```json")

with stream_chat(messages, stop_sequences=["```"]) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

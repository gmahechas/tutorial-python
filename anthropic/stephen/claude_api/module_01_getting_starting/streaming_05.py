from helper import add_user_message, stream_chat

messages = []
add_user_message(messages, "generate a one sentence movie idea")

with stream_chat(messages) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

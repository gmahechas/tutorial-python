from helper import add_user_message, add_assistant_message, stream_chat

messages = []
add_user_message(messages, "generate three diffrent sample AWS CLI commands. each should be very short")
add_assistant_message(messages, "here are three sample AWS CLI commands whitout any comment:\n```bash")

with stream_chat(messages, stop_sequences=["```"]) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

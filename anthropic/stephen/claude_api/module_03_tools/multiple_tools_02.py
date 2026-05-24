from helper import add_user_message, chat, run_conversation


messages = []
add_user_message(
    messages,
    "what is the current time in HH:MM format? Also, what is the current time in SS format?, format?",
)

run_conversation(messages)
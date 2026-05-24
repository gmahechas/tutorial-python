from helper import add_user_message, chat, run_conversation


messages = []
add_user_message(
    messages,
    "set a reminder for my doctor's appointment. its 177 days after Jan 1st, 2050",
)

run_conversation(messages)

from helper import add_user_message, chat, run_conversation


messages = []
add_user_message(
    messages,
    """" set two reminders for Jan 1, 2027 at 8AM:
            * I have a doctor's appointment
            * taxes are due
    """,
)

run_conversation(messages)

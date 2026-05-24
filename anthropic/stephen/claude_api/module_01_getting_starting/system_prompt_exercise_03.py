from helper import add_user_message, chat

system_prompt = """
    you are python engineer who writes very concise code.
    """

messages = []
add_user_message(messages, "write a python function that checks a string for duplicate characters")
answer = chat(messages)
print(answer)

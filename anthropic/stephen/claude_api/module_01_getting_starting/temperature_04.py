from helper import add_user_message, chat

messages = []
add_user_message(messages, "generate a one sentence movie idea")
answer = chat(messages, temperature=1.0)
print(answer)

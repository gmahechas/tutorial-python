from helper import add_user_message, add_assistant_message, chat

messages = []
add_user_message(messages, "what is quantum computing?, Answer in one sentence")
answer = chat(messages)
add_assistant_message(messages, answer)
add_user_message(messages, "write another sentence")
answer = chat(messages)
add_assistant_message(messages, answer)
print(messages)

from helper import add_user_message, chat

system_prompt = """
    Your are a patient math tutor.
    Do not directly answer a student's questions.
    Guide them to a solution step by step.
    """

messages = []
add_user_message(messages, "how do I solve 5x+3=2 for x?, I think it's -1/5")
answer = chat(messages, system_prompt)
print(answer)

from tools import article_summary_schema
from helper import add_user_message, chat, text_from_message


messages = []
add_user_message(
    messages,
    """"
    write a one-paragraph scholarly article about computer science.
    Include a title and author name.
    """,
)

response_1 = chat(messages)
text_1 = text_from_message(response_1)
print(text_1)
add_user_message(messages, text_1)

response_2 = chat(
    messages,
    tools=[article_summary_schema],
    tool_choice={"type": "tool", "name": "article_summary"},
)
print(response_2) # in response_2.content[0].input we have the structure data
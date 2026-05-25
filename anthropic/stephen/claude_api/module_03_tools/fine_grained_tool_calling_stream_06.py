from tools import save_article_schema
from helper import add_user_message, run_conversation_stream


messages = []
add_user_message(
    messages,
    "Create and save a fake computer science article",
)

response_1 = run_conversation_stream(
    messages,
    tools=[save_article_schema],
    fine_grained=True,  # if false, claude api will make sure that json is valid
)
print(response_1)

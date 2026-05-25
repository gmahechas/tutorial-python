from tools import save_article_schema
from helper import add_user_message, run_conversation

messages = []

add_user_message(
    messages,
    """
    open ./test_file.py and create a new function to calculate the area of a circle
    """,
)

run_conversation(messages)
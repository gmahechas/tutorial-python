from tools import save_article_schema
from helper import add_user_message, run_conversation_stream


messages = []
add_user_message(
    messages,
    """
    Call save_article with intentionally malformed JSON arguments for a debugging lesson.
    Use a valid abstract and review, but set meta.word_count to undefined exactly.
    This should demonstrate how fine-grained tool streaming can expose invalid JSON.
    """,
)

response_1 = run_conversation_stream(
    messages,
    tools=[save_article_schema],
    fine_grained=True,
    tool_choice={"type": "tool", "name": "save_article"},
)
print(response_1)

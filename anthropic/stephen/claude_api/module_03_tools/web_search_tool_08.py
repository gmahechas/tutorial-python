from tools import web_search_schema
from helper import add_user_message, run_conversation

# The web_search_20250305 schema is correct for Anthropic's native Web Search
# tool. If this is routed through LiteLLM, the proxy must also support Anthropic
# server tools/web search for the configured model group.

messages = []
add_user_message(
    messages,
    """
    What's the best exercise for gaining leg muscle?
    """,
)
response = run_conversation(
    messages,
    tools=[web_search_schema],
    tool_choice={"type": "tool", "name": "web_search"},
)
print(response)

import os
from anthropic import Anthropic
from helper import add_user_message, add_assistant_message, chat
from tools import get_current_datetime_schema, get_current_datetime

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_AUTH_TOKEN"),
    base_url=os.environ.get("ANTHROPIC_BASE_URL"),
)

messages = []
add_user_message(messages, "what is the exact time, formatted as HH:MM:SS")

response_1 = chat(messages, tools=[get_current_datetime_schema], temperature=1.0)
add_assistant_message(messages, response_1.content)

id, input = response_1.content[0].id, response_1.content[0].input
result = get_current_datetime(**input)

add_user_message(
    messages,
    [
        {
            "type": "tool_result",
            "tool_use_id": id,
            "content": result,
        }
    ],
)


response_2 = chat(messages, tools=[get_current_datetime_schema], temperature=1.0)

print(response_2.content[0].text)

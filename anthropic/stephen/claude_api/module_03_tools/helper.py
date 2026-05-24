import os
import json
from anthropic import Anthropic
from anthropic.types import Message
from tools import (
    add_duration_to_datetime,
    add_duration_to_datetime_schema,
    batch_tool_schema,
    get_current_datetime_schema,
    get_current_datetime,
    set_reminder,
    set_reminder_schema,
)

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_AUTH_TOKEN"),
    base_url=os.environ.get("ANTHROPIC_BASE_URL"),
)


def add_user_message(messages, message):
    user_message = {
        "role": "user",
        "content": message.content if isinstance(message, Message) else message,
    }
    messages.append(user_message)
    return messages


def add_assistant_message(messages, message):
    assistant_message = {
        "role": "assistant",
        "content": message.content if isinstance(message, Message) else message,
    }
    messages.append(assistant_message)
    return messages


def chat(
    messages,
    system_prompt=None,
    temperature=1.0,
    stop_sequences=[],
    tools=None,
    tool_choice=None,
):
    params = {
        "model": "claude-sonnet-4-5-20250929",
        "max_tokens": 1024,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }
    if system_prompt:
        params["system"] = system_prompt
    if tools:
        params["tools"] = tools
    if tool_choice:
        params["tool_choice"] = tool_choice
    message = client.messages.create(**params)
    return message


def text_from_message(message):
    return "\n".join([block.text for block in message.content if block.type == "text"])


def run_batch_tool(invocations=[]):
    batch_output = []
    for invocation in invocations:
        name = invocation["name"]
        arguments = json.loads(invocation["arguments"])

        tool_output = run_tool(name, arguments)
        batch_output.append(
            {
                "tool_name": name,
                "output": tool_output,
            }
        )
    return batch_output


def run_tool(tool_name, tool_input):
    if tool_name == "get_current_datetime":
        return get_current_datetime(**tool_input)
    elif tool_name == "add_duration_to_datetime":
        return add_duration_to_datetime(**tool_input)
    elif tool_name == "set_reminder":
        return set_reminder(**tool_input)
    elif tool_name == "batch_tool":
        return run_batch_tool(tool_input["invocations"])


def run_tools(response):
    tool_requests = [block for block in response.content if block.type == "tool_use"]
    tool_result_blocks = []
    for tool_request in tool_requests:
        try:
            tool_output = run_tool(tool_request.name, tool_request.input)
            tool_result_block = {
                "type": "tool_result",
                "tool_use_id": tool_request.id,
                "content": json.dumps(tool_output),
                "is_error": False,
            }
        except Exception as e:
            tool_result_block = {
                "type": "tool_result",
                "tool_use_id": tool_request.id,
                "content": f"Error: {e}",
                "is_error": True,
            }
        tool_result_blocks.append(tool_result_block)
    return tool_result_blocks


def run_conversation(messages):
    while True:
        response = chat(
            messages,
            tools=[
                get_current_datetime_schema,
                add_duration_to_datetime_schema,
                set_reminder_schema,
                #batch_tool_schema, # removing this tools the agent will send 2 separate tool calls
            ],
        )
        add_assistant_message(messages, response)
        print(text_from_message(response))

        if response.stop_reason != "tool_use":
            break

        tool_results = run_tools(response)
        add_user_message(messages, tool_results)

    return messages

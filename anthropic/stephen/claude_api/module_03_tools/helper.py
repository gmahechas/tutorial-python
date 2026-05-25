import os
import json
from anthropic import Anthropic
from tools import (
    add_duration_to_datetime,
    add_duration_to_datetime_schema,
    batch_tool_schema,
    get_current_datetime_schema,
    get_current_datetime,
    save_article,
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
        "content": message.content if hasattr(message, "content") else message,
    }
    messages.append(user_message)
    return messages


def add_assistant_message(messages, message):
    assistant_message = {
        "role": "assistant",
        "content": message.content if hasattr(message, "content") else message,
    }
    messages.append(assistant_message)
    return messages

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
    elif tool_name == "save_article":
        return save_article(**tool_input)


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

def run_conversation(messages):
    while True:
        response = chat(
            messages,
            tools=[
                get_current_datetime_schema,
                add_duration_to_datetime_schema,
                set_reminder_schema,
                # batch_tool_schema, # removing this tools the agent will send 2 separate tool calls
            ],
        )
        add_assistant_message(messages, response)
        print(text_from_message(response))

        if response.stop_reason != "tool_use":
            break

        tool_results = run_tools(response)
        add_user_message(messages, tool_results)

    return messages


def chat_stream(
    messages,
    system=None,
    temperature=1.0,
    stop_sequences=[],
    tools=None,
    tool_choice=None,
    betas=[],
):
    params = {
        "model": "claude-sonnet-4-5-20250929",
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }

    if tool_choice:
        params["tool_choice"] = tool_choice

    if tools:
        params["tools"] = tools

    if system:
        params["system"] = system

    if betas:
        params["betas"] = betas

    return client.beta.messages.stream(**params)


def run_conversation_stream(messages, tools=[], tool_choice=None, fine_grained=False):
    while True:
        with chat_stream(
            messages,
            tools=tools,
            betas=["fine-grained-tool-streaming-2025-05-14"] if fine_grained else [],
            tool_choice=tool_choice,
        ) as stream:
            for chunk in stream:
                if chunk.type == "text":
                    print(chunk.text, end="")

                if chunk.type == "content_block_start":
                    if chunk.content_block.type == "tool_use":
                        print(f'\n>>> Tool Call: "{chunk.content_block.name}"')

                if chunk.type == "input_json" and chunk.partial_json:
                    print(chunk.partial_json, end="")

                if chunk.type == "content_block_stop":
                    print("\n")

            response = stream.get_final_message()

        add_assistant_message(messages, response)

        if response.stop_reason != "tool_use":
            break

        tool_results = run_tools(response)
        add_user_message(messages, tool_results)

        if tool_choice:
            break

    return messages

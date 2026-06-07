import os
import json
from pathlib import Path
from anthropic import Anthropic
from tools import (
    TextEditorTool,
    add_duration_to_datetime,
    add_duration_to_datetime_schema,
    batch_tool_schema,
    get_current_datetime_schema,
    get_current_datetime,
    get_text_edit_schema,
    save_article,
    set_reminder,
    set_reminder_schema,
)

thinking_test_str = "ANTHROPIC_MAGIC_STRING_TRIGGER_REDACTED_THINKING_46C9A13E193C177646C7398A98432ECCCE4C1253D5E2D82641AC0E52CC2876CB"

text_editor_tool = TextEditorTool()

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
    output = []
    for block in message.content:
        if block.type == "thinking":
            signature_label = (
                " (signature present)" if getattr(block, "signature", None) else ""
            )
            output.append(f"[thinking{signature_label}]\n{block.thinking}")
        elif block.type == "redacted_thinking":
            output.append(
                "[redacted thinking]\nThinking content was redacted by Anthropic."
            )
        elif block.type == "text":
            output.append(block.text)
    return "\n\n".join(output)


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
    elif tool_name == "str_replace_based_edit_tool":
        command = tool_input["command"]
        if command == "view":
            return text_editor_tool.view(
                tool_input["path"], tool_input.get("view_range")
            )
        elif command == "str_replace":
            return text_editor_tool.str_replace(
                tool_input["path"], tool_input["old_str"], tool_input["new_str"]
            )
        elif command == "create":
            return text_editor_tool.create(tool_input["path"], tool_input["file_text"])
        elif command == "insert":
            return text_editor_tool.insert(
                tool_input["path"],
                tool_input["insert_line"],
                tool_input["new_str"],
            )
        elif command == "undo_edit":
            return text_editor_tool.undo_edit(tool_input["path"])
        else:
            raise Exception(f"Unknown text editor command: {command}")
    else:
        raise Exception(f"Unknown tool name: {tool_name}")


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
    thinking=False,
    thinking_budget=1024,
):
    params = {
        "model": "claude-sonnet-4-5-20250929",
        "max_tokens": 4096,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }

    if thinking:
        params["thinking"] = {
            "type": "enabled",
            "budget_tokens": thinking_budget,
        }

    if tools:
        tools_clone = tools.copy()
        last_tool = dict(tools_clone[-1])
        last_tool["cache_control"] = {"type": "ephemeral"}
        tools_clone[-1] = last_tool
        params["tools"] = tools_clone

    if system_prompt:
        params["system"] = [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ]

    if tool_choice:
        params["tool_choice"] = tool_choice
    message = client.messages.create(**params)
    return message


def run_conversation(
    messages,
    tools=None,
    tool_choice=None,
    thinking=False,
    thinking_budget=1024,
    system_prompt=None,
):
    conversation_tools = tools or [
        get_current_datetime_schema,
        add_duration_to_datetime_schema,
        set_reminder_schema,
        get_text_edit_schema,
        # batch_tool_schema, # removing this tools the agent will send 2 separate tool calls
    ]
    while True:
        response = chat(
            messages,
            system_prompt=system_prompt,
            tools=conversation_tools,
            tool_choice=tool_choice,
            thinking=thinking,
            thinking_budget=thinking_budget,
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


def upload(file_path):
    path = Path(file_path)
    extension = path.suffix.lower()

    mime_type_map = {
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".md": "text/plain",
        ".py": "text/plain",
        ".js": "text/plain",
        ".html": "text/plain",
        ".css": "text/plain",
        ".csv": "text/csv",
        ".json": "application/json",
        ".xml": "application/xml",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }

    mime_type = mime_type_map.get(extension)

    if not mime_type:
        raise ValueError(f"Unknown mimetype for extension: {extension}")
    filename = path.name

    with open(file_path, "rb") as file:
        return client.beta.files.upload(file=(filename, file, mime_type))


def list_files():
    return client.beta.files.list()


def delete_file(id):
    return client.beta.files.delete(id)


def download_file(id, filename=None):
    file_content = client.beta.files.download(id)

    if not filename:
        file_metadata = get_metadata(id)
        file_content.write_to_file(file_metadata.filename)
    else:
        file_content.write_to_file(filename)


def get_metadata(id):
    return client.beta.files.retrieve_metadata(id)

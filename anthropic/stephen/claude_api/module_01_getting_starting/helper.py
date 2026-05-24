import os
from anthropic import Anthropic

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_AUTH_TOKEN"),
    base_url=os.environ.get("ANTHROPIC_BASE_URL"),
)


def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)
    return messages


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)
    return messages


def chat(messages, system_prompt=None, temperature=1.0):
    params = {
        "model": "claude-sonnet-4-5-20250929",
        "max_tokens": 1024,
        "messages": messages,
        "temperature": temperature,
    }
    if system_prompt:
        params["system"] = system_prompt
    message = client.messages.create(**params)
    return message.content[0].text


def stream_chat(messages, system_prompt=None, temperature=1.0, stop_sequences=None):
    params = {
        "model": "claude-sonnet-4-5-20250929",
        "max_tokens": 1024,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }
    if system_prompt:
        params["system"] = system_prompt
    return client.messages.stream(**params)

import json
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


def chat(messages, system_prompt=None, temperature=1.0, stop_sequences=None):
    params = {
        "model": "claude-sonnet-4-5-20250929",
        "max_tokens": 1024,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
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


def generate_dataset():
    prompt = """
"Generate a evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
each representing task that requires Python, JSON, or a Regex to complete.

Example output:
```json
[
    {
        "task": "Description of task",
        "format": "json", (or "python", or "regex"),
        "solution_criteria": "Key criteria for evaluating the solution",
    },
    ...additional
]
```

* Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a regular expression.
* Focus on tasks that do not require writing much code

Please generate 3 objects.
"""
    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")
    text = chat(messages, stop_sequences=["```"])
    return json.loads(text)

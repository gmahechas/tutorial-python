import base64
from pathlib import Path
from helper import add_user_message, run_conversation

IMAGE_PATH = Path(__file__).parent / "earth_03.pdf"


with open(IMAGE_PATH, "rb") as f:
    file_bytes = base64.b64encode(f.read()).decode("utf-8")

messages = []
add_user_message(
    messages,
    [
        {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": file_bytes,
            },
        },
        {"type": "text", "text": "summarize the document in one sentence"},
    ],
)

response_1 = run_conversation(messages)
print(response_1)

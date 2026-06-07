from pathlib import Path
from helper import upload, add_user_message, run_conversation

FILE_PATH = Path(__file__).parent / "code_execution_06.csv"

file_metadata = upload(FILE_PATH)
print(file_metadata)

messages = []
add_user_message(
    messages,
    [
        {
            "type": "text",
            "text": """
                Run a detailed analysis to determine major drivers of churn.
                Your final output should include at least one detailed plot summarizing your findings.

                Critical note: Every time you execute code, you're starting with a completely clean slate. 
                No variables or library imports from previous executions exist. You need to redeclare/reimport all variables/libraries.
            """,
        },
        {"type": "container_upload", "file_id": file_metadata.id},
    ],
)

run_conversation(messages, tools=[{"type": "code_execution_20250825", "name": "code_execution"}])

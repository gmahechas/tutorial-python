from helper import add_user_message, run_conversation


messages = []
add_user_message(
    messages,
    "write a one paragraph guide to recursion",  # Use thinking_test_str to test redacted thinking handling.
)

response_1 = run_conversation(messages, thinking=True)
print(response_1)

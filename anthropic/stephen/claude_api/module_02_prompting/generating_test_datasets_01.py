import json
from helper import generate_dataset

dataset = generate_dataset()
with open("anthropic/stephen/claude_api/module_02_prompting/dataset.json", "w") as f:
    json.dump(dataset, f)
from helper import PromptEvaluator

evaluator = PromptEvaluator(max_concurrent_tasks=3)

dataset = evaluator.generate_dataset(
    # Describe the purpose or goal of the prompt you're trying to test
    task_description="write a compact, concise 1 day meal plan for a single athlete",
    # Describe the different inputs that your prompt requires
    prompt_inputs_spec={
        "height": "Athlete's height in cm",
        "weight": "Athlete's weight in kg",
        "goal": "goal of the athlete",
        "restrictions": "dietary restrictions of the athlete",
    },
    # Where to write the generated dataset
    output_file="anthropic/stephen/claude_api/module_02_01_prompting_engineer/dataset.json",
    # Number of test cases to generate (recommend keeping this low if you're getting rate limit errors)
    num_cases=3,
)
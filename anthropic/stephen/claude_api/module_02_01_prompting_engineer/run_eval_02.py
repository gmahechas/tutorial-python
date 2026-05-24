from generating_datasets_01 import evaluator
from helper import add_user_message, chat


def run_prompt(prompt_inputs):
    prompt = f"""
    Generate a one-day meal plan for an athlete that meets their dietary restrictions.

    Height: {prompt_inputs["height"]}
    Weight: {prompt_inputs["weight"]}
    Goal: {prompt_inputs["goal"]}
    Restrictions: {prompt_inputs["restrictions"]}

    Guidelines:
    1. Include accurate daily calorie amount
    2. Show protein, fat, and carb amounts
    3. Specify when to eat each meal
    4. Use only foods that fix restrictions
    5. List all portion sizes in grams
    6. Keep budget-friendly if mentioned
    """

    messages = []
    add_user_message(messages, prompt)
    return chat(messages)


results = evaluator.run_evaluation(
    run_prompt_function=run_prompt,
    dataset_file="anthropic/stephen/claude_api/module_02_01_prompting_engineer/dataset.json",
    extra_criteria="""
    The output should include:
    - Daily caloric total
    - Macronutrient breakdown
    - Meals with exact foods, portions, and timing
    """,
    json_output_file="anthropic/stephen/claude_api/module_02_01_prompting_engineer/output.json",
    html_output_file="anthropic/stephen/claude_api/module_02_01_prompting_engineer/output.html",
)

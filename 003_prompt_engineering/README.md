# Prompt Engineering

Prompt engineering is about taking a prompt you've written and improving it to get more reliable, higher-quality outputs. This process involves iterative refinement — starting with a basic prompt, evaluating its performance, then systematically applying engineering techniques to improve it.

## Iterative Improvement Process

Follow this cycle and repeat until you achieve your desired results:

1. Set a goal — Define what you want your prompt to accomplish.
2. Write an initial prompt — Create a basic first attempt.
3. Evaluate the prompt — Test it against your criteria.
4. Apply prompt engineering techniques — Use specific methods to improve performance.
5. Re-evaluate — Verify that your changes improved results.

Repeat steps 4–5 until satisfied. Each iteration should show measurable improvement in your evaluation scores.

## Evaluation Pipeline (Example)

To demonstrate this process, we use a `PromptEvaluator` class that handles dataset generation and model grading. Control concurrency with `max_concurrent_tasks`:

```python
evaluator = PromptEvaluator(max_concurrent_tasks=5)
```

Start with a low concurrency value (like `3`) to avoid rate limit errors.

### Generating Test Data

The evaluation system can automatically generate test cases based on your prompt requirements. Define the inputs your prompt needs:

```python
dataset = evaluator.generate_dataset(
	task_description="Write a compact, concise 1 day meal plan for a single athlete",
	prompt_inputs_spec={
		"height": "Athlete's height in cm",
		"weight": "Athlete's weight in kg", 
		"goal": "Goal of the athlete",
		"restrictions": "Dietary restrictions of the athlete"
	},
	output_file="dataset.json",
	num_cases=3
)
```

Keep test cases low (2–3) during development to speed iteration. Increase for final validation.

### Writing an Initial Prompt

Start with a simple, naive prompt to establish a baseline. Example:

```python
def run_prompt(prompt_inputs):
	prompt = f"""
What should this person eat?

- Height: {prompt_inputs["height"]}
- Weight: {prompt_inputs["weight"]}
- Goal: {prompt_inputs["goal"]}
- Dietary restrictions: {prompt_inputs["restrictions"]}
"""
    
	messages = []
	add_user_message(messages, prompt)
	return chat(messages)
```

This basic prompt will likely produce poor results, but it gives a starting baseline to measure improvements.

### Adding Evaluation Criteria

When running evaluation, specify additional grading criteria:

```python
results = evaluator.run_evaluation(
	run_prompt_function=run_prompt,
	dataset_file="dataset.json",
	extra_criteria="""
The output should include:
- Daily caloric total
- Macronutrient breakdown
- Meals with exact foods, portions, and timing
"""
)
```

This ensures the grading model scores outputs against the requirements that matter.

## Analyzing Results

After evaluation you'll get numerical scores and a detailed HTML report showing per-case performance and grader reasoning. Use the report to identify failures and guide the next iteration.

Don't be discouraged by low initial scores — a low score is expected for a first attempt. The goal is consistent improvement.

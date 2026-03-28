# Prompt Evaluation — Simple 5‑Step Workflow

Use this short, practical workflow to test and improve prompts quickly.

## The 5 steps (simple)

1) Draft a prompt

Example (baseline):

```text
Please answer the user's question:

{question}
```

2) Build a small eval dataset

Collect a handful of representative inputs — include common cases, edge cases, and at least one adversarial example.

Example dataset:

- "What's 2+2?"
- "How do I make oatmeal?"
- "How far away is the Moon?"

3) Run each input through Claude

For every question, merge it into the prompt template, send it to Claude, and save the response.

4) Grade the responses

Score each reply (automatically or by hand) from 1–10. Compute the average to get a baseline score.

Example scores:

- Math: 10
- Oatmeal: 4
- Moon distance: 9

Average = (10 + 4 + 9) / 3 = 7.66

5) Improve the prompt and repeat

Change the prompt, re-run the same dataset, and compare scores. Keep the change small so you can see its effect.

Example improved prompt:

```text
Please answer the user's question. Give an accurate, clear, and complete response.

{question}
```

If the new average rises (e.g., 8.7), the change likely helped.

## Quick pseudo-code

```python
questions = ["What's 2+2?", "How do I make oatmeal?", "How far away is the Moon?"]
def evaluate(prompt_template, questions):
    scores = []
    for q in questions:
        prompt = prompt_template.format(question=q)
        response = client.chat.create(prompt=prompt, temperature=0)
        score = grader(q, response.text)  # 1..10
        scores.append(score)
    return sum(scores)/len(scores)

baseline = evaluate(baseline_prompt, questions)
improved = evaluate(improved_prompt, questions)
print(baseline, improved)
```

## Fast tips

- Use `temperature=0` for deterministic extraction tasks.
- Add validators (JSON Schema, regex) to catch parse errors automatically.
- Log inputs and outputs so you can reproduce failures.
- Start small (dozens of examples), then scale the dataset.

## Next steps

- Create a small test harness that runs prompts and validators.
- Store prompts and tests in version control.
- Integrate evaluation into CI for PR checks when ready.

That's it — a simple loop: draft, test, score, improve, repeat.

## Graders — simple guide

A grader assigns a numeric score (1–10) and optional reasoning about output quality. Use one of:

- **Code grader:** programmatic checks (JSON parse, length, regex, syntax). Fast and deterministic.
- **Model grader:** ask a model to judge usefulness, completeness, or style. Flexible but can vary.
- **Human grader:** people rate outputs; most reliable but slow and costly.

Simple model grader (pseudo-code)

```python
def grade_by_model(task, solution):
    eval_prompt = f"""You are an expert reviewer.

Task:
{task}

Solution:
{solution}

Reply with a JSON object exactly like:
{"score": <1-10>, "reasoning": "short explanation"}
"""
    resp = client.chat.create(prompt=eval_prompt, temperature=0)
    return json.loads(resp.text)
```

Integrate into your runner:

```python
def run_test_case(test_case):
    output = run_prompt(test_case)
    grade = grade_by_model(test_case, output)
    return {"output": output, "score": grade["score"], "reasoning": grade.get("reasoning")}

def run_eval(dataset):
    results = [run_test_case(tc) for tc in dataset]
    avg = mean([r["score"] for r in results])
    print("Average score:", avg)
    return results
```

Tips:

- Ask the grader to return strict JSON to simplify parsing.
- Use `temperature=0` for repeatable evaluations.
- Combine a code grader with a model grader for best coverage (fast checks + judgment).

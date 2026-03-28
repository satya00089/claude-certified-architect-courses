import json
from statistics import mean

import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "claude-haiku-4-5"
client = Anthropic()


def add_user_message(messages, text):
    """Helper to add a user message to the conversation."""
    messages.append({"role": "user", "content": text})


def add_assistant_message(messages, text):
    """Helper to add an assistant message to the conversation."""
    messages.append({"role": "assistant", "content": text})


def chat(
    messages,
    system=None,
    temperature=1.0,
    stop_sequences=None,
    model=DEFAULT_MODEL,
    max_tokens=1000,
):
    """Helper to send a chat request to the model."""
    if stop_sequences is None:
        stop_sequences = []

    params = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }

    if system:
        params["system"] = system

    resp = client.messages.create(**params)
    try:
        return resp.content[0].text
    except Exception as e:
        return str(resp)


def run_prompt(test_case, model=None, temperature=1.0, max_tokens=1000):
    """Run the prompt for a given test case and return the output."""
    prompt = f"""
Please solve the following task:

{test_case['task']}
"""

    messages = []
    add_user_message(messages, prompt)
    return chat(
        messages,
        model=model or DEFAULT_MODEL,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def grade_by_model(test_case, output, model=None, max_tokens=1000):
    """Grade the model's output for a given test case."""
    eval_prompt = f"""
You are an expert AWS code reviewer. Your task is to evaluate the following AI-generated solution.

Original Task:
<task>
{test_case['task']}
</task>

Solution to Evaluate:
<solution>
{output}
</solution>

Output Format
Provide your evaluation as a structured JSON object with the following fields, in this specific order:
- "strengths": An array of 1-3 key strengths
- "weaknesses": An array of 1-3 key areas for improvement
- "reasoning": A concise explanation of your overall assessment
- "score": A number between 1-10

Respond with JSON. Keep your response concise and direct.
"""

    messages = []
    add_user_message(messages, eval_prompt)
    add_assistant_message(messages, "```json")
    eval_text = chat(
        messages,
        stop_sequences=["```"],
        model=model or DEFAULT_MODEL,
        max_tokens=max_tokens,
    )
    try:
        return json.loads(eval_text)
    except Exception as e:
        return {
            "error": "failed to parse eval output",
            "raw": eval_text,
            "exception": str(e),
        }


def run_test_case(test_case, model=None, temperature=1.0, max_tokens=1000):
    """Run a single test case end-to-end: get model output and grade it."""
    output = run_prompt(
        test_case, model=model, temperature=temperature, max_tokens=max_tokens
    )
    model_grade = grade_by_model(test_case, output, model=model, max_tokens=max_tokens)
    score = model_grade.get("score") if isinstance(model_grade, dict) else None
    reasoning = model_grade.get("reasoning") if isinstance(model_grade, dict) else None
    return {
        "output": output,
        "test_case": test_case,
        "score": score,
        "reasoning": reasoning,
        "grade_raw": model_grade,
    }


def run_eval(dataset, model=None, temperature=1.0, max_tokens=1000):
    """Run evaluation on a dataset of test cases."""
    results = []
    for test_case in dataset:
        results.append(
            run_test_case(
                test_case, model=model, temperature=temperature, max_tokens=max_tokens
            )
        )
    numeric_scores = [
        r.get("score") for r in results if isinstance(r.get("score"), (int, float))
    ]
    average_score = mean(numeric_scores) if numeric_scores else None
    return results, average_score


def generate_dataset(model=None, max_tokens=1000):
    """Generate a dataset for prompt evaluation."""
    prompt = """
Generate a evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
each representing task that requires Python, JSON, or a Regex to complete.

Example output:
```json
[
    {
        "task": "Description of task",
        "format": "json" or "python" or "regex"
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
    text = chat(
        messages,
        stop_sequences=["```"],
        model=model or DEFAULT_MODEL,
        max_tokens=max_tokens,
    )
    try:
        return json.loads(text)
    except Exception as e:
        return {
            "error": "failed to parse generated dataset",
            "raw": text,
            "exception": str(e),
        }


def main():
    """Streamlit app for model-based grading."""
    st.set_page_config(page_title="Model-Based Grading")
    st.title("Model-Based Grading — Prompt Evaluation")

    model = st.selectbox(
        "Model", [DEFAULT_MODEL, "claude-sonnet-4-0", "claude-instant"], index=0
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 1.0, step=0.05)
    max_tokens = st.slider("Max tokens", 100, 4000, 1000, step=50)

    st.markdown(
        "Load `dataset.json` (must be in the same folder) or generate a small dataset."
    )

    dataset = None
    if st.checkbox("Load dataset.json from workspace", value=True):
        try:
            with open("dataset.json", "r", encoding="utf-8") as f:
                dataset = json.load(f)
            st.success(f"Loaded {len(dataset)} test cases from dataset.json")
        except Exception as e:
            st.error(f"Failed to load dataset.json: {e}")

    if st.button("Generate dataset using the model"):
        with st.spinner("Generating dataset..."):
            created = generate_dataset(model=model, max_tokens=max_tokens)
            if created:
                dataset = created
                try:
                    with open("dataset.json", "w", encoding="utf-8") as f:
                        json.dump(dataset, f, indent=2)
                    st.success("Generated dataset saved to dataset.json")
                except Exception as e:
                    st.warning("Generated dataset (not saved to disk)")
            else:
                st.error("Failed to generate dataset")

    if not dataset:
        st.info(
            "No dataset loaded. Generate or add a dataset.json file in this folder."
        )
        return

    st.markdown("---")
    st.subheader("Run a single test case")
    idx = st.selectbox(
        "Select test case",
        list(range(len(dataset))),
        format_func=lambda i: f"#{i} - {dataset[i].get('format', '')}",
    )
    test_case = dataset[idx]
    st.json(test_case)
    # Initialize storage for last run/grade so we can display full-width below
    if "mbg_last_output" not in st.session_state:
        st.session_state["mbg_last_output"] = None
    if "mbg_last_grade" not in st.session_state:
        st.session_state["mbg_last_grade"] = None

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Run prompt for selected case"):
            with st.spinner("Running model..."):
                try:
                    out = run_prompt(
                        test_case,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    st.session_state["mbg_last_output"] = out
                    st.session_state["mbg_last_grade"] = None
                    st.success("Run complete")
                except Exception as e:
                    st.error(f"Run error: {e}")
    with col2:
        if st.button("Grade selected output"):
            with st.spinner("Grading output..."):
                try:
                    # run the prompt first to get output, then grade
                    output = run_prompt(
                        test_case,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    grade = grade_by_model(
                        test_case, output, model=model, max_tokens=max_tokens
                    )
                    st.session_state["mbg_last_output"] = output
                    st.session_state["mbg_last_grade"] = grade
                except Exception as e:
                    st.error(f"Grading error: {e}")
    with col3:
        if st.button("Run and grade selected case"):
            with st.spinner("Running and grading..."):
                try:
                    out = run_prompt(
                        test_case,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    grade = grade_by_model(
                        test_case, out, model=model, max_tokens=max_tokens
                    )
                    st.session_state["mbg_last_output"] = out
                    st.session_state["mbg_last_grade"] = grade
                except Exception as e:
                    st.error(f"Error: {e}")

    # Display last run/grade full-width below the action buttons
    if st.session_state.get("mbg_last_output"):
        st.markdown("---")
        st.subheader("Model output")
        st.code(st.session_state.get("mbg_last_output"))

    if st.session_state.get("mbg_last_grade") is not None:
        grade = st.session_state.get("mbg_last_grade")
        st.subheader("Grade")
        if isinstance(grade, dict) and "error" not in grade:
            # Try to parse numeric score and show it prominently
            score = grade.get("score")
            numeric_score = None
            if isinstance(score, (int, float)):
                numeric_score = score
            else:
                try:
                    numeric_score = float(score)
                except Exception:
                    numeric_score = None

            if numeric_score is not None:
                # display as a prominent metric (rounded to 2 decimals)
                try:
                    st.metric("Score", round(numeric_score, 2))
                except Exception:
                    st.markdown(f"**Score:** {numeric_score}")
            else:
                # fall back to text if no parsable numeric score
                st.markdown(f"**Score:** {score}")

            # show full structured grade below
            st.json(grade)
        else:
            st.error(f"Grading failed: {grade}")

    st.markdown("---")
    st.subheader("Run full evaluation")
    if st.button("Run evaluation for all test cases"):
        with st.spinner("Running evaluation for all cases..."):
                try:
                    results, avg = run_eval(
                        dataset, model=model, temperature=temperature, max_tokens=max_tokens
                    )
                    # Show average score prominently when numeric
                    if isinstance(avg, (int, float)):
                        st.success("Completed.")
                        try:
                            st.metric("Average score", round(avg, 2))
                        except Exception:
                            st.markdown(f"**Average score:** {avg}")
                    else:
                        st.success(f"Completed. Average score: {avg}")

                    st.download_button(
                        "Download results as JSON",
                        json.dumps(results, indent=2),
                        file_name="evaluation_results.json",
                    )
                    st.write(results)
                except Exception as e:
                    st.error(f"Evaluation error: {e}")


if __name__ == "__main__":
    main()

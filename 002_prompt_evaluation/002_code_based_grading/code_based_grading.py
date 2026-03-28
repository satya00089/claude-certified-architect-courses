import os
import json
import re
import ast
import time
from dotenv import load_dotenv
import streamlit as st
from anthropic import Anthropic


load_dotenv()

# Central constant for dataset filename used in multiple places
DATASET_FILENAME = "dataset.json"

client = Anthropic()

def add_user_message(messages, text):
    """Helper to add a user message to the conversation."""
    messages.append({"role": "user", "content": text})


def add_assistant_message(messages, text):
    """Helper to add an assistant message to the conversation."""
    messages.append({"role": "assistant", "content": text})


def chat(client, messages, model, system=None, temperature=1.0, stop_sequences=None):
    """Helper to send a chat message to the model and receive a response."""
    if stop_sequences is None:
        stop_sequences = []
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }
    if system:
        params["system"] = system
    resp = client.messages.create(**params)
    try:
        return resp.content[0].text
    except Exception:
        if isinstance(resp, str):
            return resp
        return json.dumps(resp, default=str)


def run_prompt(client, model, test_case, temperature=1.0):
    """Run the model on a single test case, returning the raw output."""
    prompt = f"""Please solve the following task:

{test_case['task']}

* Respond only with Python, JSON, or a plain Regex
* Do not add any comments or commentary or explanation
"""
    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```code")
    return chat(
        client, messages, model, temperature=temperature, stop_sequences=["```"]
    )


def validate_json(text):
    """Check if the text is valid JSON."""

    try:
        json.loads(text.strip())
        return 10
    except Exception:
        return 0


def validate_python(text):
    """Use ast to check if the code is syntactically valid Python."""
    try:
        ast.parse(text.strip())
        return 10
    except Exception:
        return 0


def validate_regex(text):
    """A very basic check to see if the regex compiles."""
    try:
        re.compile(text.strip())
        return 10
    except Exception:
        return 0


def grade_syntax(response, test_case):
    """Grade the syntax of the response based on the expected format."""
    fmt = test_case.get("format", "python")
    if fmt == "json":
        return validate_json(response)
    elif fmt == "python":
        return validate_python(response)
    else:
        return validate_regex(response)


def grade_by_model(client, model, test_case, output, temperature=1.0):
    """Use the model itself to grade the output, returning a structured JSON evaluation."""
    eval_prompt = f"""You are an expert AWS code reviewer. Your task is to evaluate the following AI-generated solution.

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
        client, messages, model, temperature=temperature, stop_sequences=["```"]
    )
    try:
        return json.loads(eval_text)
    except Exception:
        return {"strengths": [], "weaknesses": [], "reasoning": eval_text, "score": 1}


def run_test_case(client, model, test_case, temperature=1.0):
    """Run a single test case and return the results."""
    output = run_prompt(client, model, test_case, temperature=temperature)
    model_grade = grade_by_model(
        client, model, test_case, output, temperature=temperature
    )
    model_score = model_grade.get("score", 0)
    reasoning = model_grade.get("reasoning", "")
    syntax_score = grade_syntax(output, test_case)
    score = (model_score + syntax_score) / 2
    return {
        "output": output,
        "test_case": test_case,
        "score": score,
        "reasoning": reasoning,
        "model_grade": model_grade,
        "syntax_score": syntax_score,
    }


def run_eval(client, model, dataset, temperature=1.0, progress_callback=None):
    """Run evaluation on the entire dataset, calling the model for each test case."""
    results = []
    for i, test_case in enumerate(dataset):
        result = run_test_case(client, model, test_case, temperature=temperature)
        results.append(result)
        if progress_callback:
            progress_callback(i + 1, len(dataset))
        time.sleep(0.3)
    return results


def find_local_dataset():
    """Look for the dataset file in common locations."""
    candidates = [
        os.path.join(
            os.getcwd(), "prompt-evaluation", "002_code_based_grading", DATASET_FILENAME
        ),
        os.path.join(os.getcwd(), DATASET_FILENAME),
        DATASET_FILENAME,
    ]
    for p in candidates:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return None


def main():
    """Streamlit app for code-based prompt evaluation."""
    st.set_page_config(page_title="Code-based Grader")
    st.title("Code-based Prompt Evaluation")
    with st.expander("Dataset format & example", expanded=True):
        st.markdown("Dataset must be a JSON array of objects. Required fields:")
        st.markdown("- `task`: string — the instruction to solve.")
        st.markdown("- `format`: string — one of `json`, `python`, or `regex`.")
        st.markdown("Optional fields: `id` (string/number), `notes` (string).")
        example = [
            {
                "task": "Return a JSON object describing an S3 bucket policy that allows public GetObject access for objects under the bucket.",
                "format": "json",
            },
            {
                "task": "Write a Python function list_s3_keys(bucket) that returns a list of object keys for the given S3 bucket using boto3.",
                "format": "python",
            },
            {
                "task": "Provide a regex that matches a simple AWS ARN (for example: starts with arn:aws: then service, region, account, resource).",
                "format": "regex",
            },
        ]
        st.code(json.dumps(example, indent=2), language="json")
        st.markdown(
            f"Save this as `{DATASET_FILENAME}` and either upload it here or place it next to the app before launching."
        )

    st.sidebar.header("Settings")
    default_model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")
    model = st.sidebar.text_input("Model", value=default_model)
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 1.0, 0.05)
    st.sidebar.markdown("Ensure ANTHROPIC_API_KEY is set in your environment.")

    uploaded_file = st.file_uploader(f"Upload {DATASET_FILENAME}", type=["json"])
    dataset = None
    if uploaded_file is not None:
        try:
            dataset = json.load(uploaded_file)
        except Exception as e:
            st.error(f"Failed to parse uploaded JSON: {e}")

    if dataset is None:
        dataset = find_local_dataset()

    if not dataset:
        st.warning(
            "No dataset found. Upload a dataset.json or generate one with the notebook."
        )
        return

    st.write(f"Loaded dataset with {len(dataset)} items")

    idx = st.selectbox(
        "Select test case",
        list(range(len(dataset))),
        format_func=lambda i: dataset[i].get("task", "")[:120],
    )

    if st.button("Run selected test case"):
        with st.spinner("Running model..."):
            try:
                result = run_test_case(
                    client, model, dataset[idx], temperature=temperature
                )
            except Exception as e:
                st.error(f"Error calling model: {e}")
                return
        st.subheader("Model Output")
        fmt = dataset[idx].get("format", "python")
        lang = "python" if fmt == "python" else None
        st.code(result["output"], language=lang)
        st.markdown(f"**Score:** {result['score']}")
        st.markdown("**Model evaluation (raw):**")
        st.json(result["model_grade"])

    confirm_full = st.checkbox("I understand this will make one API call per test case")
    if st.button("Run full evaluation (calls API for each item)"):
        if not confirm_full:
            st.warning(
                "Please confirm you understand the API cost/usage by checking the box."
            )
        else:
            progress = st.progress(0)

            def progress_cb(done, total):
                progress.progress(int(done / total * 100))

            with st.spinner("Running full evaluation..."):
                results = run_eval(
                    client,
                    model,
                    dataset,
                    temperature=temperature,
                    progress_callback=progress_cb,
                )
            st.success("Finished evaluation")
            st.write(
                f"Average score: {sum(r['score'] for r in results)/len(results):.2f}"
            )
            st.download_button(
                "Download results",
                data=json.dumps(results, indent=2),
                file_name="results.json",
                mime="application/json",
            )


if __name__ == "__main__":
    main()

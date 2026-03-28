from textwrap import dedent
import json
import re
import os
from dotenv import load_dotenv
import streamlit as st
from anthropic import Anthropic

load_dotenv()
client = Anthropic()
DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5")


def chat(
    messages, model=DEFAULT_MODEL, temperature=0.7, max_tokens=800, stop_sequences=None
):
    """Helper function to call the Anthropic API with a chat conversation."""
    if stop_sequences is None:
        stop_sequences = []

    params = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }
    res = client.messages.create(**params)
    try:
        return res.content[0].text
    except Exception:
        return str(res)


def extract_json(text):
    """Extract the first JSON object or array from a string, if any."""
    starts = [i for i in (text.find("{"), text.find("[")) if i != -1]
    if not starts:
        return None
    start = min(starts)
    stack = []
    for i in range(start, len(text)):
        c = text[i]
        if c in "{[":
            stack.append(c)
        elif c in "}]":
            if not stack:
                continue
            stack.pop()
            if not stack:
                candidate = text[start : i + 1].strip()
                candidate = re.sub(r"```(?:json)?\n?|```", "", candidate).strip()
                try:
                    return json.loads(candidate)
                except Exception:
                    return None
    return None


st.set_page_config(page_title="Prompting Explorer")
st.title("Prompting Explorer — quick prompt tester")

user_model = st.selectbox(
    "Model", [DEFAULT_MODEL, "claude-sonnet-4-0", "claude-instant"], index=0
)
temperature = st.slider("Temperature", 0.0, 1.5, 0.7, step=0.1)

tabs = st.tabs(["Run Prompt", "Generate Test Case"])

with tabs[0]:
    st.header("Run an arbitrary prompt")
    prompt = st.text_area("Prompt", height=260)
    if st.button("Send prompt"):
        with st.spinner("Calling model..."):
            try:
                messages = [{"role": "user", "content": prompt}]
                out = chat(messages, model=user_model, temperature=temperature)
                st.subheader("Model response")
                st.code(out)
            except Exception as e:
                st.error(f"Error calling model: {e}")

with tabs[1]:
    st.header("Generate a single JSON test case")
    task_desc = st.text_input(
        "Task description",
        "Write a compact, concise 1 day meal plan for a single athlete",
    )
    prompt_inputs = st.text_area(
        "Prompt inputs (JSON mapping key → description)",
        value='{"height":"Athlete height in cm","weight":"Athlete weight in kg","goal":"Goal","restrictions":"Dietary restrictions"}',
        height=180,
    )
    if st.button("Generate test case"):
        try:
            spec = json.loads(prompt_inputs)
        except Exception as e:
            st.error(f"Invalid JSON for prompt inputs: {e}")
            spec = None

        if spec:
            example_inputs = ", ".join([f'"{k}": "EXAMPLE_VALUE"' for k in spec.keys()])
            allowed_keys = ", ".join([f'"{k}"' for k in spec.keys()])
            rendered = dedent(
                f"""
            Generate a single detailed test case for a prompt evaluation based on:

            <task_description>
            {task_desc}
            </task_description>

            Allowed input keys:
            {allowed_keys}

            Output only a JSON object with the following keys:
            - prompt_inputs (an object using the allowed keys)
            - solution_criteria (an array of concise evaluation criteria)

            Example output format:
            ```json
            {{
                "prompt_inputs": {{
                    {example_inputs}
                }},
                "solution_criteria": ["criterion 1", "criterion 2"]
            }}
            ```
            """
            )

            try:
                messages = [{"role": "user", "content": rendered}]
                raw = chat(
                    messages, model=user_model, temperature=0.7, stop_sequences=["```"]
                )
                parsed = extract_json(raw)
                if parsed is None:
                    st.warning(
                        "Could not parse JSON from model response — showing raw output below."
                    )
                    st.code(raw)
                else:
                    st.subheader("Generated test case")
                    st.json(parsed)
            except Exception as e:
                st.error(f"Anthropic API error: {e}")

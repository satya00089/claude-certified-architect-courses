# Prompting examples — Prompt evaluator and Streamlit quick UI

This folder contains an interactive notebook (`prompting.ipynb`) that implements a `PromptEvaluator` for generating and grading prompt-evaluation test cases. To make experimentation easier, there is a lightweight Streamlit app that lets you run arbitrary prompts and generate a single JSON test case from a task description and input spec.

Files added
- `prompting.ipynb` — notebook with `PromptEvaluator`, dataset generation and evaluation flows.
- `prompting_streamlit.py` — lightweight Streamlit UI for quick interactive testing.

Prerequisites
- Python 3.8 or newer
- A virtual environment (recommended)
- Set your Anthropic API key in the environment variable `ANTHROPIC_API_KEY`

Quick start
1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install required packages:

```powershell
pip install streamlit anthropic python-dotenv
```

3. Run the Streamlit app:

```powershell
streamlit run prompting_streamlit.py
```

What the Streamlit app does
- `Run Prompt`: send an arbitrary prompt to Claude and see the raw reply.
- `Generate Test Case`: provide a task description and a JSON spec of allowed input keys; the app asks Claude to return a single test case in JSON and attempts to parse/display it.

Notes
- The Streamlit app is intentionally minimal — the notebook contains the fuller `PromptEvaluator` implementation and evaluation pipeline.
- Do not commit your API key. Use environment variables or a local `.env` file and add `.env` to `.gitignore`.

If you'd like I can:
- Run a smoke test of the Streamlit app locally.
- Add a consolidated `requirements.txt` for this folder.

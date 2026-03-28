
# Accessing Claude with the API — What to expect

This folder contains short, self-contained examples that demonstrate how to call Anthropic's Claude models from Python. The examples cover a range of common patterns: direct request examples, multi-turn conversation handling, Streamlit demos, Jupyter notebooks, and small exercises exploring system prompts, temperature, streaming, and structured outputs.

What you'll find
- `001_requests/` — simple Python script and notebook showing basic request/response usage (`claude_requests.py`, `requests.ipynb`).
- `002_multi_turn_conversations/` — Streamlit demo showing how to maintain conversation state across turns (uses `st.session_state`).
- `003_chat_exercise/` — a short chat exercise and solution files.
- `004_system_prompts/` — experiments with system/instruction prompts and how they affect responses.
- `005_system_prompts_exercise/` — an exercise notebook for system prompts.
- `006_temperature/` — examples that demonstrate the effect of the `temperature` parameter on outputs.
- `007_streaming/` — examples that demonstrate streaming responses where supported.
- `008_structured_data/` — examples that ask Claude to produce structured (JSON-like) outputs and a small UI demo.

Prerequisites
- Python 3.8 or newer.
- A virtual environment (recommended).
- An Anthropic API key available as the environment variable `ANTHROPIC_API_KEY` (examples use the `anthropic` Python package).

Quick start
1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies for the example you want to run (each subfolder contains a `requirements.txt`):

```powershell
pip install -r 001_requests/requirements.txt
```

3. Set your Anthropic API key (one-time, or set for the current session):

```powershell
setx ANTHROPIC_API_KEY "your_api_key_here"
# OR for the current PowerShell session only:
$env:ANTHROPIC_API_KEY = "your_api_key_here"
```

4. Run an example:

- Raw request example:

```powershell
python 001_requests/claude_requests.py
```

- Streamlit multi-turn demo:

```powershell
pip install -r 002_multi_turn_conversations/requirements.txt
streamlit run 002_multi_turn_conversations/multi_turn_conversations.py
```

- Open a notebook in your browser:

```powershell
pip install notebook
jupyter notebook 001_requests/requests.ipynb
```

What to expect when you run the examples
- Script outputs: concise Claude replies printed to stdout or returned as JSON.
- Streamlit demos: an interactive browser UI that preserves conversation history and shows model replies.
- Notebooks: step-by-step examples with explanatory text and sample outputs.
- Temperature/streaming experiments: observable changes in creativity, determinism, or partial/streamed output behavior.
- Structured-data examples: Claude returns JSON-like objects or text that can be parsed into structured data.

Security & costs
- Do not commit API keys to source control. Use environment variables or a local `.env` file (and add it to `.gitignore`).
- Running examples consumes model tokens; monitor your usage and costs.



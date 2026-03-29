# Extended Thinking demo (Claude Anthropic)

This folder contains the `thinking.ipynb` notebook that demonstrates Anthropic's
extended "thinking" feature (redacted inner thoughts), plus a Streamlit demo
app that reproduces the notebook's interactive flow.

Contents
- `thinking.ipynb` — main notebook demonstrating how to enable thinking in the
  Anthropic SDK.
- `streamlit_app.py` — small Streamlit app to interact with the same chat flow.
- `requirements.txt` — minimal packages needed to run the notebook and app.

Features
- Load environment variables with `python-dotenv` and create an Anthropic client.
- Helper functions: `add_user_message`, `add_assistant_message`, `chat`, and
  `text_from_message`.
- Demonstrates `thinking=True` with configurable `thinking_budget` and a magic
  trigger string to show redacted thinking behavior.

Prerequisites
- Python 3.8+
- A valid Anthropic API key set in a `.env` file (e.g., `ANTHROPIC_API_KEY=...`).

Quickstart
1. Create and activate a virtual environment:

```
python -m venv .venv
.venv\\Scripts\\activate
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Run the notebook or start the Streamlit demo:

```
jupyter notebook thinking.ipynb
# or
streamlit run streamlit_app.py
```

Notes
- The notebook and app assume the Anthropic SDK's `client.messages.create(...)`
  interface used in the notebook. Confirm your installed SDK version matches.
- Place API keys and any config in `.env`. The Streamlit app will raise an error
  if the Anthropic client cannot be created.

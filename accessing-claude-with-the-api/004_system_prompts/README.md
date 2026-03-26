# System Prompts — Streamlit Playground

This folder demonstrates using a system prompt with the Claude-style messages API and includes a small Streamlit playground to experiment interactively.

## What is a system prompt?
A system prompt sets the assistant's behavior (tone, role, constraints). In this course we use it to guide Claude to act as a patient math tutor that guides students step-by-step rather than directly giving answers.

## Files
- `system_prompts.ipynb` — Example notebook showing helper functions and usage.
- `streamlit_app.py` — Small Streamlit app to interactively edit the system prompt and send messages.
- `requirements.txt` — Python dependencies.
- `.env.example` — Example env file (rename to `.env` and set your API key locally).

## Setup
1. Copy the example env and add your Anthropic API key (do NOT commit your `.env`):

```bash
cp .env.example .env
# then edit .env and set ANTHROPIC_API_KEY
```

2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Run the Streamlit playground:

```bash
streamlit run streamlit_app.py
```

## How to use the playground
- Paste your API key in the sidebar (or ensure `ANTHROPIC_API_KEY` is set in `.env`).
- Edit the system prompt text area to change the assistant's behavior.
- Type a user message and press **Send** to call the API.
- The UI shows the assistant response and a payload preview.

## Notes
- Keep your real API key private; do not commit `.env` to the repository.
- `anthropic` is used in the same message-based style as the notebook. If SDK signatures differ in your installed version, adapt the client construction accordingly in `streamlit_app.py`.

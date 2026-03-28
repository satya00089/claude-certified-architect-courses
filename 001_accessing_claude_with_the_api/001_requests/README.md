Claude Requests Streamlit app

Overview
--------
This small Streamlit app demonstrates how to make requests to the Anthropic (Claude) API from Python. It includes a simple UI for entering prompts, selecting a model, and viewing Claude's response. The README explains the environment setup, the key API function, message structure, and how the example code works.

Setting up your environment
---------------------------
1. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# or cmd
.\.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install streamlit anthropic python-dotenv
```

3. Copy `.env.example` to `.env` and set your Anthropic API key:

```bash
copy .env.example .env
# then edit .env and set ANTHROPIC_API_KEY
```

Make sure `.env` is listed in `.gitignore` so you don't accidentally commit secrets.

How the code is organized
-------------------------
- `claude_requests.py` — Streamlit app that:
	- loads environment variables with `python-dotenv`;
	- creates an `Anthropic` client instance;
	- provides UI controls for model, prompt, and max tokens;
	- sends a request using `client.messages.create(...)` and displays the response.
- `.env.example` — example environment file with `ANTHROPIC_API_KEY` placeholder.

Making your first request (theory)
---------------------------------
Making a request to Claude centers on the `client.messages.create()` function. The three most important parameters are:

- `model` — the name of the Claude model to use (for example `claude-sonnet-4-0`).
- `max_tokens` — an upper safety limit for the response length (not a target).
- `messages` — a list of message dictionaries that represent the conversation history.

The `max_tokens` parameter is a safety limit; Claude will stop if it reaches that many tokens, but it does not try to exactly hit the number.

Messages and conversation structure
----------------------------------
Messages are dictionaries with two keys:

- `role`: either `"user"` or `"assistant"`.
- `content`: the text content of the message.

Example single-turn request:

```python
message = client.messages.create(
		model=model,
		max_tokens=1000,
		messages=[
				{"role": "user", "content": "What is quantum computing? Answer in one sentence"}
		]
)
```

Extracting the response
-----------------------
The returned `message` (response) object contains metadata and generated content. In most cases you want the generated text, which is available as:

```python
message.content[0].text
```

This gives you a readable string such as: "Quantum computing is a type of computation that leverages quantum mechanics..."

Streamlit-specific notes
------------------------
- The app uses `st.text_area` for the prompt and `st.slider` for `max_tokens`.
- Error handling in the example code uses explicit exception types rather than a broad `except Exception` so errors from the API or networking are surfaced cleanly.

Run the Streamlit app
----------------------
From the `001_requests` folder run:

```bash
streamlit run claude_requests.py
```

Try different prompts and models. Remember to keep your API key private and never commit `.env` to version control.

Further experimentation
----------------------
- Convert the notebook examples into small scripts or a web UI (this repo shows both).
- Add logging, rate limiting, or retries for production usage.
- For multi-turn conversations, maintain a `messages` list and send the full history on each request — see the `002_multi_turn_conversations` example.

License / Security
------------------
- Do not share your API key. If it is compromised, rotate it immediately.
- This example is provided for educational use.

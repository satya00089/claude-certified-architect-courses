Claude Requests Streamlit app

Overview
--------
This folder shows how to maintain conversation context (multi-turn dialogs) when using the Anthropic API. The Streamlit example `multi_turn_conversations.py` demonstrates a simple UI with a toggle to enable/disable multi-turn mode and `st.session_state` to persist the message history across interactions.

Why multi-turn matters
----------------------
Stateless requests (where each request contains only the current user prompt) lose context between turns. To make follow-up prompts meaningful you must include the relevant conversation history with your request so Claude can reference previous messages.

Setup
-----
Same as the other example:

```bash
pip install streamlit anthropic python-dotenv
copy .env.example .env
# edit .env and set ANTHROPIC_API_KEY
```

How the Streamlit example works
-------------------------------
- A `checkbox` labeled "Enable multi-turn (keep conversation history)" toggles whether the app will maintain a `messages` list in `st.session_state`.
- When multi-turn is enabled:
	- the app appends the user's message to `st.session_state.messages`;
	- it sends the entire `messages` list to `client.messages.create(...)`;
	- it takes Claude's reply and appends it as an assistant message to `st.session_state.messages` so the next request includes both user and assistant history.
- A `Reset conversation` button clears `st.session_state.messages`.

Key helper functions (in the example)
-------------------------------------
- `add_user_message(messages, text)` — append a user message dict to the history.
- `add_assistant_message(messages, text)` — append an assistant message dict.
- `chat(messages)` — wrapper that calls `client.messages.create(...)` with the provided messages list and returns the raw response.

Example flow
------------
1. Add: `{"role": "user", "content": "Define cloud computing in one sentence"}`
2. Send to Claude; save reply as assistant message
3. Add follow-up user message: `"Write another sentence"`
4. Send full history; Claude replies with context-aware continuation

Run the Streamlit app
---------------------
From this folder run:

```bash
streamlit run multi_turn_conversations.py
```

Notes and next steps
--------------------
- Showing the full message list in the UI can help debug conversation state.
- In production, limit history length (e.g., trim old messages) to control token usage.
- Consider serializing/persisting longer histories for longer sessions or cross-device continuity.

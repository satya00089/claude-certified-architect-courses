## Current Datetime — Streamlit Demo

**Overview:**
- **Purpose:**: Small Streamlit app that returns the current date/time in a user-specified format. It supports two modes: local Python formatting or an Anthropic (Claude) tool flow demonstration.

**Files:**
- **App:**: `streamlit_app.py` — Streamlit UI and logic for Local / Anthropic modes.
- **Dependencies:**: `requirements.txt` — packages required to run the demo.
- **Notebook:**: `current_datetime.ipynb` — original notebook used to experiment with the Anthropic tool flow.

**Quick Start**

1. Create (optional) and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
.venv\Scripts\Activate.ps1  # Windows PowerShell
```

2. Install dependencies:

```bash
pip install -r 004_tools/001_current_datetime/requirements.txt
```

3. Run the Streamlit app from the repository root:

```bash
streamlit run 004_tools/001_current_datetime/streamlit_app.py
```

**Using the app**

- **Date format:** Enter any Python `datetime.strftime` format (e.g. `%Y-%m-%d %H:%M`).
- **Source:** Choose `Local (Python)` to compute locally or `Anthropic Claude` to demonstrate the tool flow with Claude.
- **Anthropic mode:** If selected, the app will call the Anthropic API and, when Claude requests the tool, respond with a `tool_result` block containing the computed datetime.
- **Show raw:** Toggle to inspect the raw API response returned by the SDK.

**Anthropic / API notes**

- The Anthropic flow in this demo uses the `ToolParam` schema and the `messages.create` API. When responding with a tool result, the allowed fields for the `tool_result` block are limited. The API expects only the following fields in the tool-result block:
  - `type` (should be `tool_result`)
  - `tool_use_id` (the id from the model's tool-use request)
  - `content` (the tool return value)

- Extra fields (e.g., `isError`, `is_error`, or other custom fields) will cause a 400 Bad Request. If you see errors like `Extra inputs are not permitted`, check that your `tool_result` blocks contain only the three allowed fields above.

- Ensure your Anthropic API key is available as `CLAUDE_API_KEY` in the environment or in a `.env` file at the project root. Example `.env`:

```
CLAUDE_API_KEY=sk-xxx-your-key-here
```

**Notebook integration**

- The original notebook (`current_datetime.ipynb`) shows how to call `client.messages.create(...)`, inspect `resp.content[0].input`, compute the datetime locally, and then send the `tool_result` back to the model.
- When constructing the assistant message with the tool result, send a message like:

```python
assistant_message = {
    "role": "assistant",
    "content": [{
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": computed_datetime
    }]
}
```

**Troubleshooting**

- 400 error / `Extra inputs are not permitted`: remove any extra keys from the tool result block (e.g., `isError` / `is_error`).
- `Anthropic client not initialized`: ensure `anthropic` is installed and `CLAUDE_API_KEY` is set.

**Next steps / Suggestions**

- I can: run a minimal test locally (if you want me to run commands in your venv), hide the Anthropic option when the client is not configured, or add CI tests. Tell me which you prefer.

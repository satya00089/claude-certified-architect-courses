# Caching — Examples and notes

This folder contains the `caching.ipynb` notebook demonstrating caching and
streaming update patterns when using tool schemas with the Anthropic
messages API. The notebook shows how to pass `tools` to the helper `chat()`
function, how to control caching for specific tools, and how to stream partial
results into a UI.

Quick start

1. Create a `.env` file containing your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-...
```

2. (Optional) Activate your virtual environment.

3. Install dependencies:

```powershell
pip install python-dotenv anthropic
# If you use the streamlit demos elsewhere in this repo, also install streamlit
pip install streamlit
```

4. Open and run the notebook (`caching.ipynb`) in Jupyter Lab/Notebook and run
the cells interactively to explore the examples.

Highlights in this notebook

- Example `chat()` helper that accepts `tools`, `system`, `thinking`, and
  `thinking_budget` parameters.
- Pattern for making a single tool non-cacheable by setting
  `tools_clone[-1]["cache_control"] = {"type": "ephemeral"}`.
- Wrapping a `system` message in a list so you can attach a
  `cache_control` field (shown in the notebook).
- Demonstration of streaming/partial updates to the UI and how to handle
  structured partial responses.

Code snippet (from notebook):

```python
tools = [db_query_schema, add_duration_to_datetime_schema, set_reminder_schema, get_current_datetime_schema]
messages = []
add_user_message(messages, "what's 1+1")
chat(messages, tools=tools)
```

Notes

- If you enable `thinking`, ensure `max_tokens` is larger than
  the `thinking_budget` when making the API call (other demos in this repo
  enforce or adjust `max_tokens` accordingly).
- If you see errors about the Anthropic client, confirm `ANTHROPIC_API_KEY` is
  set in your environment and that the `anthropic` package is installed.

If you'd like, I can also add a small Streamlit demo mirroring the key
cells from `caching.ipynb` (upload/tools UI and streaming updates). Just tell
me whether you want a full demo and I'll add `streamlit_app.py` here.

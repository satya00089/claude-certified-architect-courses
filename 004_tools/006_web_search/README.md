# Web Search Tool

This folder demonstrates how to give the model a **web search tool** — a built-in
Anthropic capability that lets the model query live web content and ground its answers
in up-to-date, cited sources.

## What it is

The `web_search_20250305` tool is a first-party tool type registered directly with the
Anthropic API. Unlike custom tools you implement yourself, you just include the schema in
the `tools` list and the API handles the search transparently — no external search API
key required.

```python
web_search_schema = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 5,                        # limit searches per request
    "allowed_domains": ["nih.gov"],       # optional domain whitelist
}
```

## Key parameters

| Parameter | Purpose |
|-----------|---------|
| `type` | Must be `"web_search_20250305"` — selects the built-in search tool |
| `name` | Tool name the model calls (usually `"web_search"`) |
| `max_uses` | Maximum number of searches the model can make per response |
| `allowed_domains` | Optional whitelist — restricts searches to trusted domains only |
| `blocked_domains` | Optional blacklist — explicitly excluded domains |

## Why you need it

Without web search, the model answers from training data which may be stale or incomplete.
With this tool the model can:

- Retrieve **current information** — news, research, prices, documentation.
- **Cite sources** — ground answers in specific URLs so users can verify.
- **Restrict scope** — pin searches to a trusted domain (e.g. `nih.gov`, `docs.python.org`)
  to avoid misinformation from low-quality results.
- Answer questions that require **combining** multiple live sources.

## How it works

```
User question
      │
      ▼
chat(messages, tools=[web_search_schema])
      │
      ├─ model decides to search ──► Anthropic API issues web query
      │                                        │
      │                              Results injected into context
      │                                        │
      └─ model composes final answer with citations
             │
             ▼
      Response with grounded, cited answer
```

Unlike custom tools, you do **not** implement a `run_tool` function — the API handles the
search roundtrip internally. The model's final message will include cited web content.

## Files

| File | Description |
|------|-------------|
| `web_search.ipynb` | Notebook with basic and domain-restricted search examples |
| `streamlit_app.py` | Interactive **Medical Research Assistant** demo |
| `requirements.txt` | Python dependencies |

## Run the Streamlit demo

```bash
pip install -r 004_tools/006_web_search/requirements.txt
# add ANTHROPIC_API_KEY to a .env file or export it
streamlit run 004_tools/006_web_search/streamlit_app.py
```

The demo is a **Medical Research Assistant** that restricts all searches to `nih.gov`,
so every answer is grounded exclusively in peer-reviewed NIH/PubMed content. You can also
switch to unrestricted mode and supply your own domain allow/block lists.

## Implementation notes

- `max_uses` prevents runaway search loops — keep it between 3–10 for most use cases.
- `allowed_domains` is a strong trust boundary; use it when accuracy matters.
- Increase `max_tokens` (≥ 2048) — web results add significant context to the response.
- Citations appear in the response content as `web_search_result` blocks alongside text.

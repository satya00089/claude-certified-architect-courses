# Streaming conversations with tools

This folder demonstrates streaming conversations where a model can emit partial content and
structured tool calls (for example, `tool_use` blocks). The runner executes tool calls as they
are discovered (sometimes even while the model is still streaming), returns structured results,
and the conversation continues.

## What this is

- A demonstration of how to handle model streaming together with tool invocations.
- Shows how to detect content blocks like `tool_use`, stream partial JSON inputs (`input_json`),
  and then execute the requested tool and feed results back into the conversation.

## Why you need this

- Lower latency UX: stream partial outputs to the user while the model is still composing.
- Fine-grained tooling: detect a tool call as it is being produced (partial JSON), validate
  or cancel before executing, or run the tool as soon as enough input has been produced.
- Better observability: get a real-time view of what the model is asking the system to do.

## How it works (high-level)

1. Send the model a `tools` list (tool schemas) along with the chat request.
2. Use a streaming API (beta) so the model returns chunked content. Chunks may include:
   - `text` — partial text output
   - `content_block_start` — beginning of a structured block (e.g., `tool_use`)
   - `input_json` — partial JSON for tool inputs (useful for validation)
   - `content_block_stop` — end of the structured block
3. If a `tool_use` block is produced, the runner can execute the named tool (locally or via
   an API), then create `tool_result` blocks and inject them back into the messages.
4. Repeat until the model finishes (no further `tool_use`).

## Files

- `tool_streaming.ipynb` — notebook with examples of fine-grained streaming and tool execution.
- `streamlit_app.py` — small interactive demo (mock streaming + optional Anthropic integration).
- `requirements.txt` — dependencies for the demo.

## Run the Streamlit demo

1. Install dependencies:

```bash
pip install -r 004_tools/004_streaming_with_tools/requirements.txt
```

2. (Optional) Set your Anthropic API key in the environment or a `.env` file:

```
ANTHROPIC_API_KEY=your_key_here
```

3. Start the app:

```bash
streamlit run 004_tools/004_streaming_with_tools/streamlit_app.py
```

The app supports a mock streaming mode (no API key required) and an optional real Anthropic
integration (toggle in the sidebar). When using a real model, the app will stream chunks from
the model, detect `tool_use` blocks, execute defined tools (locally), and feed results back
into the conversation.

## Implementation notes

- Validate `input_json` chunks before executing a tool.
- Make tools idempotent and side-effect-safe where possible.
- Log all tool calls and results for traceability.

See [tool_streaming.ipynb](004_tools/004_streaming_with_tools/tool_streaming.ipynb) for the
original notebook examples and more details.

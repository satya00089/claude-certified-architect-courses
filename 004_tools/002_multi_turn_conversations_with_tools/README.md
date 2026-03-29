# Multi-turn conversations with tools

This folder demonstrates how to run multi-turn conversations where the assistant can request
and use external tools (small functions or APIs) during a chat. The runtime executes those
tool requests, returns structured results to the conversation, and lets the assistant continue
the dialog using the fresh tool output.

## Key concepts

- **Tool definition**: a schema describing a tool (name, description, input schema). In this
  example we use `ToolParam` objects to expose tools to the model.
- **Tool use**: the assistant may emit a `tool_use` block naming which tool to call and the
  inputs to pass.
- **Tool executor**: runtime code (e.g. `run_tools`) that finds `tool_use` blocks, validates
  inputs, calls the corresponding local function, and returns `tool_result` blocks.
- **Roundtrip**: tool results are injected back into the conversation (typically as a user
  message or `tool_result` block) so the assistant can continue the multi-turn flow.

## Typical flow

1. Register available tools (schemas) and send them with the chat request.
2. The model replies. If it requests a tool, the model may stop with `stop_reason == "tool_use"`.
3. The runner extracts `tool_use` blocks and executes the requested tools.
4. Tool outputs (structured JSON) are returned as `tool_result` blocks and appended to the
   conversation as user input.
5. Repeat calling the model with the updated messages until the assistant reply is final
   (no further `tool_use`).

## Minimal example (concept)

```python
# send tools to model
response = chat(messages, tools=[get_current_datetime_schema])

if response.stop_reason == "tool_use":
    tool_results = run_tools(response)          # execute local functions
    add_user_message(messages, tool_results)    # append the results and continue
    # call chat(messages, ...) again
```

## Implementation notes

- Validate and sanitize tool inputs before executing.
- Return structured results and expose an `is_error` flag for failures.
- Prefer idempotent, side-effect-safe tools when possible.
- Log tool calls and results for traceability and debugging.

See the working implementation in [004_tools/002_multi_turn_conversations_with_tools/multiple_turns.ipynb](004_tools/002_multi_turn_conversations_with_tools/multiple_turns.ipynb).

## Streamlit demo app

A small interactive demo shows the multi-turn tool flow without requiring an LLM. The app
simulates the assistant emitting a `tool_use` request, runs the local tool, and continues the
conversation with the tool output.

Run the demo locally:

1. Install the demo dependencies:

```
pip install -r 004_tools/002_multi_turn_conversations_with_tools/requirements.txt
```

2. Start the app:

```
streamlit run 004_tools/002_multi_turn_conversations_with_tools/streamlit_app.py
```

The demo supports example prompts such as:

- `What is the current time in HH:MM format?`
- `What is the current time in SS format?`

To integrate a real model, replace the `mock_assistant_response` function with a call to your
model that can emit structured `tool_use` blocks and follow the same roundtrip pattern.

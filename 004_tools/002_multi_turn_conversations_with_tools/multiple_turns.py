import os
import streamlit as st
import json
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import ToolParam

load_dotenv()
client = Anthropic()  # will use env var or default config

def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    """A simple tool that returns the current date and time in a specified format."""
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)


def run_tool(tool_name, tool_input):
    """Executes a specified tool with the given input."""
    if tool_name == "get_current_datetime":
        return get_current_datetime(**tool_input)
    raise ValueError(f"Unknown tool: {tool_name}")


def text_from_message(message):
    """Extract text blocks from an Anthropic message-like object (robust to dicts/objects)."""
    blocks = getattr(message, "content", None) or message
    texts = []
    try:
        for block in blocks:
            if isinstance(block, dict):
                if block.get("type") == "text" and block.get("text"):
                    texts.append(block.get("text"))
            else:
                if getattr(block, "type", None) == "text" and getattr(block, "text", None):
                    texts.append(getattr(block, "text"))
    except Exception:
        # Fallback: message might be a plain string
        return str(message)

    return "\n".join(texts) if texts else str(getattr(message, "content", message))


def extract_tool_requests(message):
    """Find tool_use blocks in a model message and return a list of {id,name,input}."""
    requests = []
    blocks = getattr(message, "content", []) or []
    for block in blocks:
        block_type = block.get("type") if isinstance(block, dict) else getattr(block, "type", None)
        if block_type == "tool_use":
            name = block.get("name") if isinstance(block, dict) else getattr(block, "name", None)
            inp = block.get("input") if isinstance(block, dict) else getattr(block, "input", None)
            rid = block.get("id") if isinstance(block, dict) else getattr(block, "id", None)
            requests.append({"id": rid, "name": name, "input": inp or {}})
    return requests


def run_tools_for_message(message):
    """Execute any tool_use requests found in a model message and return tool_result blocks."""
    tool_requests = extract_tool_requests(message)
    tool_result_blocks = []
    for tr in tool_requests:
        try:
            tool_output = run_tool(tr["name"], tr["input"] or {})
            tool_result_blocks.append({
                "type": "tool_result",
                "tool_use_id": tr.get("id"),
                "content": json.dumps(tool_output),
                "is_error": False,
            })
        except Exception as e:
            tool_result_blocks.append({
                "type": "tool_result",
                "tool_use_id": tr.get("id"),
                "content": f"Error: {e}",
                "is_error": True,
            })
    return tool_result_blocks


def append_message(role, text):
    """Appends a message to the session state (simple structured messages used by the demo)."""
    st.session_state.messages.append({"role": role, "text": text})


def to_api_messages(messages):
    """Convert local message list into a simple list of dicts suitable for model APIs."""
    api_msgs = []
    for m in messages:
        role = m.get("role")
        # Tool results are injected as user messages for the model to consume
        if role == "tool_result":
            api_msgs.append({"role": "user", "content": m.get("text")})
        else:
            api_msgs.append({"role": role, "content": m.get("text")})
    return api_msgs


def main():
    """Streamlit app to demonstrate multi-turn conversations with optional real model integration."""
    st.set_page_config(page_title="Multi-turn with Tools (demo)", layout="centered")
    st.title("Multi-turn Conversations with Tools — Demo")
    st.markdown(
        "This demo shows how an assistant can stop to call a tool, the runner executes the tool, and the conversation continues."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.expander("About this demo", expanded=False):
        st.write(
            "You can run this as a mock (no LLM) or enable a real Anthropic model. "
            "When using a real model, the app executes `tool_use` requests produced by the model "
            "and feeds results back into the conversation."
        )

    # Sidebar controls for real model usage
    model_input = st.sidebar.text_input("Model", value=os.environ.get("ANTHROPIC_MODEL", "claude-2"))
    temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.5, value=0.7)

    with st.form("user_input", clear_on_submit=True):
        user_text = st.text_area(
            "Your message",
            height=80,
            placeholder="E.g. What is the current time in HH:MM format?",
        )
        submit = st.form_submit_button("Send")

    if submit and user_text:
        append_message("user", user_text)


        tools = []
        if ToolParam is not None:
            tools.append(
                ToolParam(
                    {
                        "name": "get_current_datetime",
                        "description": "Returns the current date and time formatted according to the specified format string.",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "date_format": {"type": "string", "default": "%Y-%m-%d %H:%M:%S"}
                            },
                            "required": [],
                        },
                    }
                )
            )

        # Loop until the model stops requesting tools
        while True:
            api_msgs = to_api_messages(st.session_state.messages)
            params = {
                "model": model_input,
                "messages": api_msgs,
                "max_tokens": 500,
                "temperature": temperature,
            }
            if tools:
                params["tools"] = tools

            try:
                response = client.messages.create(**params)
            except Exception as e:
                st.error(f"Model call failed: {e}")
                break

            assistant_text = text_from_message(response)
            append_message("assistant", assistant_text)

            # If the model requested a tool, execute it and feed results back
            stop_reason = getattr(response, "stop_reason", None)
            if stop_reason != "tool_use":
                break

            tool_results = run_tools_for_message(response)
            # append each tool result as a visible tool_result and also inject as a user message
            for tr in tool_results:
                append_message("tool_result", tr.get("content"))
            append_message("user", json.dumps({"tool_results": tool_results}))

    # Render conversation
    for msg in st.session_state.messages:
        role = msg.get("role")
        if role == "user":
            st.markdown(f"**User:** {msg.get('text')}")
        elif role == "assistant":
            st.markdown(f"**Assistant:** {msg.get('text')}")
        elif role == "tool_result":
            st.markdown("**Tool result:**")
            st.code(msg.get("text"))

    st.markdown("---")
    st.markdown("**Try these example prompts:**")
    st.markdown("- What is the current time in HH:MM format?")
    st.markdown("- What is the current time in SS format?")
    st.markdown("- Give me the current timestamp")


if __name__ == "__main__":
    main()

"""Streamlit demo for the Extended Thinking notebook.

Usage:
    streamlit run streamlit_app.py

Requires a working Anthropic SDK and API key in a .env file.
"""

from dotenv import load_dotenv
import streamlit as st
from anthropic import Anthropic

load_dotenv()


# Default model (same as notebook)
MODEL = "claude-sonnet-4-5"

# Magic string from the notebook to trigger redacted thinking demonstrations
THINKING_TEST_STR = "ANTHROPIC_MAGIC_STRING_TRIGGER_REDACTED_THINKING_46C9A13E193C177646C7398A98432ECCCE4C1253D5E2D82641AC0E52CC2876CB"


client = Anthropic()


def add_user_message(messages, message):
    """Helper to add a user message to the conversation history."""
    messages.append({"role": "user", "content": message})


def add_assistant_message(messages, message):
    """Helper to add an assistant message to the conversation history."""
    messages.append({"role": "assistant", "content": message})


def chat(
    client,
    messages,
    system=None,
    temperature=1.0,
    stop_sequences=None,
    tools=None,
    thinking=False,
    thinking_budget=1024,
):
    """Helper to call the Anthropic SDK with the right parameters for this demo."""
    if stop_sequences is None:
        stop_sequences = []

    params = {
        "model": MODEL,
        "max_tokens": 4000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }

    if thinking:
        # ensure max_tokens is strictly greater than the thinking budget
        current_max = params.get("max_tokens") or 0
        if thinking_budget >= current_max:
            params["max_tokens"] = int(thinking_budget * 1.5)
        params["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}

    if tools:
        params["tools"] = tools
    if system:
        params["system"] = system

    if client is None:
        raise RuntimeError(
            "Anthropic client not available. Set ANTHROPIC_API_KEY in .env"
        )

    return client.messages.create(**params)


def text_from_message(message):
    """Helper to extract text from the SDK response. Fall back to string repr."""
    try:
        if hasattr(message, "content"):
            content = message.content
            # content may be a list of blocks
            if isinstance(content, list):
                parts = [
                    getattr(block, "text", None) or block.get("text", "")
                    for block in content
                ]
                return "\n".join([p for p in parts if p])
            if isinstance(content, str):
                return content
        if isinstance(message, dict):
            c = message.get("content")
            if isinstance(c, str):
                return c
            if isinstance(c, list):
                return "\n".join(
                    [b.get("text", "") for b in c if b.get("type") == "text"]
                )
    except Exception:
        pass
    return str(message)


def main():
    """Main Streamlit app function."""
    st.title("Extended Thinking — demo")

    st.markdown("Small demo that mirrors `thinking.ipynb` (use `.env` for keys).")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.form(key="send_form"):
        user_input = st.text_area(
            "User message",
            value="write a one paragraph story about a dog who loves to surf",
            height=120,
        )
        temperature = st.slider("Temperature", 0.0, 2.0, 1.0, 0.1)
        thinking = st.checkbox("Enable thinking (redacted)")
        thinking_budget = st.slider("Thinking budget tokens", 128, 8192, 1024, step=128)
        col1, col2 = st.columns([1, 3])
        trigger = col1.form_submit_button("Trigger magic thinking test")
        submit = col2.form_submit_button("Send")

    if trigger:
        add_user_message(st.session_state.messages, THINKING_TEST_STR)
        try:
            resp = chat(
                client,
                st.session_state.messages,
                temperature=temperature,
                thinking=True,
                thinking_budget=thinking_budget,
            )
            assistant_text = text_from_message(resp)
            add_assistant_message(st.session_state.messages, assistant_text)
            st.success("Response received (magic test)")
            st.write(assistant_text)
            st.json(getattr(resp, "__dict__", resp))
        except Exception as e:
            st.error(f"API call failed: {e}")

    if submit:
        add_user_message(st.session_state.messages, user_input)
        try:
            resp = chat(
                client,
                st.session_state.messages,
                temperature=temperature,
                thinking=thinking,
                thinking_budget=thinking_budget,
            )
            assistant_text = text_from_message(resp)
            add_assistant_message(st.session_state.messages, assistant_text)
            st.success("Response received")
            st.write(assistant_text)
            try:
                st.json(getattr(resp, "__dict__", resp))
            except Exception:
                st.write(repr(resp))
        except Exception as e:
            st.error(f"API call failed: {e}")

    st.subheader("Conversation history")
    for m in st.session_state.messages:
        role = m.get("role")
        content = m.get("content")
        if role == "user":
            st.markdown(f"**User:** {content}")
        else:
            st.markdown(f"**Assistant:** {content}")


if __name__ == "__main__":
    main()

import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant.
When streaming is enabled, send text chunks as they are generated so the user
sees the response build up in real time.
"""

client = Anthropic()

# Reusable labels/constants
ASSISTANT_RESPONSE_LABEL = "Assistant response"


def _extract_text_from_message(message):
    """Return the first content text from a message object, or None."""
    content = getattr(message, "content", None)
    if isinstance(content, (list, tuple)) and len(content) > 0:
        first = content[0]
        return getattr(first, "text", None)
    return None


def _run_stream(user_input, system_prompt, model, temperature, max_tokens, placeholder):
    """Run a streaming request and update `placeholder` with incremental text."""
    collected = ""
    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": user_input}],
        temperature=temperature,
        system=system_prompt,
    ) as stream:
        for chunk in stream.text_stream:
            collected += chunk
            placeholder.text_area("Assistant (streaming)", value=collected, height=300)

        final = stream.get_final_message()

    final_text = _extract_text_from_message(final)
    if final_text:
        st.subheader("Final assistant text")
        st.write(final_text)

    st.subheader("Final message object")
    try:
        st.json(final)
    except TypeError:
        st.write(final)


def _run_non_stream(user_input, system_prompt, model, temperature, max_tokens):
    """Run a non-streaming request and display the assistant text or raw response."""
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": user_input}],
        temperature=temperature,
        system=system_prompt,
    )

    text = _extract_text_from_message(resp)
    if text is not None:
        st.subheader(ASSISTANT_RESPONSE_LABEL)
        st.write(text)
    else:
        st.subheader(ASSISTANT_RESPONSE_LABEL)
        st.write(str(resp))


def main():
    """Streamlit app for demonstrating streaming responses from the Claude API."""
    st.set_page_config(page_title="Streaming Playground")
    st.title("Streaming Playground — Claude streaming demo")
    st.markdown(
        "Interactive demo showing how to stream responses from Claude and display them chunk-by-chunk."
    )

    model = st.selectbox("Model", ["claude-sonnet-4-0", "claude-instant"], index=0)
    system_prompt = st.text_area(
        "System prompt", value=DEFAULT_SYSTEM_PROMPT, height=150
    )
    user_input = st.text_area(
        "User message",
        value="Write a 1-sentence description of a fake database that stores unusual artifacts.",
        height=150,
    )

    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, step=0.01)
    max_tokens = st.slider("Max tokens", 100, 4000, 500, step=50)
    stream_enable = st.checkbox("Enable streaming", value=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Send"):
            if stream_enable:
                placeholder = st.empty()
                with st.spinner("Streaming response..."):
                    try:
                        _run_stream(
                            user_input,
                            system_prompt,
                            model,
                            temperature,
                            max_tokens,
                            placeholder,
                        )
                    except (
                        ConnectionError,
                        TimeoutError,
                        RuntimeError,
                        ValueError,
                        AttributeError,
                    ) as e:
                        st.error(f"Streaming error: {e}")
            else:
                with st.spinner("Calling the API..."):
                    try:
                        _run_non_stream(
                            user_input, system_prompt, model, temperature, max_tokens
                        )
                    except (
                        ConnectionError,
                        TimeoutError,
                        RuntimeError,
                        ValueError,
                        AttributeError,
                    ) as e:
                        st.error(f"API error: {e}")

    with col2:
        if st.button("Reset", type="secondary", use_container_width=True):
            st.rerun()

    st.markdown("### Payload preview")
    messages_payload = [{"role": "user", "content": user_input}]
    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream_enable,
        "messages": messages_payload,
        "system": system_prompt,
    }
    st.json(payload)


if __name__ == "__main__":
    main()

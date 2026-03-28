import json
import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant that outputs only the requested content
in the specified format, with no explanatory text or extra commentary."""

client = Anthropic()


def _extract_text_from_message(message):
    """Return the first content text from a message object, or None."""
    content = getattr(message, "content", None)
    if isinstance(content, (list, tuple)) and len(content) > 0:
        first = content[0]
        return getattr(first, "text", None)
    return None


def generate_structured(
    messages,
    system=None,
    model="claude-sonnet-4-0",
    temperature=0.0,
    max_tokens=500,
    stop_sequences=None,
):
    """Call the API with optional stop sequences and return the assistant text."""
    params = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
        "temperature": temperature,
    }
    if system:
        params["system"] = system
    if stop_sequences is not None:
        params["stop_sequences"] = stop_sequences

    resp = client.messages.create(**params)
    return _extract_text_from_message(resp) or str(resp)


def main():
    """Streamlit app for generating structured data with optional assistant prefill and stop sequences."""
    st.set_page_config(page_title="Structured Data Playground")
    st.title("Structured Data — Prefill + Stop Sequences")
    st.markdown(
        "Generate clean structured outputs (JSON, Python, CSV, lists) using an assistant-prefill and stop sequence technique."
    )

    model = st.selectbox("Model", ["claude-sonnet-4-0", "claude-instant"], index=0)
    fmt = st.selectbox("Format", ["JSON", "Python", "CSV", "Bulleted list"])
    system_prompt = st.text_area(
        "System prompt", value=DEFAULT_SYSTEM_PROMPT, height=120
    )
    user_input = st.text_area(
        "User prompt",
        value="Generate a very short AWS EventBridge rule as JSON",
        height=150,
    )

    temperature = st.slider("Temperature", 0.0, 1.0, 0.0, step=0.01)
    max_tokens = st.slider("Max tokens", 50, 2000, 500, step=50)

    use_prefill = st.checkbox("Use assistant prefill + stop sequence", value=True)

    prefill_map = {
        "JSON": ("```json", ["```"]),
        "Python": ("```python", ["```"]),
        "CSV": ("```csv", ["```"]),
        "Bulleted list": ("- ", ["\n\n"]),
    }

    assistant_prefill = None
    stop_seq = None
    if use_prefill:
        assistant_prefill, stop_seq = prefill_map.get(fmt, (None, None))

    if st.button("Generate"):
        messages = [{"role": "user", "content": user_input}]
        if assistant_prefill:
            # Prefill an assistant message so Claude continues in the desired format
            messages.append({"role": "assistant", "content": assistant_prefill})

        with st.spinner("Calling the API..."):
            result = generate_structured(
                messages,
                system=system_prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stop_sequences=stop_seq,
            )

        st.subheader("Raw output")
        st.text_area("Result", value=result, height=300)

        if fmt == "JSON" and use_prefill:
            try:
                parsed = json.loads(result.strip())
                st.subheader("Parsed JSON")
                st.json(parsed)
            except json.JSONDecodeError as e:
                st.error(f"JSON parse error: {e}")

    st.markdown("### Payload preview")
    messages_preview = [{"role": "user", "content": user_input}]
    if assistant_prefill:
        messages_preview.append({"role": "assistant", "content": assistant_prefill})

    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stop_sequences": stop_seq,
        "messages": messages_preview,
        "system": system_prompt,
    }
    st.json(payload)


if __name__ == "__main__":
    main()

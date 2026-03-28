import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant.
Explain how the `temperature` parameter affects response variability and creativity.
"""

client = Anthropic()


def chat_with_temperature(
    user_text, system_prompt=None, model="claude-sonnet-4-0", temperature=0.7, max_tokens=1000
):
    """Send a message to the Claude API with an explicit temperature."""
    messages = [{"role": "user", "content": user_text}]
    params = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
        "temperature": temperature,
    }
    if system_prompt:
        params["system"] = system_prompt

    resp = client.messages.create(**params)
    # Safely extract the assistant text if available
    content = getattr(resp, "content", None)
    if isinstance(content, (list, tuple)) and len(content) > 0:
        first = content[0]
        text = getattr(first, "text", None)
        if text is not None:
            return text
    return str(resp)


def main():
    """Streamlit app for experimenting with the temperature parameter."""
    st.set_page_config(page_title="Temperature Playground")
    st.title("Temperature Playground — Claude examples")
    st.markdown(
        "Interactive playground for experimenting with the `temperature` parameter and the Claude message API."
    )

    model = st.selectbox("Model", ["claude-sonnet-4-0", "claude-instant"], index=0)
    system_prompt = st.text_area("System prompt", value=DEFAULT_SYSTEM_PROMPT, height=150)
    user_input = st.text_area("User message", value="Write a short movie idea.", height=150)

    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, step=0.01)
    max_tokens = st.slider("Max tokens", 100, 4000, 1000, step=100)

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Send"):
            with st.spinner("Calling the API..."):
                answer = chat_with_temperature(
                    user_input,
                    system_prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            st.subheader("Assistant response")
            st.write(answer)
    with col2:
        if st.button("Reset conversation", type="secondary", use_container_width=True):
            st.rerun()

    st.markdown("### Payload preview")
    st.json(
        {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": user_input}],
            "system": system_prompt,
        }
    )


if __name__ == "__main__":
    main()

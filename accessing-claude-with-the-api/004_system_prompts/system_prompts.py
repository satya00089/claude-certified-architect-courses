import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


DEFAULT_SYSTEM_PROMPT = """You are a patient math tutor.
Do not directly answer a student's questions.
Guide them to a solution step by step.
"""

client = Anthropic()


def chat_with_system(
    user_text, system_prompt, model="claude-sonnet-4-0", max_tokens=1000
):
    """Send a message to the Claude API with a system prompt."""
    messages = [{"role": "user", "content": user_text}]
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=messages,
        system=system_prompt,
    )
    try:
        return resp.content[0].text
    except Exception:
        return str(resp)


def main():
    """Streamlit app for testing system prompts with the Claude API."""
    st.set_page_config(page_title="System Prompt Playground")
    st.title("System Prompt Playground — Claude examples")
    st.markdown(
        "Interactive playground for experimenting with system prompts and the Claude message API."
    )
    model = st.selectbox(
        "Model", ["claude-sonnet-4-0", "claude-instant"], index=0
    )
    system_prompt = st.text_area(
        "System prompt", value=DEFAULT_SYSTEM_PROMPT, height=200
    )
    user_input = st.text_area("User message", value="", height=150)

    max_tokens = st.slider("Max tokens", 100, 4000, 1000, step=100)
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Send"):
            try:
                with st.spinner("Calling the API..."):
                    answer = chat_with_system(
                        user_input,
                        system_prompt,
                        model=model,
                        max_tokens=max_tokens,
                    )
                st.subheader("Assistant response")
                st.write(answer)
            except Exception as e:
                st.error(f"API error: {e}")
    with col2:
        if st.button("Reset conversation", type="secondary", use_container_width=True):
            st.rerun()

    st.markdown("### Payload preview")
    st.json(
        {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": user_input}],
            "system": system_prompt,
        }
    )


if __name__ == "__main__":
    main()

from anthropic import Anthropic
from dotenv import load_dotenv
import streamlit as st
from requests.exceptions import RequestException

load_dotenv()

st.set_page_config(
    page_title="Claude Requests",
    page_icon="🤖",
    layout="wide"
)

st.title("Claude Requests")

client = Anthropic()
st.markdown("Use this app to send a prompt to Claude and view the response.")
model = st.selectbox("Model", ["claude-sonnet-4-0", "claude-2.1"], index=0)
prompt = st.text_area("Prompt", value="What is cloud computing? Answer in a sentence.")
max_tokens = st.slider("Max tokens", 10, 2000, 100)

# Multi-turn toggle and session state for conversation history
multi_turn = st.checkbox("Enable multi-turn (keep conversation history)", value=True)
if "messages" not in st.session_state:
    st.session_state.messages = []

def add_user_message(messages, message_text):
    """Helper function to add a user message to the conversation history."""
    messages.append({"role": "user", "content": message_text})

def add_assistant_message(messages, message_text):
    """Helper function to add an assistant message to the conversation history."""
    messages.append({"role": "assistant", "content": message_text})

def chat(messages_list):
    """Helper function to send a list of messages to Claude and return the response."""
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=messages_list,
    )
    return message

col1, col2 = st.columns([5, 1])
with col1:
    send_clicked = st.button("Send")
with col2:
    reset_clicked = False
    if multi_turn:
        reset_clicked = st.button("Reset conversation", type="secondary", use_container_width=True)

if reset_clicked:
    st.session_state.messages = []

if send_clicked:
    with st.spinner("Calling Claude..."):
        try:
            if multi_turn:
                # append user message, send full history, then append assistant reply
                add_user_message(st.session_state.messages, prompt)
                resp = chat(st.session_state.messages)
                try:
                    assistant_text = resp.content[0].text
                except Exception:
                    assistant_text = str(resp)
                add_assistant_message(st.session_state.messages, assistant_text)
            else:
                resp = client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                )
                try:
                    assistant_text = resp.content[0].text
                except Exception:
                    assistant_text = str(resp)
        except (TypeError, ValueError, RuntimeError, RequestException) as e:
            st.exception(e)
        else:
            st.subheader("Response")
            st.write(assistant_text)
            try:
                st.subheader("Full response (JSON)")
                st.json(resp)
            except (TypeError, ValueError):
                pass

st.markdown(
    "---\nRun this app with: `streamlit run multi_turn_conversations.py` (from the same folder)"
)

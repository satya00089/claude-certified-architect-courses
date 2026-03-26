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

if st.button("Send"):
    with st.spinner("Calling Claude..."):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
        except (TypeError, ValueError, RuntimeError, RequestException) as e:
            st.exception(e)
        else:
            st.subheader("Response")
            st.write(resp.content[0].text)
            try:
                st.subheader("Full response (JSON)")
                st.json(resp)
            except (TypeError, ValueError):
                pass

st.markdown(
    "---\nRun this app with: `streamlit run claude_requests.py` (from the same folder)"
)

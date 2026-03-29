"""Streamlit demo for the Code Execution notebook.

Usage:
    streamlit run streamlit_app.py

Requires a working Anthropic SDK and API key in a .env file. The client is
initialized with beta headers enabling the files and code-execution APIs.
"""

from dotenv import load_dotenv
import streamlit as st
from anthropic import Anthropic
import io
import base64
from pathlib import Path

load_dotenv()


# Client configured with code-execution and files API beta headers (matches notebook)
client = Anthropic(
    default_headers={
        "anthropic-beta": "code-execution-2025-08-25, files-api-2025-04-14"
    }
)

# Default model used in the notebook
MODEL = "claude-sonnet-4-5-20250929"


def add_user_message(messages, message):
    messages.append({"role": "user", "content": message})


def add_assistant_message(messages, message):
    messages.append({"role": "assistant", "content": message})


def chat(
    client,
    messages,
    system=None,
    temperature=1.0,
    stop_sequences=None,
    tools=None,
    thinking=False,
    thinking_budget=2000,
):
    if stop_sequences is None:
        stop_sequences = []

    params = {
        "model": MODEL,
        "max_tokens": 10000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }

    if thinking:
        current_max = params.get("max_tokens") or 0
        if thinking_budget >= current_max:
            params["max_tokens"] = thinking_budget + 1
        params["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}

    if tools:
        params["tools"] = tools
    if system:
        params["system"] = system

    if client is None:
        raise RuntimeError("Anthropic client not available. Set ANTHROPIC_API_KEY in .env")

    return client.messages.create(**params)


def text_from_message(message):
    try:
        if hasattr(message, "content"):
            content = message.content
            if isinstance(content, list):
                parts = [getattr(block, "text", None) or block.get("text", "") for block in content]
                return "\n".join([p for p in parts if p])
            if isinstance(content, str):
                return content
        if isinstance(message, dict):
            c = message.get("content")
            if isinstance(c, str):
                return c
            if isinstance(c, list):
                return "\n".join([b.get("text", "") for b in c if b.get("type") == "text"])
    except Exception:
        pass
    return str(message)


def upload_streamlit_file(uploaded_file):
    """Upload an uploaded_file (Streamlit UploadedFile) to the Anthropic Files API.

    Returns the file metadata object from the API.
    """
    if uploaded_file is None:
        return None

    fname = uploaded_file.name
    extension = Path(fname).suffix.lower()

    mime_type_map = {
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".md": "text/plain",
        ".py": "text/plain",
        ".csv": "text/csv",
        ".json": "application/json",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg",
        ".png": "image/png",
    }

    mime_type = mime_type_map.get(extension, "application/octet-stream")

    file_bytes = uploaded_file.read()
    file_obj = io.BytesIO(file_bytes)

    # The beta files.upload expects a file tuple (filename, fileobj, mime_type)
    return client.beta.files.upload(file=(fname, file_obj, mime_type))


def main():
    st.title("Code Execution — demo")
    st.markdown("Small demo that mirrors `code_execution.ipynb` (use `.env` for keys).")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.form(key="send_form"):
        prompt_default = (
            "Run a detailed analysis to determine major drivers of churn.\n"
            "Your final output should include at least one detailed plot summarizing your findings.\n\n"
            "Critical note: Every time you execute code, you're starting with a completely clean slate.\n"
            "No variables or library imports from previous executions exist. You need to redeclare/reimport all variables/libraries."
        )

        prompt = st.text_area("Instruction / prompt", value=prompt_default, height=200)
        uploaded_file = st.file_uploader("Upload file for code execution (CSV, XLSX, or code)", type=["csv", "xlsx", "txt", "py", "ipynb"], key="exec_uploader")
        temperature = st.slider("Temperature", 0.0, 2.0, 0.0, 0.1)
        thinking = st.checkbox("Enable thinking (redacted)")
        thinking_budget = st.slider("Thinking budget tokens", 256, 8192, 2000, step=128)
        col1, col2 = st.columns([1, 3])
        submit = col2.form_submit_button("Send for execution")

    if submit:
        if uploaded_file is None:
            st.warning("Please upload a file to run code against.")
            return

        try:
            file_metadata = upload_streamlit_file(uploaded_file)
            st.write(f"Uploaded: {getattr(file_metadata, 'filename', getattr(file_metadata, 'id', 'unknown'))}")

            messages = []
            # The notebook uses a container_upload block pointing to the uploaded file id
            messages.append({"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "container_upload", "file_id": getattr(file_metadata, 'id', file_metadata.get('id'))}
            ]})

            tools = [{"type": "code_execution_20250825", "name": "code_execution"}]

            resp = chat(
                client,
                messages,
                temperature=temperature,
                tools=tools,
                thinking=thinking,
                thinking_budget=thinking_budget,
            )

            assistant_text = text_from_message(resp)
            add_assistant_message(st.session_state.messages, assistant_text)
            st.success("Execution response received")
            st.write(assistant_text)
            try:
                st.json(getattr(resp, "__dict__", resp))
            except Exception:
                st.write(repr(resp))
        except Exception as e:
            st.error(f"API call or upload failed: {e}")

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

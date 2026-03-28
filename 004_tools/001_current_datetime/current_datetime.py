import streamlit as st
from datetime import datetime
from typing import Any, Dict
from dotenv import load_dotenv
import os

try:
    from anthropic import Anthropic
    from anthropic.types import ToolParam
except Exception:
    Anthropic = None
    ToolParam = None

load_dotenv()

client = None
if Anthropic is not None:
    try:
        client = Anthropic()
    except Exception:
        client = None

def get_current_datetime(date_format: str = "%Y-%m-%d %H:%M:%S") -> str:
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)

def anthropic_get_datetime(date_format: str, model: str = "claude-haiku-4-5") -> Dict[str, Any]:
    if client is None:
        raise RuntimeError("Anthropic client not initialized. Ensure CLAUDE_API_KEY is set and `anthropic` is installed.")
    if ToolParam is None:
        raise RuntimeError("Anthropic types not available (ToolParam).")

    get_current_datetime_schema = ToolParam({
        "name": "get_current_datetime",
        "description": "Get the current date and time in a specified format.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date_format": {
                    "type": "string",
                    "description": "The format in which to return the date and time.",
                    "default": "%Y-%m-%d %H:%M:%S",
                }
            },
            "required": ["date_format"],
        },
    })

    user_message = {"role": "user", "content": f"what is the current date and time, formatted as {date_format}?"}
    resp = client.messages.create(model=model, max_tokens=200, tools=[get_current_datetime_schema], messages=[user_message])

    # Try to extract tool use info
    tool_input = None
    tool_use_id = None
    try:
        tool_use = resp.content[0]
        tool_input = getattr(tool_use, "input", None) or (tool_use.get("input") if isinstance(tool_use, dict) else None)
        tool_use_id = getattr(tool_use, "id", None) or (tool_use.get("id") if isinstance(tool_use, dict) else None)
    except Exception:
        tool_input = None
        tool_use_id = None

    if not tool_input:
        # Model didn't request the tool; return the model text
        model_text = getattr(resp.content[0], "text", str(resp.content[0]))
        return {"model_text": model_text, "tool_applied": False, "raw": resp}

    # Compute the result locally and send it back as a tool_result
    try:
        tool_result_value = get_current_datetime(**tool_input)
    except Exception as e:
        tool_result_value = f"Error computing datetime: {e}"

    tool_result_block = {"type": "tool_result", "tool_use_id": tool_use_id, "content": tool_result_value}
    assistant_message = {"role": "assistant", "content": [tool_result_block]}

    new_resp = client.messages.create(model=model, max_tokens=200, tools=[get_current_datetime_schema], messages=[user_message, assistant_message])
    model_text = getattr(new_resp.content[0], "text", str(new_resp.content[0]))
    return {"model_text": model_text, "tool_applied": True, "tool_result": tool_result_value, "raw": new_resp}

def main():
    st.title("Current Datetime — Streamlit Demo")
    st.markdown("Small demo that returns the current datetime in a requested format. Choose `Local` or `Anthropic`.")

    with st.form("dt_form"):
        date_format = st.text_input("Date format", value="%Y-%m-%d %H:%M")
        source = st.selectbox("Source", ["Local (Python)", "Anthropic Claude"])
        model = st.text_input("Anthropic model", value="claude-haiku-4-5")
        show_raw = st.checkbox("Show raw API response (Anthropic)", value=False)
        submit = st.form_submit_button("Get datetime")

    if submit:
        if source == "Local (Python)":
            try:
                val = get_current_datetime(date_format)
                st.success(val)
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            try:
                result = anthropic_get_datetime(date_format, model=model)
                if result.get("tool_applied"):
                    st.success(result.get("tool_result"))
                    st.subheader("Model response")
                    st.write(result.get("model_text"))
                    if show_raw:
                        st.subheader("Raw response")
                        st.write(result.get("raw"))
                else:
                    st.write(result.get("model_text"))
                    if show_raw:
                        st.write(result.get("raw"))
            except Exception as e:
                st.error(f"Anthropic call failed: {e}")

    st.markdown("#### Notes")
    st.markdown("- Ensure `CLAUDE_API_KEY` (Anthropic key) is available in environment or in a `.env` file when using Anthropic mode.")
    st.markdown("- Run from this folder: `streamlit run streamlit_app.py`")

if __name__ == "__main__":
    main()

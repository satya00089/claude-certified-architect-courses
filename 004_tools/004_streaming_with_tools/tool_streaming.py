import os
import time
import json
import streamlit as st
from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import ToolParam

load_dotenv()
client = Anthropic()  # will use env var or default config


def save_article(abstract=None, meta=None):
    """Example tool that 'saves' an article and returns metadata."""
    if abstract is None or meta is None:
        raise ValueError("abstract and meta are required")
    word_count = meta.get("word_count") or len(abstract.split())
    review = meta.get("review") or "Auto-generated review: concise and clear."
    return {"status": "saved", "word_count": word_count, "review": review}


def run_tool(tool_name, tool_input):
    """Executes a specified tool with the given input."""
    if tool_name == "save_article":
        return save_article(**tool_input)
    raise ValueError(f"Unknown tool: {tool_name}")


def mock_stream_generator(user_prompt, tool_choice=None):
    """Yield mock streaming chunks to mimic fine-grained tool streaming."""
    # partial text
    yield {"type": "text", "text": "Composing document outline...\n"}
    time.sleep(0.25)
    yield {"type": "text", "text": "Writing abstract: "}
    time.sleep(0.25)

    wants_save = ("save" in user_prompt.lower()) or (tool_choice == "save_article")
    if wants_save:
        # start of a tool call block
        yield {
            "type": "content_block_start",
            "content_block": {"type": "tool_use", "name": "save_article"},
        }
        time.sleep(0.12)
        # partial JSON chunk
        ij = json.dumps(
            {
                "abstract": "A short demo abstract.",
                "meta": {"word_count": 5, "review": "Auto-review: OK"},
            }
        )
        yield {"type": "input_json", "partial_json": ij}
        time.sleep(0.12)
        yield {"type": "content_block_stop"}
        time.sleep(0.1)
        # Simulate tool execution and result
        result = run_tool(
            "save_article",
            {
                "abstract": "A short demo abstract.",
                "meta": {"word_count": 5, "review": "Auto-review: OK"},
            },
        )
        yield {"type": "text", "text": "\nTool result: " + json.dumps(result) + "\n"}
    else:
        yield {"type": "text", "text": "No tool requested. Finalizing document...\n"}


def chunk_to_text(chunk):
    """Convert a streaming chunk (dict or object) to displayable text."""
    if isinstance(chunk, dict):
        t = chunk.get("type")
        if t == "text":
            return chunk.get("text", "")
        if t == "content_block_start":
            cb = chunk.get("content_block", {})
            if cb.get("type") == "tool_use":
                return f"\n>>> Tool Call: \"{cb.get('name')}\"\n"
        if t == "input_json":
            return chunk.get("partial_json", "")
        if t == "content_block_stop":
            return "\n"
    # fallback
    return str(chunk)


def main():
    """Streamlit app demonstrating fine-grained streaming with tool calls."""
    st.set_page_config(page_title="Streaming + Tools Demo", layout="centered")
    st.title("Streaming Conversations with Tools — Demo")

    st.markdown(
        "This demo shows fine-grained streaming where the model can emit tool calls while streaming."
    )

    if "history" not in st.session_state:
        st.session_state.history = []

    model_input = st.sidebar.text_input(
        "Model", value=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
    )
    fine_grained = st.sidebar.checkbox("Fine-grained streaming (beta)", value=False)
    tool_choice = st.sidebar.selectbox(
        "Force tool choice (optional)", options=["auto", "save_article"]
    )

    with st.form("prompt_form", clear_on_submit=True):
        user_prompt = st.text_area(
            "User prompt",
            height=120,
            placeholder="E.g. Create and save a short article",
        )
        submit = st.form_submit_button("Send")

    out_placeholder = st.empty()

    if submit and user_prompt:
        st.session_state.history.append({"role": "user", "text": user_prompt})

        # Build tool schema
        tools = []
        if ToolParam is not None:
            tools.append(
                ToolParam(
                    {
                        "name": "save_article",
                        "description": "Saves a scholarly journal article",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "abstract": {"type": "string"},
                                "meta": {
                                    "type": "object",
                                    "properties": {
                                        "word_count": {"type": "integer"},
                                        "review": {"type": "string"},
                                    },
                                },
                            },
                            "required": ["abstract", "meta"],
                        },
                    }
                )
            )

        api_messages = [{"role": "user", "content": user_prompt}]
        params = {"model": model_input, "messages": api_messages, "max_tokens": 800}
        if tools:
            params["tools"] = tools
        if fine_grained:
            params["betas"] = ["fine-grained-tool-streaming-2025-05-14"]
        if tool_choice != "auto":
            params["tool_choice"] = {"type": "tool", "name": tool_choice}

        output = ""
        out_placeholder.code(output)

        try:
            with client.beta.messages.stream(**params) as stream:
                for chunk in stream:
                    # chunk may be object-like or dict-like
                    if hasattr(chunk, "type"):
                        c = {
                            "type": getattr(chunk, "type"),
                            "text": getattr(chunk, "text", None),
                        }
                        # content_block, partial_json may also be attrs
                        content_block = getattr(chunk, "content_block", None)
                        if content_block is not None:
                            c["content_block"] = {
                                "type": getattr(content_block, "type", None),
                                "name": getattr(content_block, "name", None),
                            }
                        partial_json = getattr(chunk, "partial_json", None)
                        if partial_json is not None:
                            c["partial_json"] = partial_json
                    else:
                        c = chunk

                    output += chunk_to_text(c)
                    out_placeholder.code(output)

                # final message available from stream
                final = stream.get_final_message()
                assistant_text = (
                    "\n".join([b.text for b in final.content if b.type == "text"])
                    if hasattr(final, "content")
                    else str(final)
                )
                st.session_state.history.append(
                    {"role": "assistant", "text": assistant_text}
                )

                # if model requested tools, run them
                stop_reason = getattr(final, "stop_reason", None)
                if stop_reason == "tool_use":
                    # execute and show results
                    tool_results = []
                    for block in final.content:
                        if block.type == "tool_use":
                            tr = run_tool(block.name, block.input or {})
                            tool_results.append(tr)
                            st.session_state.history.append(
                                {"role": "tool_result", "text": json.dumps(tr)}
                            )

        except Exception as e:
            st.error(f"Streaming call failed: {e}")

    # Render conversation history
    for entry in st.session_state.history:
        if entry.get("role") == "user":
            st.markdown(f"**User:** {entry.get('text')}")
        elif entry.get("role") == "assistant":
            st.markdown(f"**Assistant:** {entry.get('text')}")
        elif entry.get("role") == "tool_result":
            st.markdown("**Tool result:**")
            st.code(entry.get("text"))


if __name__ == "__main__":
    main()

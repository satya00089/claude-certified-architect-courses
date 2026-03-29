"""
Medical Research Assistant — Streamlit Demo
============================================
Use case: ask medical or health questions and get answers grounded exclusively in
NIH / PubMed sources via the Anthropic web_search tool with allowed_domains=["nih.gov"].

You can also switch to "General search" mode to remove the domain restriction, or supply
your own allow/block lists.

Example questions to try:
  - What are the most effective treatments for Type 2 diabetes?
  - What does current research say about the gut-brain connection?
  - What are the NIH guidelines for managing hypertension?
  - What does the evidence say about intermittent fasting and longevity?
  - What are the latest findings on Alzheimer's prevention?
"""

import streamlit as st
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()


SYSTEM_PROMPT = """\
You are a medical research assistant. You answer health and medical questions using only
evidence from peer-reviewed research and authoritative health organisations.

When you search the web:
- Prefer systematic reviews, meta-analyses, and clinical guidelines.
- Always cite the source URL for every factual claim.
- Clearly distinguish between established consensus and emerging/preliminary findings.
- Do not provide personal medical advice; direct users to consult a healthcare professional
  for individual decisions.

Structure your answer with:
1. A direct, concise answer to the question.
2. Key evidence (bullet points with citations).
3. A brief caveat if the evidence is contested or preliminary."""


def build_search_schema(
    mode: str, custom_allowed: str, custom_blocked: str, max_uses: int
) -> dict:
    """Construct the web_search tool schema based on user-selected mode and inputs."""
    schema: dict = {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": max_uses,
    }
    if mode == "NIH only (nih.gov)":
        schema["allowed_domains"] = ["nih.gov"]
    elif mode == "Trusted health sources":
        schema["allowed_domains"] = [
            "nih.gov",
            "who.int",
            "cdc.gov",
            "mayoclinic.org",
            "pubmed.ncbi.nlm.nih.gov",
        ]
    elif mode == "Custom":
        if custom_allowed.strip():
            schema["allowed_domains"] = [
                d.strip() for d in custom_allowed.split(",") if d.strip()
            ]
        if custom_blocked.strip():
            schema["blocked_domains"] = [
                d.strip() for d in custom_blocked.split(",") if d.strip()
            ]
    # "General (no restrictions)" — no domain filter
    return schema


def extract_text_and_citations(response) -> tuple[str, list[str]]:
    """Pull plain text and any web result URLs from a response."""
    texts = []
    citations = []
    for block in response.content:
        block_type = getattr(block, "type", None)
        if block_type == "text":
            texts.append(block.text)
        elif block_type == "web_search_result":
            url = getattr(block, "url", None) or getattr(block, "source", None)
            if url:
                citations.append(url)
    return "\n".join(texts), citations


def run_search(
    client, model: str, question: str, schema: dict
) -> tuple[str, list[str]]:
    """Run the web search tool with the given question and return the answer text and citations."""
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": question}],
        tools=[schema],
    )
    return extract_text_and_citations(response)


# ── UI ────────────────────────────────────────────────────────────────────────


def main():
    """Main Streamlit app function"""
    st.set_page_config(page_title="Medical Research Assistant", layout="centered")
    st.title("Medical Research Assistant")
    st.markdown(
        "Ask any medical or health question. Answers are grounded in web-searched, "
        "cited sources via the Anthropic **`web_search`** tool."
    )

    model = st.sidebar.text_input("Model", value="claude-sonnet-4-5")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Search scope**")
    mode = st.sidebar.selectbox(
        "Domain restriction",
        [
            "NIH only (nih.gov)",
            "Trusted health sources",
            "General (no restrictions)",
            "Custom",
        ],
    )
    custom_allowed = ""
    custom_blocked = ""
    if mode == "Custom":
        custom_allowed = st.sidebar.text_input(
            "Allowed domains (comma-separated)", placeholder="nih.gov, who.int"
        )
        custom_blocked = st.sidebar.text_input(
            "Blocked domains (comma-separated)", placeholder="example.com"
        )

    max_uses = st.sidebar.slider(
        "Max web searches per query", min_value=1, max_value=10, value=5
    )

    # Domain info badge
    schema = build_search_schema(mode, custom_allowed, custom_blocked, max_uses)
    allowed = schema.get("allowed_domains")
    blocked = schema.get("blocked_domains")
    if allowed:
        st.sidebar.success(f"✓ Restricted to: {', '.join(allowed)}")
    if blocked:
        st.sidebar.warning(f"✗ Blocked: {', '.join(blocked)}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Example questions**")
    examples = [
        "What are the most effective treatments for Type 2 diabetes?",
        "What does research say about the gut-brain connection?",
        "What are NIH guidelines for managing hypertension?",
        "What does evidence say about intermittent fasting and longevity?",
        "Latest findings on Alzheimer's prevention?",
    ]
    for ex in examples:
        if st.sidebar.button(ex, key=ex):
            st.session_state["prefill"] = ex

    # Main input
    prefill = st.session_state.pop("prefill", "")
    question = st.text_area(
        "Your question",
        value=prefill,
        height=100,
        placeholder="E.g. What are the most effective treatments for Type 2 diabetes?",
    )

    if st.button("Search & Answer", type="primary", disabled=not question.strip()):
        with st.spinner("Searching and composing answer…"):
            try:
                client = Anthropic()
                answer, citations = run_search(client, model, question.strip(), schema)
            except Exception as e:
                st.error(f"Error: {e}")
                return

        st.markdown("---")
        st.markdown("### Answer")
        st.markdown(answer if answer.strip() else "_No text response returned._")

        if citations:
            st.markdown("### Sources")
            for url in citations:
                st.markdown(f"- [{url}]({url})")

        with st.expander("Schema used for this query"):
            st.json(schema)


if __name__ == "__main__":
    main()

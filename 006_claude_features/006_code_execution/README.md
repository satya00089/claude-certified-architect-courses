# Code Execution — Streamlit demo

This folder contains the `code_execution.ipynb` notebook demonstrating the
code-execution and files APIs together. The notebook shows how to upload files
to the Anthropic Files API and then invoke the Code Execution tool to run code
against the uploaded file (container upload pattern).

Quick start

1. Create a `.env` file with your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-...
```

2. (Optional) activate your project's virtualenv.

3. Install the required packages:

```powershell
pip install streamlit python-dotenv anthropic
```

4. Run the demo:

```powershell
streamlit run 006_claude_features/006_code_execution/streamlit_app.py
```

Notes

- The Streamlit demo uploads the chosen file to the Anthropic Files API and
  then sends a `container_upload` block that references the uploaded file id in
  the conversation messages (matching the examples in
  `code_execution.ipynb`).
- The demo configures the Anthropic client with the beta headers required for
  code execution and the files API. Ensure your API key has access to these
  features.
- The helper `chat()` ensures `max_tokens` is larger than the `thinking_budget`
  when `thinking` is enabled.

If you'd like, I can also start this Streamlit app for you now.

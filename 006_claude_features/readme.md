# 006_claude_features — What to expect

This folder contains small demos and notebooks that showcase selected Anthropic
features used in the course. Each subfolder either contains a notebook, a
Streamlit demo, or both. The purpose of these examples is to be runnable
reference code you can experiment with locally.

Quick overview of folders/demos

- `001_extended_thinking` — Extended Thinking demo (Streamlit + notebook). Shows
	how the `thinking` parameter can be enabled and how redacted-thinking
	behavior is demonstrated. Run the Streamlit app at:
	`006_claude_features/001_extended_thinking/thinking.py`.
- `002_image_support` — Image demo: upload images, encode as base64 image
	blocks and send to the API. Streamlit app: `002_image_support/images.py`.
- `003_pdf_support` — PDF demo: upload PDF files and send as document blocks.
	Streamlit app: `003_pdf_support/pdf.py`.
- `004_citations` — Citations demo: upload or paste documents and request
	citation-enabled document analysis. Streamlit app:
	`004_citations/citations.py`.
- `005_caching` — Notebook showing patterns for caching tool calls and
	streaming partial results. See `005_caching/caching.ipynb`.
- `006_code_execution` — Code Execution + Files API demo. Upload a file and
	invoke the code-execution tool. Streamlit app:
	`006_code_execution/code_execution.py`.

Prerequisites

- A Python virtual environment. Activate it before running Streamlit.
- A `.env` file in the repository root (or in each demo folder) with your
	Anthropic key:

```
ANTHROPIC_API_KEY=sk-...
```

- Install the common dependencies used by the Streamlit demos:

```powershell
pip install streamlit python-dotenv anthropic
```

Quick run (example)

```powershell
& .venv\Scripts\Activate.ps1
pip install streamlit python-dotenv anthropic
streamlit run 006_claude_features/002_image_support/streamlit_app.py
```

Important notes & expectations

- API keys and access: Some demos (notably code execution and files API)
	require beta/privileged access. The `006_code_execution` Streamlit app
	configures the client with beta headers — make sure your API key has the
	required permissions before using that demo.
- Thinking vs tokens: The demos include a `thinking` toggle with a
	`thinking_budget` slider. When `thinking` is enabled the examples ensure
	`max_tokens` is kept greater than the thinking budget. If you modify the
	code, ensure any custom `max_tokens` you set is strictly greater than the
	`thinking_budget` to avoid API errors.
- Magic test string: The special redacted-thinking trigger is intentionally
	kept only in the Extended Thinking demo. The image/pdf/citations demos do
	not expose this magic trigger (they instead provide normal send/submit
	controls).
- File uploads & privacy: Uploaded files are sent to the Anthropic Files API
	in some demos. Do NOT upload sensitive or private files to these demos.
	Treat this workspace as an experimentation environment.
- Code execution caution: The code-execution demo uploads files and asks the
	remote tool to execute code. Do not upload secrets or files you wouldn't
	want run remotely. Understand the security and privacy implications.

If you'd like, I can start any of the Streamlit demos for you, or add a
`requirements.txt` for each demo. Which demo should I run or improve next?


# Structured Data Playground

Demonstrates how to produce clean structured outputs from Claude using assistant-prefill + stop sequences.

Files
- `structured_data.py`: Streamlit app showing the prefill + stop sequence technique.
- `structured_data.ipynb`: Notebook explaining and demonstrating the technique.
- `requirements.txt`: Python dependencies for the demo.

Quick start

1. Create a `.env` file in this folder with your Anthropic key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

2. Install dependencies (preferably in a virtualenv):

```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:

```bash
streamlit run structured_data.py
```

Notes

- For JSON and code formats, the app pre-fills the assistant message with a code fence (e.g., ` ```json `) and uses `stop_sequences=["```"]` to prevent trailing commentary.
- After generation, JSON output can be parsed with `json.loads(result.strip())` to obtain a native object.
- This technique works for many structured formats where Claude would otherwise add explanatory text.

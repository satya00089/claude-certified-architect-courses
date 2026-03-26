# Streaming Playground

Demo showing how to stream responses from Claude and present them to users in real time.

Files
- `streaming.py`: Streamlit app that demonstrates incremental response streaming.
- `streaming.ipynb`: Notebook with background and example usage.
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
streamlit run streaming.py
```

Notes

- Toggle `Enable streaming` in the app to switch between chunked real-time updates and a standard single-response call.
- Use `stream.text_stream` to get content chunks and `stream.get_final_message()` to retrieve the assembled message for storage.

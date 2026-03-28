# Temperature Playground

A small interactive demo showing how the `temperature` parameter affects Claude's outputs.

Files
- `temperature.py`: Streamlit app to interactively adjust temperature and see results.
- `temperature.ipynb`: Notebook with background and example usage.
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
streamlit run temperature.py
```

4. Open `temperature.ipynb` with Jupyter Notebook or Jupyter Lab to view the notebook examples.

Notes
- Use low temperatures (0.0 - 0.3) for deterministic/factual outputs.
- Use medium (0.4 - 0.7) for balanced creativity and coherence.
- Use high (0.8 - 1.0) for brainstorming and creative outputs.

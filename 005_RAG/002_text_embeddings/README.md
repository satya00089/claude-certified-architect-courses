# Text Embeddings

This folder demonstrates how to turn text chunks into **vector embeddings** using the
VoyageAI embedding model — the step that makes semantic retrieval possible in a RAG pipeline.

## What are embeddings?

An embedding is a fixed-length list of floating-point numbers (a vector) that represents
the semantic meaning of a piece of text. Texts with similar meaning produce vectors that
are close together in high-dimensional space; unrelated texts are far apart.

```
"leg muscle exercises"  →  [0.021, -0.143, 0.887, ...]   ◄─ close together
"quadriceps training"   →  [0.019, -0.138, 0.901, ...]   ◄─

"quarterly earnings"    →  [-0.512, 0.334, -0.071, ...]  ◄─ far away
```

This property allows a RAG system to retrieve the most relevant document chunks for any
natural-language query without needing exact keyword matches.

## Why VoyageAI?

[VoyageAI](https://www.voyageai.com/) provides state-of-the-art embedding models optimised
for retrieval tasks. The notebook uses `voyage-3-large`, which supports two `input_type`
modes important for RAG:

| `input_type` | When to use |
|--------------|-------------|
| `"document"` | When embedding chunks at **index time** (store in vector DB) |
| `"query"` | When embedding a **user question** at retrieval time |

Separating document and query embeddings improves retrieval accuracy because the model
is optimised for the asymmetry between a long document chunk and a short user question.

## How embeddings fit in a RAG pipeline

```
Source document
      │
      ▼
 chunk_by_section()          ← splits on Markdown ## headings
      │
      ▼
 generate_embedding(chunk, input_type="document")
      │
      ▼
 Vector database (store vectors + original text)

                     ┌─ At query time ─────────────────────────┐
                     │                                         │
                     │  User question                          │
                     │       │                                 │
                     │       ▼                                 │
                     │  generate_embedding(q, input_type="query")
                     │       │                                 │
                     │       ▼                                 │
                     │  cosine_similarity(query_vec, all_doc_vecs)
                     │       │                                 │
                     │       ▼                                 │
                     │  Top-k chunks → LLM context             │
                     └─────────────────────────────────────────┘
```

## Key function

```python
def generate_embedding(text, model="voyage-3-large", input_type="query"):
    result = client.embed([text], model=model, input_type=input_type)
    return result.embeddings[0]   # returns a list of floats
```

- Returns a single embedding vector for one piece of text.
- Call with `input_type="document"` for chunks, `input_type="query"` for questions.
- Batch calls (`client.embed([text1, text2, ...])`) are more efficient for indexing many chunks.

## Setup

1. Get a VoyageAI API key from [dash.voyageai.com](https://dash.voyageai.com/).
2. Add it to `.env`:

```
VOYAGE_API_KEY=your_key_here
```

3. Install dependencies:

```bash
pip install -r 005_RAG/002_text_embeddings/requirements.txt
```

4. Run the notebook `embeddings.ipynb`.

## Files

| File | Description |
|------|-------------|
| `embeddings.ipynb` | Notebook — section chunking + embedding generation |
| `report.md` | Sample multi-section report used as input document |
| `requirements.txt` | Python dependencies (`voyageai`, `anthropic`, etc.) |

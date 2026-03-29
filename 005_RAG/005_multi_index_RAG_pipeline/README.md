# Multi-index RAG pipeline

This folder contains an interactive notebook that demonstrates a minimal
multi-index Retrieval-Augmented Generation (RAG) pipeline. The implementation
shows how to:

- Chunk a markdown report by section
- Build a lexical BM25 index and an embedding-based VectorIndex
- Combine results across indexes using Reciprocal Rank Fusion (RRF) in a
  `Retriever` class
- Query the fused retriever to return the best-matching document chunks

Contents
- `multi_index_RAG_pipeline.ipynb` — main notebook with the implementation and
  runnable examples

Prerequisites
- Python 3.8+
- If present, install pinned dependencies:

```
pip install -r requirements.txt
```

If there is no `requirements.txt` in this folder, install the common packages used
in the notebook:

```
pip install python-dotenv voyageai
```

Quickstart
1. Create & activate a virtual environment (Windows example):

```
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies (see above).

3. Run the notebook:

```
jupyter notebook multi_index_RAG_pipeline.ipynb
```

Overview of key components
- `chunk_by_section(document_text)` — splits a markdown file into section chunks
- `generate_embedding(chunks)` — calls the configured embedding client to
  return vectors for text inputs
- `VectorIndex` — lightweight in-memory vector store (supports cosine or
  euclidean distance)
- `BM25Index` — simple BM25 lexical index with tokenization based on a
  regex tokenizer
- `Retriever` — combines results from both indexes using RRF and returns top-k
  fused results

Example usage (copy into a notebook cell)

```python
from dotenv import load_dotenv
import voyageai

load_dotenv()
client = voyageai.Client()

with open('report.md', 'r') as f:
    text = f.read()

chunks = chunk_by_section(text)

vector_index = VectorIndex(embedding_fn=generate_embedding)
bm25_index = BM25Index()
retriever = Retriever(bm25_index, vector_index)

retriever.add_documents([{'content': c} for c in chunks])

results = retriever.search("what happened with INC-2023-Q4-011?", k=3)
for doc, score in results:
    print(f"Score: {score:.4f}\nContent:\n{doc['content']}\n{'-'*50}\n")
```

Notes
- Put any API keys or configuration needed by your embedding provider into a
  `.env` file (the notebook uses `python-dotenv`).
- `generate_embedding` in the notebook uses the configured `voyageai.Client()`;
  consult the notebook for exact client usage and authentication.
- Vector embeddings must have consistent dimensionality across documents.
- Consider replacing the simple tokenizer in `BM25Index` with a more robust
  tokenizer (spaCy, Hugging Face tokenizers, etc.) for production use.

Next steps / improvements
- Extract notebook code into a reusable Python module
- Add unit tests for `VectorIndex`, `BM25Index`, and `Retriever`
- Cache embeddings to reduce API calls and costs

License
Follow the repository license.

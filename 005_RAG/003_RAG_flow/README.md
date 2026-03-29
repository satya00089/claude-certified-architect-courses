# RAG Implementation (Vector Index + Embeddings)

This folder contains a minimal Retrieval-Augmented Generation (RAG) implementation used
in `rag_impl.ipynb`. It demonstrates the end-to-end flow: chunking source documents,
creating embeddings for chunks, storing vectors in a simple in-memory index, and
retrieving the most relevant chunks for a user query.

## Overview

RAG combines an LLM with a retrieval layer so the model can answer questions using
external data. The notebook implements a small, educational pipeline:

1. Chunk source documents (e.g., Markdown `report.md`) using `chunk_by_section`.
2. Generate embeddings for each chunk with VoyageAI (`generate_embedding`).
3. Store embeddings + chunk text in a lightweight `VectorIndex` (in-memory).
4. At query time, embed the user question and search the index for top-k similar chunks.
5. Provide those chunks as context to the LLM to generate a grounded answer.

## Files

- `rag_impl.ipynb` — The main notebook showing the full RAG flow.
- `report.md` — Sample multi-section report used as the input document.

## Key components (reference)

- `chunk_by_section(document_text)` — splits input on `\n## ` headings.
- `generate_embedding(text, model="voyage-3-large", input_type="query")`
  - Supports batching. Use `input_type="document"` when indexing and
    `input_type="query"` when embedding user questions.
- `VectorIndex` — an in-memory vector store with add/search functionality.
  - `add_vector(vector, document)` stores the vector and its document metadata.
  - `search(query_vector, k=1)` returns the top-k (document, distance) tuples.

## Sample usage

Indexing (run once to build the index):

```python
with open("./report.md","r") as f:
    text = f.read()

chunks = chunk_by_section(text)
# Batch-embed all chunks to avoid rate limits
embeddings = generate_embedding(chunks, model="voyage-3-large", input_type="document")

store = VectorIndex(embedding_fn=lambda t: generate_embedding(t, input_type="document"))
for chunk, emb in zip(chunks, embeddings):
    store.add_vector(vector=emb, document={"content": chunk})
```

Querying:

```python
user_embedding = generate_embedding("What did the software engineering dept do last year?", input_type="query")
results = store.search(user_embedding, k=2)
for doc, dist in results:
    print(f"Distance: {dist:.4f}\nContent: {doc['content']}\n{'-'*40}")
```

Then pass the retrieved `doc['content']` pieces as context to your LLM prompt for a grounded answer.

## Practical notes & tips

- Embedding consistency: use the same model and vector dimensionality for document and query
  embeddings. Mismatched dimensions will cause errors in the `VectorIndex`.
- Batch embeddings: call the embedding API with a list of texts to avoid rate limits and
  improve throughput.
- Distance metric: `cosine` is generally best for semantic similarity; the `VectorIndex`
  supports `cosine` and `euclidean` distances.
- Persistence: this example uses an in-memory index. For production, persist vectors
  in a vector DB (FAISS, Milvus, Pinecone) for durability and scale.
- Chunking: prefer semantic or section-based chunking for reports and structured text.
  For noisy text, sentence-based chunking with overlap helps preserve context.
- Choose `k` (top-k) based on your context window size — fewer, higher-quality chunks
  usually produce better results than many low-relevance chunks.

## Run instructions

1. Install dependencies (if not already installed):

```bash
pip install voyageai python-dotenv
```

2. Add your VoyageAI key to `.env` (see parent folders) as `VOYAGE_API_KEY`.
3. Open and run `rag_impl.ipynb` in a Jupyter environment.

## Next steps / Improvements

- Persist the vectors to a production vector store (FAISS / Pinecone / Milvus).
- Improve chunking with a semantic chunker that splits based on embedding distance drops.
- Add metadata (title, section, source file, offsets) to documents for richer retrieval.
- Implement re-ranking of retrieved chunks using the LLM before final answer composition.

---

See the notebook: [rag_impl.ipynb](rag_impl.ipynb)

# Text Chunking Strategies

This folder demonstrates three core strategies for splitting documents into chunks before
embedding them in a Retrieval-Augmented Generation (RAG) pipeline. Choosing the right
strategy directly affects retrieval quality and answer accuracy.

## What is chunking and why does it matter?

Large language models have a fixed context window. RAG works by:

1. Splitting source documents into **chunks**.
2. Embedding each chunk as a vector and storing them in a vector database.
3. At query time, retrieving the most semantically similar chunks.
4. Feeding those chunks as context to the model.

Chunk quality is the single biggest lever in RAG performance:

- Chunks too **small** → lose context, incomplete answers.
- Chunks too **large** → dilute relevance signal, waste tokens, exceed context limits.
- Chunks that break **mid-thought** → confuse the model and hurt retrieval precision.

## Strategies covered

### 1. Character-based (`chunk_by_char`)

Splits text every N characters with an optional overlap.

```python
chunk_by_char(text, chunk_size=150, chunk_overlap=20)
```

| Pros | Cons |
|------|------|
| Simple, predictable size | Cuts mid-sentence or mid-word |
| Works on any text | Poor semantic coherence |
| Easy to control token budget | Overlap adds redundancy |

Best for: quick prototyping, plain text with no clear structure.

---

### 2. Sentence-based (`chunk_by_sentence`)

Groups N sentences per chunk with a 1-sentence overlap, splitting on `.`, `!`, or `?`.

```python
chunk_by_sentence(text, max_sentences_per_chunk=5, overlap_sentences=1)
```

| Pros | Cons |
|------|------|
| Preserves grammatical units | Chunk size varies with sentence length |
| Better semantic coherence | Can still break paragraphs arbitrarily |
| Overlap keeps adjacent context | Regex splits can fail on abbreviations |

Best for: prose documents, news articles, research summaries.

---

### 3. Section-based (`chunk_by_section`)

Splits Markdown documents on `## ` section headers, keeping each section intact.

```python
chunk_by_section(document_text)   # splits on "\n## "
```

| Pros | Cons |
|------|------|
| Semantically meaningful units | Requires structured Markdown |
| No arbitrary mid-thought breaks | Sections may be very long |
| Natural retrieval granularity | Not applicable to plain text |

Best for: reports, documentation, wikis — any well-structured Markdown file.

---

## Choosing a strategy

```
Is the document structured Markdown with ## headings?
   └─ Yes → chunk_by_section
   └─ No  → Is it well-written prose?
               └─ Yes → chunk_by_sentence
               └─ No  → chunk_by_char (fallback)
```

For production RAG pipelines, consider pairing one of these with a **semantic chunker**
that splits on embedding-distance drops for even better coherence.

## Files

| File | Description |
|------|-------------|
| `chunking.ipynb` | Notebook with all three strategies applied to `report.md` |
| `report.md` | Sample multi-section research report used as input |

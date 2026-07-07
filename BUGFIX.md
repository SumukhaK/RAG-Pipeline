# bugfix branch — changes log

This branch tracks targeted bug fixes found while reviewing `src/`. Each entry below was
diagnosed by reading the relevant code first, then fixed as a single, isolated commit and
verified before moving to the next one. No unrelated refactoring was included.

## 1. Broken import path in `src/search.py`

**Commit:** `977f6a8`

`RAGSearch.__init__`'s fallback branch (used when no persisted FAISS index exists yet) did:

```python
from data_loader import load_all_documents
```

Every other import in the file uses the `src.` package prefix (e.g.
`from src.vectorstore import FaissVectorStore`). The missing prefix meant this line raised
`ImportError` the moment it actually ran — i.e. on a fresh checkout with no prebuilt
`faiss_store/`.

**Fix:** changed to `from src.data_loader import load_all_documents`.

## 2. Duplicate embedding model load

**Commit:** `977f6a8`

`FaissVectorStore.__init__` already loads its own `SentenceTransformer(embedding_model)`
instance. `build_from_documents()` then constructed an `EmbeddingPipeline`, whose `__init__`
loaded a **second**, independent `SentenceTransformer` of the same model — so every ingestion
run loaded the model into memory twice.

**Fix:** `EmbeddingPipeline` now accepts an optional `model` constructor argument. When
provided, it reuses that instance instead of loading a new one. `FaissVectorStore` passes its
own `self.model` in, so the model is loaded exactly once per run. Standalone use of
`EmbeddingPipeline` without a preloaded model is unaffected.

## 3. Hardcoded, empty Groq API key

**Commit:** `3efdd54`

`RAGSearch.__init__` called `load_dotenv()` but then set:

```python
groq_api_key = ""
```

so `ChatGroq` was always initialized with no credentials, regardless of what was in `.env`.
This was the only place in the codebase that didn't read the key from the environment — the
notebook and README already used `os.getenv("GROQ_API_KEY")` correctly.

**Fix:** read the key via `os.getenv("GROQ_API_KEY")` and raise a clear `ValueError` if it's
unset, instead of silently continuing with an empty credential.

## Verification

- All three fixes were verified by running the actual code (not just reading it), using a real
  `GROQ_API_KEY` in a local, gitignored `.env` file (never committed — confirmed with
  `git check-ignore` and `git status` after each change).
- `src/data_loader.py`, `src/embeddings.py`, `src/vectorstore.py`, and `src/search.py` were
  import-checked together after fix #1 and #2.
- `RAGSearch().search_and_summarize(...)` was run end-to-end against the existing persisted
  FAISS store after fix #3, making a live Groq API call and returning a real answer.
- `git status` was checked after every change to confirm only the intended file(s) were
  modified — no regenerated vector store or other side effects.

## Still open (not part of this branch)

From the same review, two further issues were identified but are out of scope for this branch:

- `FaissVectorStore.build_from_documents()` stores only `{"text": chunk.page_content}` as
  metadata, discarding the source file and page number that the document loaders attach —
  retrieved chunks currently carry no citation information.
- Two disconnected vector stores exist in the repo (a ChromaDB store under `data/vector_store/`
  from the notebook, and the FAISS store under `faiss_store/` used by `src/`) with no single
  ingestion pipeline producing both.

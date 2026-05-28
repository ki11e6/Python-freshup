# Day 4 — FastAPI Deep + RAG Ingestion (Saturday, 8h)

**Time:** 8 hours · **Goal:** by end of day, you can run `uv run python scripts/ingest.py` and have a populated Chroma store you can `similarity_search` against.

---

## Quick reference (interview-day skim)

| Question | Answer |
|---|---|
| **What's RAG?** | Retrieval-Augmented Generation — retrieve relevant context from a knowledge base, stuff it into the prompt, then generate. Reduces hallucination, grounds answers, lets the LLM use private/recent data. |
| **Why chunk?** | LLMs have context limits; embeddings are most useful on focused passages; retrieval ranks chunks not documents. |
| **Chunk size trade-off** | Too small → loses context, multiple chunks needed; too large → less precise retrieval, more tokens per query. Default: 1000 chars, 200 overlap. |
| **What's overlap?** | Each chunk shares some text with neighbors. Prevents losing info that sits at a chunk boundary. |
| **Embedding** | Maps text → fixed-length vector (1536 dims for `text-embedding-3-small`) where similar text → nearby vectors. |
| **Vector store** | Database optimized for ANN (approximate nearest neighbor) search over embeddings. Chroma, Pinecone, Weaviate, pgvector. |
| **Similarity metric** | Usually cosine similarity. Sometimes dot product or L2. |
| **Top-k retrieval** | Get the `k` most-similar chunks for a query. Typical k=4-8. |
| **MMR vs similarity** | MMR (Maximal Marginal Relevance) rewards diversity — avoids returning 5 chunks saying the same thing. |
| **Hybrid search** | Combine dense (embedding) + sparse (BM25) retrieval. Best of semantic + keyword. |

---

## Block A — FastAPI deep (3h)

You already built `/health` and stub `/ask` on Day 3. Now structure for growth.

### A1. Router-based project layout (45 min)

```
docsgpt/
├── pyproject.toml
├── .env
├── docsgpt/
│   ├── __init__.py
│   ├── main.py              # creates app, includes routers
│   ├── config.py            # Settings
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── ask.py
│   │   └── health.py
│   ├── rag/                 # populated today
│   │   └── __init__.py
│   ├── agent/               # populated Day 5
│   │   └── __init__.py
│   └── deps.py              # shared FastAPI dependencies
```

`docsgpt/main.py`:
```python
from fastapi import FastAPI
from docsgpt.routers import ask, health

app = FastAPI(title="DocsGPT", version="0.1.0")
app.include_router(health.router)
app.include_router(ask.router)
```

`docsgpt/routers/health.py`:
```python
from fastapi import APIRouter

router = APIRouter(tags=["meta"])

@router.get("/health")
async def health():
    return {"status": "ok"}
```

`docsgpt/routers/ask.py`:
```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

router = APIRouter(prefix="", tags=["rag"])

class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    k: int = Field(default=4, ge=1, le=20)

class AskResponse(BaseModel):
    answer: str
    sources: list[dict]

@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    # Day 4 end: still a stub. Day 5 fills this in.
    return AskResponse(answer="stub", sources=[])
```

### A2. Settings & config (15 min)

`docsgpt/config.py`:
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-small"
    chroma_dir: str = "data/chroma"
    tavily_api_key: str | None = None
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str = "https://cloud.langfuse.com"

    model_config = {"env_file": ".env", "extra": "ignore"}

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

`@lru_cache` makes this a singleton — Settings only constructed once.

### A3. Error handling + middleware (30 min)

```python
# docsgpt/main.py
from fastapi import Request
from fastapi.responses import JSONResponse
import logging, time

log = logging.getLogger("docsgpt")

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.middleware("http")
async def add_latency_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-response-time-ms"] = f"{(time.perf_counter()-start)*1000:.1f}"
    return response
```

### A4. Lifespan (startup/shutdown) (15 min)

For loading the vector store **once at startup**, not per-request:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    app.state.vector_store = build_vector_store()
    yield
    # shutdown — nothing for Chroma file mode
    log.info("shutting down")

app = FastAPI(lifespan=lifespan)
```

> This is a context manager (Day 2!) used as a decorator. The pattern repeats.

### A5. Dependency injection patterns (45 min)

```python
# docsgpt/deps.py
from fastapi import Depends, Request
from docsgpt.config import Settings, get_settings

def get_vector_store(request: Request):
    """Pull from app.state — populated at startup."""
    return request.app.state.vector_store

def get_openai_client(settings: Settings = Depends(get_settings)):
    from openai import OpenAI
    return OpenAI(api_key=settings.openai_api_key)
```

Use in route:
```python
@router.post("/ask")
async def ask(
    req: AskRequest,
    vs = Depends(get_vector_store),
    settings: Settings = Depends(get_settings),
):
    ...
```

Dependencies are resolved per-request (unless wrapped in `lru_cache`). They can themselves depend on other dependencies — FastAPI builds a DAG.

### A6. Testing (30 min)

```python
# tests/test_routes.py
from fastapi.testclient import TestClient
from docsgpt.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_ask_validates_empty():
    r = client.post("/ask", json={"question": ""})
    assert r.status_code == 422   # Pydantic validation error
```

Run: `uv run pytest -v`.

---

## Block B — Pydantic v2 deep dive (1h)

You'll use Pydantic for: API contracts, settings, LLM tool args, structured outputs. Get fluent.

### Field constraints
```python
from pydantic import BaseModel, Field, EmailStr, AnyUrl

class Item(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)             # > 0
    tags: list[str] = Field(default_factory=list, max_length=10)
    email: EmailStr | None = None
    homepage: AnyUrl | None = None
```

### Validators

```python
from pydantic import BaseModel, field_validator, model_validator
from typing_extensions import Self

class Range(BaseModel):
    low: int
    high: int

    @field_validator("low", "high")
    @classmethod
    def non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("must be non-negative")
        return v

    @model_validator(mode="after")
    def check_order(self) -> Self:
        if self.low > self.high:
            raise ValueError("low must be ≤ high")
        return self
```

### Computed fields
```python
from pydantic import computed_field

class Box(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height
```

`Box(width=2, height=3).model_dump()` → `{"width": 2, "height": 3, "area": 6}`. Included in JSON schema.

### Serialization
```python
m.model_dump()                          # dict
m.model_dump(exclude={"secret"})        # drop fields
m.model_dump(exclude_none=True)         # drop None values
m.model_dump_json()                     # JSON string
Item.model_validate({"name": "x", "price": 1.0})       # from dict
Item.model_validate_json('{"name":"x","price":1.0}')   # from JSON
```

### Aliases (for external APIs)
```python
class ApiUser(BaseModel):
    user_id: int = Field(alias="userId")
    full_name: str = Field(alias="fullName")
    model_config = {"populate_by_name": True}

ApiUser.model_validate({"userId": 1, "fullName": "x"})
```

---

## Block C — Project scaffold (1h)

```bash
cd docsgpt

uv add fastapi uvicorn pydantic-settings python-dotenv
uv add langchain langchain-openai langchain-chroma langchain-text-splitters langchain-community
uv add openai chromadb httpx beautifulsoup4 lxml
uv add --dev pytest httpx mypy
```

Create `.env`:
```
OPENAI_API_KEY=sk-...
```

`.gitignore`:
```
.venv/
.env
__pycache__/
*.pyc
data/chroma/
.pytest_cache/
.mypy_cache/
*.egg-info/
```

### Verify
```bash
uv run uvicorn docsgpt.main:app --reload
# open http://localhost:8000/docs
# POST /ask with {"question": "test"} → should return stub
```

### Initialize git + first commit
```bash
git init
git add .
git commit -m "feat: initial scaffold with FastAPI routers and Pydantic settings"
```

---

## Block D — RAG ingestion pipeline (3h)

This is the heart of Saturday. By end of this block: `uv run python scripts/ingest.py` builds a persisted Chroma index.

### D1. Load (45 min)

`docsgpt/rag/load.py`:
```python
from langchain_community.document_loaders import SitemapLoader, RecursiveUrlLoader
from langchain_core.documents import Document
import bs4

def html_extractor(html: str) -> str:
    """Strip nav/footer/sidebar — keep main content only."""
    soup = bs4.BeautifulSoup(html, "lxml")
    main = soup.find("main") or soup.find("article") or soup
    for tag in main.select("nav, footer, aside, .sidebar, script, style"):
        tag.decompose()
    return main.get_text(separator="\n", strip=True)

def load_fastapi_docs(max_pages: int = 150) -> list[Document]:
    """Crawl fastapi.tiangolo.com — limit pages for cost."""
    loader = RecursiveUrlLoader(
        url="https://fastapi.tiangolo.com/",
        max_depth=4,
        extractor=html_extractor,
        prevent_outside=True,
    )
    docs = []
    for i, doc in enumerate(loader.lazy_load()):
        if i >= max_pages:
            break
        doc.metadata["doc_site"] = "fastapi"
        docs.append(doc)
    return docs

def load_langchain_docs(max_pages: int = 150) -> list[Document]:
    loader = RecursiveUrlLoader(
        url="https://python.langchain.com/docs/",
        max_depth=3,
        extractor=html_extractor,
        prevent_outside=True,
    )
    docs = []
    for i, doc in enumerate(loader.lazy_load()):
        if i >= max_pages:
            break
        doc.metadata["doc_site"] = "langchain"
        docs.append(doc)
    return docs
```

> **Why `RecursiveUrlLoader` and not `SitemapLoader`?** Sitemap parsing varies by site. Recursive crawl is reliable. Cap with `max_depth` and `max_pages` to control cost.

### D2. Chunk (30 min)

`docsgpt/rag/chunk.py`:
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def split_documents(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,   # preserves position in source doc
        separators=["\n\n", "\n", ". ", " ", ""],  # try big breaks first
    )
    return splitter.split_documents(docs)
```

**Why these defaults:**
- 1000 chars ≈ 200 tokens — fits ~4 chunks in 1k token context budget
- 200 overlap = 20% — typical, keeps cross-chunk context
- Separators tried in order — splits on paragraph break before sentence before space

**Chunking strategies (for interview):**
- **Fixed-size** — `CharacterTextSplitter`. Simplest, ignores structure.
- **Recursive** — try multiple separators in order. **Default for prose.**
- **Markdown-aware** — `MarkdownHeaderTextSplitter`. Splits at headers.
- **Code-aware** — `RecursiveCharacterTextSplitter.from_language(Language.PYTHON, ...)`.
- **Semantic** — split on embedding distance jumps between adjacent sentences. Expensive but quality-focused.

### D3. Embed + store (45 min)

`docsgpt/rag/store.py`:
```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from docsgpt.config import get_settings

def get_embeddings() -> OpenAIEmbeddings:
    s = get_settings()
    return OpenAIEmbeddings(
        model=s.embedding_model,
        api_key=s.openai_api_key,
    )

def get_vector_store() -> Chroma:
    """Persistent local Chroma — connects to existing or creates new."""
    s = get_settings()
    return Chroma(
        collection_name="docsgpt",
        embedding_function=get_embeddings(),
        persist_directory=s.chroma_dir,
    )

def ingest(splits: list[Document]) -> int:
    vs = get_vector_store()
    # batch by 100 to avoid huge requests
    n = 0
    for i in range(0, len(splits), 100):
        batch = splits[i:i+100]
        vs.add_documents(batch)
        n += len(batch)
    return n
```

### D4. Ingest CLI script (15 min)

`scripts/ingest.py`:
```python
"""Run: uv run python scripts/ingest.py"""
import logging
from docsgpt.rag.load import load_fastapi_docs, load_langchain_docs
from docsgpt.rag.chunk import split_documents
from docsgpt.rag.store import ingest

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("ingest")

def main():
    log.info("loading FastAPI docs…")
    docs = load_fastapi_docs(max_pages=150)
    log.info(f"  → {len(docs)} pages")

    log.info("loading LangChain docs…")
    docs += load_langchain_docs(max_pages=150)
    log.info(f"  → total {len(docs)} pages")

    log.info("chunking…")
    splits = split_documents(docs)
    log.info(f"  → {len(splits)} chunks")

    log.info("embedding + storing in Chroma…")
    n = ingest(splits)
    log.info(f"✓ ingested {n} chunks")

if __name__ == "__main__":
    main()
```

### D5. Verify (15 min)

```bash
uv run python scripts/ingest.py
# wait ~5-15 minutes depending on pages
# should print: ✓ ingested ~3000 chunks
```

Smoke test retrieval in REPL:
```bash
uv run python
>>> from docsgpt.rag.store import get_vector_store
>>> vs = get_vector_store()
>>> results = vs.similarity_search("how to add dependency injection in FastAPI?", k=4)
>>> for r in results:
...     print(r.metadata.get("source"), r.page_content[:120])
```

You should see chunks from `/tutorial/dependencies/...`. If you don't, debug before stopping.

### D6. Commit (5 min)
```bash
git add docsgpt/ scripts/
git commit -m "feat: RAG ingestion pipeline with Chroma + OpenAI embeddings"
```

---

## End-of-Day-4 self-check

- [ ] You can run `uvicorn docsgpt.main:app --reload` and see `/docs`
- [ ] `POST /ask` returns the stub response with 422 on invalid input
- [ ] `uv run python scripts/ingest.py` completes and prints chunk count
- [ ] `similarity_search` in REPL returns relevant chunks for a FastAPI question
- [ ] You can explain: why chunk size 1000/200, why recursive splitter, what does Chroma store

## Stretch (only if you finish early)

- Add a metadata filter: `vs.similarity_search(q, filter={"doc_site": "fastapi"})`
- Add cost logging: count embedding tokens and print estimated $ at end of ingest

---

## Tomorrow

Sunday turns this into a working chatbot: retrieval chain → streaming response → LangGraph agent → deploy. The hardest day. Sleep well.

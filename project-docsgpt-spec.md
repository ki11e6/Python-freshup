# DocsGPT — Project Spec

A RAG chatbot that answers questions about **FastAPI** and **LangChain** official docs, with sources.

> **Why this project:** self-referential (built with the tools it answers questions about), public clean data, demoable in 60 sec, mirrors your ShopfloorGPT architecture at smaller scope.

---

## Quick reference (interview-day skim)

**Elevator pitch (1 sentence):**
> "DocsGPT is a RAG service over FastAPI and LangChain docs — FastAPI + LangChain + Chroma + LangGraph, with Langfuse traces and an eval set, deployed on Render."

**Architecture in one breath:**
> "Ingest → recursive char chunking (1000/200) → embed with `text-embedding-3-small` → store in Chroma → on query, embed → top-k retrieve → optional LangGraph agent routes between doc-retrieval and web search → stuff into prompt → `gpt-4.1-mini` streams response with cited sources."

**One tradeoff:** "Picked recursive char splitter over semantic chunking — eval score improved by less than 3% but latency doubled on ingest."

**One failure fixed:** "Multi-hop questions ('how do I use Pydantic validators in FastAPI dependencies?') initially missed because retrieval treated it as one query — added query rewriting to fan out into two sub-queries before retrieval."

**Observability:** "Langfuse for trace per request, 10-question eval set, current groundedness ~0.82."

---

## Stack (committed — no debate)

| Layer | Choice | Why |
|---|---|---|
| Web framework | **FastAPI** | The point of the project. Async, Pydantic-native. |
| Validation | **Pydantic v2** | Built into FastAPI. |
| RAG framework | **LangChain** (Python) | What the JD/friend asked for; widely known. |
| Vector store | **Chroma** (local, persistent) | No signup, file-backed, dead simple. |
| Embeddings | **OpenAI `text-embedding-3-small`** | $0.02 / 1M input tokens. 1536 dims. Still the cheap+fast default in May 2026. |
| LLM | **OpenAI `gpt-4.1-mini`** | $0.40 in / $1.60 out per 1M. Sweet spot for RAG quality + cost. Use `gpt-4.1-nano` ($0.10/$0.40) if you want absolute cheapest. |
| Agent | **LangGraph** | 1 router node + 2 tools. Matches ShopfloorGPT. |
| Web search tool | **Tavily** (free tier 1k/month) | For fallback when docs don't cover the question. |
| Observability | **Langfuse** (cloud free / "Hobby" tier) | 50k units/month, 30-day retention. Plenty for demo. |
| Package mgr | **`uv`** | Fast, modern. |
| Container | **Docker** | Single Dockerfile. |
| Deploy | **Render.com** (free) | 750 free instance hours/month per workspace. **Spins down after 15 min of inactivity** (~1 min cold start) — fine for an interview demo, mention this in README. Alt: Fly.io. |

**Verified install + imports (May 2026):**
```bash
pip install langchain langchain-openai langchain-chroma langchain-text-splitters langchain-community
```
```python
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import SitemapLoader, RecursiveUrlLoader
```

**Budget:** ~$1-2 total in OpenAI credits (embeddings basically free; ~$0.004 per query with `gpt-4.1-mini`). Set a $10 hard spend cap in the OpenAI dashboard before starting.

---

## Hard scope cap (DO NOT EXCEED)

| Feature | In | Out |
|---|---|---|
| Doc sites ingested | FastAPI docs + LangChain docs | Anything else |
| Endpoints | `POST /ingest`, `POST /ask`, `GET /health` | Auth, users, billing |
| Storage | Chroma file + env config | Postgres, Redis |
| Frontend | None (curl/Postman + screenshots) | React/Next UI |
| Multi-user | No | Sessions, history |
| Agent nodes | 1 router + 2 tools | Multi-agent orchestration |

> If you find yourself adding "just one more thing" past Sunday afternoon, **stop**. The README and the narrative are worth more than another feature.

---

## File layout

```
docsgpt/
├── pyproject.toml          # uv-managed
├── .env.example
├── .gitignore
├── README.md               # write this last, but treat it as deliverable #1
├── Dockerfile
├── docker-compose.yml      # optional, for local langfuse
├── docsgpt/
│   ├── __init__.py
│   ├── main.py             # FastAPI app entry
│   ├── config.py           # pydantic-settings, loads .env
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── ask.py          # POST /ask
│   │   └── health.py       # GET /health
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── ingest.py       # CLI + functions for loading + chunking
│   │   ├── embed.py        # embedding helper
│   │   ├── store.py        # Chroma wrapper
│   │   └── retrieve.py     # retrieval + prompt build
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py        # LangGraph definition
│   │   └── tools.py        # doc_search, web_search
│   └── observability/
│       └── langfuse.py     # callback setup
├── scripts/
│   └── ingest.py           # `uv run python scripts/ingest.py`
├── data/
│   └── chroma/             # gitignored — vector DB persistence
├── evals/
│   ├── questions.yaml      # 10 hand-written Q+expected sources
│   └── run_eval.py
└── tests/
    ├── test_chunking.py
    └── test_retrieval.py
```

---

## Architecture diagram (ascii, for README)

```
┌──────────┐     ┌──────────────┐     ┌─────────┐     ┌────────┐
│  Client  │───▶│ FastAPI /ask │───▶│ Agent   │───▶│  LLM   │
└──────────┘     └──────────────┘     │ (Graph) │     └────────┘
                       │              └────┬────┘          │
                       │                   │               │
                       ▼                   ▼               ▼
                  ┌─────────┐         ┌─────────┐    ┌──────────┐
                  │Langfuse │         │  Tool:  │    │  Stream  │
                  │ traces  │         │ doc_srch│    │ response │
                  └─────────┘         │ web_srch│    └──────────┘
                                      └────┬────┘
                                           ▼
                                      ┌─────────┐
                                      │ Chroma  │
                                      └─────────┘

Ingestion (offline):
  docs URLs → Loader → RecursiveCharSplitter → Embeddings → Chroma
```

---

## Ingestion pipeline

1. **Load** — `SitemapLoader` or `RecursiveUrlLoader` for FastAPI + LangChain docs (limit pages to keep cost down — e.g. 200 pages each).
2. **Chunk** — `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)`. This is the LangChain official default. Discuss alternatives in README.
3. **Embed** — `OpenAIEmbeddings(model="text-embedding-3-small")` — batch in groups of 100.
4. **Store** — `Chroma(persist_directory="data/chroma", embedding_function=embeddings)` then `.add_documents(splits)`.

**Add metadata to each chunk:** `{"source_url": ..., "title": ..., "doc_site": "fastapi" | "langchain"}` — needed for citation in responses.

---

## Retrieval flow

1. User sends `POST /ask {"question": "...", "k": 4}`.
2. Embed question → query Chroma for top-k chunks.
3. Build prompt:
   ```
   You answer questions about FastAPI and LangChain using only the
   provided context. If the answer isn't in the context, say so.
   Cite sources as [1], [2], ... matching the chunk numbers.

   Context:
   [1] (from {source_url}) {chunk_text}
   [2] ...

   Question: {question}
   ```
4. Stream response via `gpt-4.1-mini`.
5. Return `{answer: str, sources: [{url, title}]}` (non-streamed) or SSE stream.

---

## Agent (LangGraph) — Day 5

One graph, 3 nodes:

```
START
  │
  ▼
┌──────────────────────┐
│ router (LLM call)    │
│ decides: docs / web  │
└──┬────────────┬──────┘
   │            │
   ▼            ▼
┌────────┐  ┌────────┐
│ docs_  │  │ web_   │
│ search │  │ search │
└───┬────┘  └───┬────┘
    └─────┬─────┘
          ▼
   ┌────────────┐
   │ answer LLM │
   └─────┬──────┘
         ▼
        END
```

Router uses `gpt-4.1-mini` with structured output:
```python
class RouteDecision(BaseModel):
    tool: Literal["docs_search", "web_search"]
    reason: str
```

---

## Eval set (Day 5, ~30 min)

Create `evals/questions.yaml` — 10 hand-written Q+expected-source-page pairs. Examples:

```yaml
- q: "How do I add dependency injection in FastAPI?"
  expected_source_contains: "tutorial/dependencies"
- q: "What's the difference between RecursiveCharacterTextSplitter and CharacterTextSplitter?"
  expected_source_contains: "text_splitters"
- q: "How do I write a Pydantic validator?"
  expected_source_contains: "validators"
```

Metric: % of questions where retrieval returned at least one chunk from the expected source page (call it "retrieval@4").

---

## README template (Day 5 — last 90 min, non-negotiable)

```markdown
# DocsGPT

Chat with FastAPI and LangChain docs. RAG service in Python.

[Live demo](https://docsgpt.onrender.com) · [Screenshots](#screenshots)

## What it does
[2 sentences]

## Stack
[bullet list]

## Architecture
[the ascii diagram from above]

## Trade-offs I made
- **Chunking:** chose recursive char splitter over semantic chunking. Eval gain (<3%) didn't justify ingest latency doubling. Documented in `evals/run_eval.py` output.
- **Vector DB:** Chroma local file vs Pinecone — picked Chroma to keep the project self-contained. Would switch to Pinecone or pgvector for multi-tenant prod.
- **LLM:** `gpt-4.1-mini` over flagship `gpt-5.5` — ~10x cheaper, eval delta within noise for this dataset. Verified with side-by-side run on the eval set.

## Failures I hit and what I changed
- Multi-hop questions missed retrieval → added query rewriting (split into sub-queries before retrieval).
- Long markdown code blocks got split mid-block → tuned `chunk_overlap` and added separator `["\n```", "\n## ", "\n\n", "\n", " "]`.

## Eval
`uv run python evals/run_eval.py` — current retrieval@4 = 0.85 on 10-question set.

## Observability
Langfuse traces every request. Dashboard: [link]

## Run locally
[commands]

## Deploy
[commands]
```

This README — **structured around tradeoffs and failures, not features** — is what makes interviewers actually engage.

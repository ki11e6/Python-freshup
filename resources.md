# Curated Resources

**Rule:** stick to the list per topic. Don't browse beyond. If you finish a section early, do exercises — not more reading.

All links verified May 2026.

---

## Python (Day 1-3)

### Primary — read in order
- **Official tutorial — tutorial.python.org**: https://docs.python.org/3/tutorial/ — sections 3 (Intro), 4 (Control flow), 5 (Data structures), 6 (Modules), 7 (Input/Output), 8 (Errors), 9 (Classes), 10 (Standard library brief tour). Skip 11+ for now.
- **PEP 8** style guide skim (5 min): https://peps.python.org/pep-0008/

### TS → Python bridge
- Search "Python for JavaScript developers" — any reputable cheat-sheet works. Avoid old (pre-3.10) ones; the type-hint syntax has changed.

### `uv` package manager
- https://docs.astral.sh/uv/ — quickstart only. The "Working with projects" section is what you need.

### Pydantic v2
- https://docs.pydantic.dev/latest/concepts/models/ — Models, Fields, Validators only. Skip "Performance" and integration pages.

### Type hints
- https://typing.readthedocs.io/en/latest/spec/ — reference, not a tutorial. Search what you need.
- `pyright` (used by VSCode Pylance) is more permissive than `mypy` and faster. Pick one.

### Async
- The official asyncio docs are dense. Instead: read https://realpython.com/async-io-python/ for intuition.

---

## FastAPI (Day 3-4)

### Primary
- https://fastapi.tiangolo.com/tutorial/ — tutorial in order. **Stop at "Bigger Applications - Multiple Files"** for Day 3.
- On Day 4, also read: "Dependencies", "Background Tasks", "Lifespan Events".

### Reference
- https://fastapi.tiangolo.com/reference/ — for parameter / response model lookups.

### Don't read
- "Advanced User Guide" — interview-irrelevant most of the time. Skip unless you have a specific question.

---

## LangChain (Day 4-5)

### Primary
- **RAG tutorial:** https://docs.langchain.com/oss/python/langchain/rag — the canonical end-to-end example. Read it carefully, then copy the structure.
- **Text splitters:** https://python.langchain.com/docs/concepts/text_splitters/

### Integrations needed
- **Chroma:** https://docs.langchain.com/oss/python/integrations/providers/chroma
- **OpenAI:** https://docs.langchain.com/oss/python/integrations/providers/openai

### Imports to know cold (May 2026)
```python
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_community.document_loaders import RecursiveUrlLoader, SitemapLoader, WebBaseLoader
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.tools import tool
from langchain.chat_models import init_chat_model
```

### YouTube — pick ONE
- Lance Martin's "RAG From Scratch" series on the official LangChain channel — 6 short videos. Watch at 1.5x. Don't watch a second series.

---

## LangGraph (Day 5)

### Primary
- **Quickstart:** https://docs.langchain.com/oss/python/langgraph/quickstart
- **Workflows + Agents concepts:** https://docs.langchain.com/oss/python/langgraph/workflows-agents
- **RAG with LangGraph multi-node** (the pattern you'll match): https://docs.langchain.com/oss/python/langchain/multi-agent/custom-workflow

### Imports to know
```python
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
```

---

## Vector DBs

### Chroma (what you'll use)
- https://docs.trychroma.com/ — "Getting Started" only.

### Optional skim — for interview "what other DBs have you tried?"
- Pinecone — managed, HNSW, namespaces. Strongest for big multi-tenant.
- Weaviate — open source, hybrid search built in, GraphQL API.
- pgvector — PostgreSQL extension. Use when your team already has Postgres.
- Qdrant — Rust-based, open source, increasingly popular.

---

## Observability

### Langfuse (what you'll use)
- https://langfuse.com/docs/get-started — Python SDK quickstart only.
- Free **Hobby** tier: 50k units/month, 30-day retention.

### Alternatives — name-drop only
- LangSmith — LangChain's first-party platform. Same idea, deeper LangChain integration.
- OpenInference + Arize — open standard for LLM telemetry.

---

## OpenAI

### Models (May 2026)
- **Embeddings:** `text-embedding-3-small` — $0.02 / 1M input tokens. 1536 dims. Still the cheap default.
- **LLM (RAG):** `gpt-4.1-mini` — $0.40 in / $1.60 out per 1M. Quality/cost sweet spot.
- **LLM (cheapest):** `gpt-4.1-nano` — $0.10 / $0.40. Use if budget-constrained, slight quality drop.
- **LLM (flagship):** GPT-5.5 — for when quality matters most. Expensive.
- `gpt-4o-mini` still available but no longer promoted as the default — treat as legacy.

### Pricing dashboard
- https://openai.com/api/pricing/ — verify before quoting numbers in interview.

### Set a hard spend cap
- Dashboard → Settings → Limits → set "Hard limit" to $10 before starting. Removes anxiety.

---

## Eval

### RAGAS (the standard library)
- https://docs.ragas.io/ — for context relevance, groundedness, answer relevance metrics.
- Optional for Day 5 — your custom 10-question eval is enough for the interview.

---

## Deploy

### Render (what you'll use)
- https://render.com/docs/free — free web service, Docker runtime supported. 750 free instance hours/month per workspace. Spins down after 15 min idle (~1 min cold start).
- https://render.com/docs/deploy-fastapi — FastAPI-specific guide.

### Alt: Fly.io
- https://fly.io/docs/launch/ — similar profile, slightly more knobs.

---

## Bonus — interview prep

### Python coding (Day 6 warmup)
- LeetCode easy/medium: "Two Sum", "Group Anagrams", "Top K Frequent Elements". 2-3 is enough — you're not interviewing for FAANG algos.

### System design (only if JD hints at it)
- "Designing Data-Intensive Applications" — Ch 1, 2 skim. Not for this interview but career-relevant.

### Salary research (Indian market)
- levels.fyi → Filter by India + your years + role
- Glassdoor company-specific
- AmbitionBox for Indian-specific data

---

## Anti-resources — DO NOT use

- Random YouTube playlists titled "Python in 7 days" — varying quality, will waste time.
- Old (pre-2024) LangChain blog posts — the API has moved. The deprecation rate is high.
- "Top 100 Python interview questions" listicles — most are noise. Use [interview-prep.md](interview-prep.md) instead.
- ChatGPT for primary learning — fine for clarification on a specific concept, but it'll happily hallucinate APIs. Always confirm against official docs.

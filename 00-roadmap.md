# 7-Day Roadmap

## At a glance

| Day | Date | Slot | Focus | Deliverable |
|---|---|---|---|---|
| 1 | Wed 2026-05-27 | 2.5h | Python core foundations | Can read/write Python without lookup |
| 2 | Thu 2026-05-28 | 2.5h | Python intermediate (OOP, generators, decorators) | Built a decorator + a context manager from scratch |
| 3 | Fri 2026-05-29 | 2.5h | Python advanced + tooling + FastAPI intro | "Hello world" FastAPI endpoint with Pydantic validation |
| 4 | Sat 2026-05-30 | 8h | FastAPI deep + RAG ingestion | Doc loaders + chunking + embeddings + vector store working |
| 5 | Sun 2026-05-31 | 8h | RAG retrieval + LangGraph + Deploy | **DocsGPT deployed**, README written |
| 6 | Mon 2026-06-01 | 2.5h | Python interview drilling | Comfortable with 25+ common Python Qs |
| 7 | Tue 2026-06-02 | 2.5h | GenAI interview drilling + project narrative | Can narrate project in 90 sec; ready for screen |
| 🎯 | **Wed 2026-06-03** | — | **Interview day** | — |

## Day-by-day topic outline

### Day 1 — Python core (2.5h)
Setup → data types → mutable vs immutable → control flow → comprehensions → functions (positional/keyword/*args/**kwargs/default-arg trap) → string formatting → slicing → `is` vs `==` → truthiness.

### Day 2 — Python intermediate (2.5h)
Classes & `__init__`/`__repr__`/properties → `@classmethod` vs `@staticmethod` → inheritance & MRO → exceptions (try/except/else/finally) → iterators vs generators → `yield` → decorators (build one) → context managers (`with`, `__enter__`/`__exit__`, `contextlib`).

### Day 3 — Python advanced + FastAPI intro (2.5h)
Type hints + Pydantic v2 → async/await + asyncio basics → dataclasses → shallow vs deep copy → GIL (one paragraph) → venv / `uv` / pip → pytest basics → **FastAPI hello world** with one GET + one POST, Pydantic validation.

### Day 4 — FastAPI + RAG ingestion (8h, Saturday)
- **Block A (3h):** FastAPI tutorial speed-run — routers, dependency injection, async endpoints, error handling, middleware
- **Block B (1h):** Pydantic v2 deep dive — validators, computed fields, model config
- **Block C (1h):** DocsGPT project scaffold — `pyproject.toml` / `uv`, folder layout, env config
- **Block D (3h):** Ingestion pipeline — LangChain document loaders, chunking strategies (recursive, semantic), OpenAI embeddings, Chroma vector store, ingest CLI

### Day 5 — RAG retrieval + agent + deploy (8h, Sunday)
- **Block A (2h):** Retrieval chain — top-k retrieval, prompt template, LLM call, source citations
- **Block B (2h):** `/ask` FastAPI endpoint with streaming response
- **Block C (2h):** LangGraph 1-tool agent (route between docs-retrieval vs Tavily web search)
- **Block D (2h):** Dockerfile, deploy to Render, write README as a postmortem (problem → arch → tradeoffs → failures → metrics)

### Day 6 — Python interview drilling (2.5h)
- **1.5h:** Drill the Q bank in [interview-prep.md](interview-prep.md) — Python section
- **1h:** 2-3 Python LeetCode easy (string/list manipulation)

### Day 7 — GenAI interview drilling + narrative (2.5h)
- **1h:** Drill GenAI/RAG Q bank in [interview-prep.md](interview-prep.md)
- **1h:** Practice the 5-beat project narrative out loud, time yourself (target: 90 sec)
- **30 min:** Cool down — re-read all "Quick Reference" sections, sleep early

## Time math

- Weekdays: 5 × 2.5h = 12.5h
- Weekends: 2 × 8h = 16h
- **Total: 28.5h**

## What you'll have at the end

1. **Working Python knowledge** mapped from TS — answer basic → advanced Qs comfortably
2. **FastAPI fluency** — build endpoints, validation, async, deps
3. **GenAI mental model** — RAG architecture, chunking trade-offs, embeddings, retrieval, agents
4. **Deployed portfolio project (DocsGPT)** — code on GitHub, live URL, strong README
5. **Interview-day reference notes** — every day file has a Quick Reference block

## Risks to manage

- **Python depth vs project time** — if Days 1-3 slip, you'll be cramming Python on the weekend instead of building. Don't let Day 1 spill into Day 2.
- **Tool fatigue** — LangChain has 5 ways to do everything. Stick to the one shown in the day file; don't shop alternatives.
- **README skimped** — interviewers WILL open it. Schedule the last 90 min of Day 5 for the README, not "if there's time."

See [day-01-python-core.md](day-01-python-core.md) to start.

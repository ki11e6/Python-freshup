# Interview Q&A Bank

The master drill list. Use Day 6 for Python, Day 7 for GenAI. On interview day, skim this end-to-end.

> **How to use:** read the question, answer aloud in 30-60 sec, then check the model answer. Don't memorize verbatim — internalize the structure.

---

## Section 1 — Python basics (Day 6 — 30 min)

### 1.1 Mutable vs immutable types — give examples
**Immutable:** `int`, `float`, `str`, `bool`, `tuple`, `frozenset`, `None`, `bytes`.
**Mutable:** `list`, `dict`, `set`, `bytearray`, custom classes.
**Why it matters:** mutable defaults persist across calls; immutable types can be safely shared/hashed/used as dict keys.

### 1.2 `is` vs `==`
`is` checks identity (same object in memory). `==` checks value. Use `is` only for `None`, `True`, `False`. `[] == []` is `True`; `[] is []` is `False`.

### 1.3 The default-argument trap
```python
def f(x, bucket=[]): ...
```
The list is created **once at function definition** and shared across calls. Fix with `bucket=None` and `bucket = bucket or []` inside. **Classic Python gotcha — interviewers love this.**

### 1.4 Shallow vs deep copy
Shallow (`list.copy()`, `copy.copy()`) — new outer container, shared inner objects. Deep (`copy.deepcopy()`) — recursively copies everything. Demo with `a = [[1,2],[3,4]]; b = a.copy(); b[0].append(99)` → `a` is also mutated.

### 1.5 `*args` and `**kwargs`
`*args` collects extra positional args into a tuple. `**kwargs` collects extra keyword args into a dict. Use at function definition to *accept*; use at call site to *unpack* (`f(*xs, **kwargs)`).

### 1.6 Truthiness — what's falsy?
`False`, `0`, `0.0`, `""`, `[]`, `{}`, `()`, `set()`, `None`. Everything else is truthy. `if items:` is idiomatic for "non-empty".

### 1.7 List comprehension vs generator expression
List comp: `[x*2 for x in xs]` — eager, builds full list. Generator: `(x*2 for x in xs)` — lazy, produces one at a time. Use generator when you only need to iterate once or the data is huge.

### 1.8 What does `enumerate` / `zip` / `range` return?
- `range(5)` — a range object, lazy
- `enumerate(xs)` — iterator yielding `(index, value)` pairs
- `zip(xs, ys)` — iterator yielding parallel tuples, stops at shortest input

All three are lazy iterators, not lists. Wrap in `list()` to materialize.

### 1.9 String formatting — what do you prefer?
f-strings (3.6+): `f"hello {name}"`. Faster than `.format()`, more readable than `%`. Use `f"{value:.2f}"` for formatting, `f"{value=}"` for debug.

### 1.10 What does slicing copy?
Slicing a list returns a **new list** (shallow copy). `xs[:]` is a common idiom for a shallow copy. Slicing a string returns a new string (strings are immutable anyway).

---

## Section 2 — Python intermediate (Day 6 — 30 min)

### 2.1 `@classmethod` vs `@staticmethod`
`@classmethod` — first arg is `cls`, used for alternate constructors (`User.from_dict(d)`). `@staticmethod` — no implicit first arg, just a function namespaced under the class. If you need access to the class or its subclasses, use `@classmethod`.

### 2.2 What is MRO?
Method Resolution Order — the order Python searches for a method in inheritance hierarchies. Python 3 uses **C3 linearization** — deterministic, prevents diamond ambiguity. Inspect with `MyClass.__mro__`. `super()` walks the MRO.

### 2.3 What does `super()` do without arguments?
Python 3 magic — it inspects the calling frame to find the class and instance. So `super().method()` in a method body just works without specifying `super(Parent, self)`.

### 2.4 Iterator vs generator
**Iterator** — any object with `__iter__` (returns self) and `__next__` (returns next value, raises `StopIteration` when done). **Generator** — a function with `yield` that returns a generator object (which IS an iterator). Generators are just an easier way to write iterators.

### 2.5 How does `yield` work?
A function with `yield` returns a generator object. Each call to `next()` runs the function until the next `yield`, returns that value, and pauses. State is preserved between calls. `for x in gen:` calls `next()` until `StopIteration`.

### 2.6 What is a decorator? How do you write one?
A callable that takes a function and returns a (usually wrapped) function. `@decorator` is sugar for `f = decorator(f)`. Skeleton:
```python
from functools import wraps
def my_decorator(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # before
        result = fn(*args, **kwargs)
        # after
        return result
    return wrapper
```
`@wraps` preserves `__name__`/`__doc__`.

### 2.7 What is a context manager?
An object with `__enter__` and `__exit__` methods used with `with`. Guarantees cleanup even on exception. Easier form: `@contextmanager` decorator on a generator with `try/finally` around `yield`. Examples: file handles, locks, DB sessions.

### 2.8 `try / except / else / finally` — what's `else`?
`else` runs **only if no exception was raised** in `try`. Useful when you want code that runs after success but shouldn't be caught by the same `except`. `finally` always runs.

### 2.9 `raise` vs `raise e`
Inside an `except` block, `raise` re-raises the **current** exception preserving traceback. `raise e` raises that exception object but **adds a new traceback frame**. Use bare `raise`.

### 2.10 What's `__slots__`?
A class-level declaration that restricts instances to a fixed set of attributes and removes per-instance `__dict__`. Saves memory significantly for many small objects. Trade-off: can't add attributes at runtime. Used by `@dataclass(slots=True)`.

---

## Section 3 — Python advanced (Day 6 — 20 min)

### 3.1 What's the GIL? Why does it exist?
**Global Interpreter Lock** — in CPython, only one thread can execute Python bytecode at a time. It exists because CPython's memory management (reference counting) is not thread-safe; the GIL is the simplest way to guarantee correctness.

**Implications:**
- Threading helps I/O-bound code (GIL released during I/O syscalls)
- Threading does NOT speed up CPU-bound Python — use `multiprocessing`
- Asyncio is single-threaded cooperative concurrency — sidesteps the issue

Python 3.13 added an **experimental no-GIL build** (PEP 703), still optional in 3.14.

### 3.2 `async def` and `await` — explain
`async def` defines a coroutine function. Calling it returns a coroutine object (does nothing yet). `await` suspends the coroutine and yields control to the event loop until the awaitable completes. Runs in a single thread — concurrent, not parallel.

### 3.3 `asyncio.gather` vs sequential awaits
```python
a = await f1(); b = await f2()    # sequential — sum of latencies
a, b = await asyncio.gather(f1(), f2())   # concurrent — max of latencies
```

### 3.4 When should you NOT use async?
- CPU-bound work (use multiprocessing)
- Using a library with only sync APIs (it'll block the loop)
- Simple scripts where the concurrency win doesn't justify the complexity

### 3.5 What are type hints checked at?
By default, **not** at runtime — only by static checkers like `mypy`/`pyright`. Runtime tools that DO check: Pydantic (validates), FastAPI (uses Pydantic to validate inputs), `typeguard` (decorator).

### 3.6 What does `@dataclass` give you?
Auto-generates `__init__`, `__repr__`, `__eq__` from annotations. With `frozen=True` it adds `__hash__`. With `slots=True` it uses `__slots__`. No validation — use Pydantic for that.

### 3.7 Pydantic v2 vs `@dataclass`
Pydantic validates and serializes; `@dataclass` does neither. Pydantic generates JSON Schema; `@dataclass` doesn't. Pydantic is for boundary data (HTTP bodies, config files, LLM outputs); dataclass is for internal structs. Pydantic v2 is written in Rust — fast.

### 3.8 What does `if __name__ == "__main__":` do?
Code under this block runs only when the file is executed directly, not when imported. Lets a module be both a library and a script.

---

## Section 4 — FastAPI (Day 7 — 20 min)

### 4.1 What makes FastAPI fast?
ASGI (Starlette) + Pydantic v2 (Rust-validated). Async-native. Comparable to Node.js/Go in synthetic benchmarks. Real-world performance depends on what you do (DB calls, LLM calls dominate).

### 4.2 Sync vs async endpoints
`def` endpoints run in a threadpool (FastAPI offloads). `async def` runs on the event loop. **Rule:** if you call sync blocking I/O (`requests.get`, blocking DB driver), use `def`. If you use async clients (`httpx.AsyncClient`, asyncpg), use `async def`. Never call sync blocking I/O inside `async def`.

### 4.3 Where do path/query/body params come from?
FastAPI infers from the **type** and **default**:
- Names matching `{param}` in the route → path
- Pydantic `BaseModel` → body
- Anything else → query

You can be explicit with `Path()`, `Query()`, `Body()`.

### 4.4 How does Pydantic validation produce a 422?
FastAPI catches `ValidationError`, returns 422 Unprocessable Entity with a structured error body. You can customize with `@app.exception_handler(ValidationError)`.

### 4.5 What is `Depends()`?
FastAPI's dependency injection. The function passed to `Depends()` is called per-request (unless cached). Dependencies can themselves have dependencies — FastAPI resolves the DAG. Common uses: auth, DB session, current-user, settings.

### 4.6 How do you handle startup/shutdown?
The **`lifespan`** context manager:
```python
@asynccontextmanager
async def lifespan(app):
    # startup
    yield
    # shutdown
app = FastAPI(lifespan=lifespan)
```
Older `@app.on_event("startup")` is deprecated.

### 4.7 How does FastAPI generate OpenAPI?
Automatic from type hints + Pydantic models. Swagger UI at `/docs`, ReDoc at `/redoc`. Includes path/query/body schemas, response models, examples, status codes.

### 4.8 Background tasks vs Celery vs ARQ
- `BackgroundTasks` — runs after response, same process. For light work (send email, log). No retry, no persistence.
- Celery / ARQ — proper task queues with Redis/RabbitMQ. For heavy, retryable, scheduled work.

---

## Section 5 — RAG concepts (Day 7 — 30 min)

### 5.1 What is RAG and why use it?
**Retrieval-Augmented Generation** — retrieve relevant context from a knowledge base, inject into the prompt, then generate. **Why:** reduces hallucination by grounding answers in real data; lets LLMs use private/recent data they weren't trained on; cheaper than fine-tuning; easy to update (just re-ingest).

### 5.2 What's the full RAG pipeline?
1. **Ingest:** load docs → split into chunks → embed → store in vector DB.
2. **Query:** embed the question → similarity-search the vector DB for top-k chunks → build prompt with retrieved context → call LLM → return answer with citations.

### 5.3 Why chunk?
LLMs have context limits; chunks are the unit of retrieval ranking (you want similar passages, not similar whole-documents); smaller passages → more precise retrieval. Trade-off: too small loses context, too large dilutes relevance.

### 5.4 Recursive vs fixed-size vs semantic chunking
- **Fixed-size (`CharacterTextSplitter`)** — split every N chars. Ignores structure, easy.
- **Recursive (`RecursiveCharacterTextSplitter`)** — try separators in order (paragraph → sentence → word). **Default for prose.**
- **Markdown-aware** — split on headers, preserves doc hierarchy.
- **Semantic** — split where embeddings differ between adjacent sentences. Most expensive, sometimes best quality.

### 5.5 What is overlap and why?
Each chunk shares some chars with neighbors (e.g. 200 of 1000). Prevents losing information at boundaries — if the answer spans a chunk break, overlap means it's whole in at least one chunk.

### 5.6 How do embeddings work?
A model maps text → fixed-length vector. `text-embedding-3-small` produces 1536-dim vectors. Similar text → nearby vectors. The model is trained so that semantically related text ends up close in vector space (cosine similarity).

### 5.7 Embedding similarity metrics
- **Cosine similarity** — angle between vectors. Most common. Range -1 to 1.
- **Dot product** — works when vectors are normalized.
- **L2 distance** — Euclidean. Smaller = more similar.

OpenAI embeddings are normalized, so cosine and dot product are equivalent.

### 5.8 What does the vector DB store?
The embedding vector + the original text + metadata (source URL, doc title, etc). On query, embed the question with the same model, ANN-search for nearest neighbors, return the original texts.

### 5.9 What's ANN? Why not exact search?
**Approximate Nearest Neighbor** — exact KNN is O(N×d) per query; ANN data structures (HNSW, IVF) give sub-linear search with small recall loss. Necessary at scale.

### 5.10 Hybrid retrieval — what and why?
Combine **dense** (embedding similarity) with **sparse** (keyword/BM25). Dense is great for semantic queries; sparse is great for exact terms (proper nouns, rare jargon, code symbols). Reciprocal Rank Fusion (RRF) combines them. Big quality gains, especially for technical docs with specific API names.

### 5.11 What is reranking?
After top-k retrieval, re-score the candidates with a more expensive **cross-encoder** model (e.g. Cohere Rerank, BGE-reranker). The cross-encoder sees query+doc together, gives better relevance scores than embedding cosine. Trade-off: latency + cost.

### 5.12 Query rewriting / HyDE
Pre-retrieval transforms:
- **Rewriting** — ask the LLM to rephrase the user's question for better recall.
- **HyDE (Hypothetical Doc Embeddings)** — generate a fake "ideal answer," embed THAT, use it as the query vector. Often boosts retrieval.
- **Multi-query** — generate N rewrites, retrieve for each, deduplicate.

### 5.13 How do you reduce hallucination in RAG?
1. Better retrieval (more relevant context = less making it up)
2. Prompt instructions: "answer using ONLY the context; say 'I don't know' otherwise"
3. Structured outputs / function calling
4. Citations / quote requirements
5. Eval + guardrails (block low-confidence answers)

### 5.14 How do you evaluate a RAG system?
**Retrieval metrics:**
- recall@k — was the relevant doc in top k?
- MRR (Mean Reciprocal Rank) — average of 1/rank of the relevant doc
- nDCG — accounts for graded relevance

**Generation metrics (RAG triad):**
- Context relevance — were retrieved chunks relevant to the question?
- Groundedness / faithfulness — is the answer supported by the chunks?
- Answer relevance — does the answer address the question?

Tools: RAGAS, TruLens, LangSmith / Langfuse evals.

### 5.15 What's the tradeoff: bigger LLM vs better retrieval?
**Better retrieval almost always wins** for cost+quality. A small LLM with great context outperforms a flagship LLM with bad context. Spend complexity on retrieval first, then LLM.

---

## Section 6 — LangChain / LangGraph specifics (Day 7 — 20 min)

### 6.1 What is LCEL?
LangChain Expression Language. Compose **runnables** with `|`:
```python
chain = prompt | llm | parser
chain.invoke(input)
```
Built-in support for `.stream()`, `.batch()`, `.ainvoke()`, callbacks, retries. Use for linear chains.

### 6.2 What's a Runnable?
Any LangChain object implementing `invoke` / `ainvoke` / `stream` / `batch`. Prompts, LLMs, retrievers, output parsers — all runnables, all composable with `|`.

### 6.3 Parallel runnables
Pass a dict — each value runs in parallel:
```python
chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm
```

### 6.4 When to use LangGraph instead of LCEL?
- Cycles (agent loops)
- Branching / conditional routing
- Multi-step state passing
- Human-in-the-loop / interrupts
- Persistent execution / checkpointing

LCEL is great for linear chains. LangGraph for stateful, agentic, multi-step.

### 6.5 What's `MessagesState`?
Built-in LangGraph state with `messages: list[AnyMessage]` and an **append reducer** — new messages are appended, not replaced. Most chat agents use this.

### 6.6 Conditional edges
An edge whose destination is determined by a function inspecting state. Returns a node name (or `END`):
```python
graph.add_conditional_edges("llm", router_fn, ["tool_node", END])
```

### 6.7 `bind_tools`
Attaches tool schemas to an LLM so the model can emit tool calls. The LLM doesn't run the tools — your code does, reading `last_message.tool_calls` and dispatching.

### 6.8 What's the difference between `create_agent` and a custom LangGraph?
`create_agent` is a prebuilt: LLM-with-tools loop, structured outputs, system prompts. Quick start. A custom `StateGraph` is for when you need bespoke nodes, branching, or state beyond messages.

---

## Section 7 — Behavioral / project narrative (Day 7 — 30 min)

### 7.1 "Tell me about your RAG project" — 90-second narrative

**The 5 beats:**

1. **Problem framing (10 sec)**
> "I wanted to answer questions about FastAPI and LangChain docs without keyword-search frustration or LLM hallucination, so I built a RAG service end-to-end in Python."

2. **Architecture in one breath (20 sec)**
> "Stack is FastAPI plus LangChain plus Chroma plus LangGraph, with Langfuse for observability. Pipeline: crawl the docs, split with recursive char splitter at 1000 chars with 200 overlap, embed with text-embedding-3-small, store in Chroma. At query time, embed the question, top-4 retrieve, optionally an agent routes between docs search and Tavily web search, then GPT-4.1-mini streams an answer with cited sources."

3. **One real trade-off (20 sec)**
> "I tested semantic chunking against recursive char chunking on my eval set — semantic gave less than 3% improvement on retrieval@4 but doubled ingest latency, so I stayed with recursive."

4. **One real failure I fixed (20 sec)**
> "Multi-hop questions like 'how do Pydantic validators work with FastAPI dependencies' were initially missed because retrieval treated them as one query. I added a query-rewriting step that splits these into sub-queries before retrieval — bumped retrieval@4 from 60% to 85%."

5. **Observability + numbers (20 sec)**
> "Every request is traced in Langfuse — model, tokens, latency, cost. I have a 10-question eval set with retrieval@4 at 85%, answer-substring match at 70%. Currently runs at about $0.004 per query on gpt-4.1-mini."

**Practice this out loud. Time yourself. Target 90 seconds.**

### 7.2 Possible follow-ups and short answers

**"Why Chroma and not Pinecone?"**
> "Wanted the project self-contained — Chroma is a file-backed local store, no signup. For multi-tenant prod I'd switch to Pinecone or pgvector."

**"Why didn't you fine-tune?"**
> "RAG is cheaper to iterate (just re-ingest), keeps data out of model weights, and matches the task — Q&A over a fixed corpus."

**"How would you scale this to 10M docs?"**
> "Switch Chroma → managed vector DB with HNSW (Pinecone/Weaviate). Add hybrid retrieval for keyword recall. Pre-compute embeddings in parallel batches. Add a reranker before the LLM. Cache common queries."

**"How would you handle PII or sensitive docs?"**
> "Encrypt at rest, filter PII at ingest, add access control at retrieval (metadata filters per user), log access — and avoid sending sensitive context to third-party LLMs (use a hosted open model or Azure OpenAI with a BAA)."

**"What's the worst-case latency?"**
> "Cold start on Render ~60s. Warm path: ~300ms retrieval + ~1-2s LLM streaming. Web-search fallback adds ~1-2s for Tavily. P99 around 4s end-to-end."

**"How do you stop prompt injection?"**
> "System prompt instructs the model to treat retrieved context as data, not instructions. For higher stakes, I'd add input/output guardrails (e.g. NeMo Guardrails, Llama Guard)."

### 7.3 Behavioral

**"Why are you switching from TS to Python?"**
> "Backend skills transfer — FastAPI is structurally similar to NestJS. Adding Python broadens what I can build, especially the GenAI ecosystem, which is Python-first. Also already use Python in scripts and tooling daily."

**"Why this role?"**
> Honest version: "Friend referred me, I respect his engineering judgment. The work — Python backend + GenAI — is where I want to grow. I've been building in this space; this would be doing it full-time."

**"Weakness?"**
> "Most of my AI work has been integrating LLMs as a feature, not training models. I'm intentionally focusing on the application-engineering side, but if the role expects ML fundamentals, that's a gap I'd close by [taking specific course / shadowing].\""

**"Salary expectations?"**
> Have a number ready. Anchor with research from levels.fyi / Glassdoor for the region/level. Don't go first if you can avoid it.

### 7.4 Things to ASK them

These show seriousness:
- "What does the current Python + GenAI stack look like — LangChain? Custom? Multi-model?"
- "How are you handling eval and regression — manual reviews, an eval harness?"
- "What's the team's split between feature work and platform/infra?"
- "What does a typical week look like for someone in this role 3 months in?"
- "Why did the previous person leave / why is this role open?" (only if you can ask gracefully)

---

## Interview-day cool-down (30 min before the call)

1. **Skim the Quick Reference at the top of each day file** — that's all the recall you need.
2. **Re-read your README** — your project is your strongest credibility.
3. **Test the live URL once** — make sure Render hasn't spun down with a stale state.
4. **Open `/docs` (Swagger)** in a tab — to show during demo if asked.
5. **Have your GitHub repo open** with the code structure visible.
6. **Water, deep breath, smile.** You've earned this.

Good luck.

# Day 3 — Python Advanced + FastAPI Intro

**Time:** 2.5 hours · **Goal:** Type hints, async, Pydantic, tooling, and **a running FastAPI app**.

---

## Quick reference (interview-day skim)

| Concept | One-line answer |
|---|---|
| Type hints | Optional, not enforced at runtime. Checked by `mypy`/`pyright`. FastAPI + Pydantic use them at runtime. |
| `Optional[X]` | Equivalent to `X \| None` (3.10+ prefers the pipe syntax) |
| `Union[X, Y]` | Equivalent to `X \| Y` (3.10+) |
| `list[int]` vs `List[int]` | 3.9+ — use lowercase built-ins. `from typing import List` is legacy. |
| `async def` | Function returns a coroutine. Must be `await`ed or run on event loop. |
| `await` | Yields control to event loop while awaiting an awaitable. |
| `asyncio.gather` | Run multiple coroutines concurrently and wait for all. |
| `asyncio.run(main())` | Entry point — runs the event loop. |
| GIL | One Python bytecode runs at a time in CPython. Threading good for I/O, multiprocessing for CPU. |
| `dataclass` | `@dataclass` auto-generates `__init__`, `__repr__`, `__eq__`. No validation. |
| Pydantic `BaseModel` | Like `dataclass` + runtime validation + JSON serialization. |
| `uv` | Modern Python package manager — fast, replaces pip+venv+pip-tools. |
| `pytest` | De-facto test runner. `pytest test_x.py::test_func -v` |
| FastAPI `@app.get` | Decorator that registers a route. Path params, query params, body all type-driven. |
| FastAPI `Depends` | Dependency injection. The DI you know from NestJS — but per-request, not per-app. |

---

## 1. Type hints (20 min)

Python is dynamically typed but you can (and should) annotate.

```python
def greet(name: str, age: int = 18) -> str:
    return f"hi {name}, {age}"

# 3.10+ syntax
def find(uid: int) -> User | None:
    ...

def parse(items: list[dict[str, int]]) -> set[str]:
    ...
```

### Common types
```python
from typing import Any, Callable, Literal, TypedDict, Protocol

handler: Callable[[int, str], bool]            # fn(int, str) -> bool
mode: Literal["read", "write", "append"]       # finite set of strs
data: dict[str, Any]                           # anything

class Config(TypedDict):
    host: str
    port: int

class Loggable(Protocol):
    def log(self, msg: str) -> None: ...
```

> **TS analogy:** `Callable[[int], bool]` ≈ `(arg: number) => boolean`. `Literal["a", "b"]` ≈ `"a" | "b"`. `TypedDict` ≈ TS `interface` for plain objects. `Protocol` ≈ TS structural typing (duck typing made explicit).

### Type hints are NOT runtime checked

```python
def add(a: int, b: int) -> int:
    return a + b

add("x", "y")   # returns "xy" — no error
```

Validators that *do* check at runtime: **Pydantic** (covered next).

Tooling: `mypy` or `pyright` for static checking. Pyright is faster, used by VSCode's Pylance.

---

## 2. Dataclasses + Pydantic v2 (30 min)

### `@dataclass` — built-in, no validation
```python
from dataclasses import dataclass, field

@dataclass
class Point:
    x: int
    y: int
    label: str = "origin"
    tags: list[str] = field(default_factory=list)  # mutable default!

p = Point(1, 2)
# Point(x=1, y=2, label='origin', tags=[])
```

`field(default_factory=list)` is how you set a mutable default (same trap as default-arg lists from Day 1).

### Pydantic v2 — validation + serialization

```python
from pydantic import BaseModel, Field, field_validator, EmailStr

class User(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    age: int = Field(ge=0, le=150)
    tags: list[str] = []

    @field_validator("name")
    @classmethod
    def name_no_digits(cls, v: str) -> str:
        if any(c.isdigit() for c in v):
            raise ValueError("name cannot contain digits")
        return v

# Instantiate — validates
u = User(id=1, name="sharath", email="s@example.com", age=25)
u.model_dump()       # → dict
u.model_dump_json()  # → JSON str
User.model_json_schema()  # → JSON Schema (used by FastAPI for OpenAPI docs)

# Invalid → raises ValidationError
User(id="not an int", name="", email="bad", age=-1)
```

**Pydantic v2 is the foundation of FastAPI** — every request body, response, query param schema goes through it.

> **TS analogy:** `BaseModel` ≈ Zod schema. Both runtime-validate and infer types.

### Pydantic vs `@dataclass` — when to use which
- **Pydantic** — anything from a network/file (FastAPI bodies, config files, LLM tool args)
- **`@dataclass`** — pure in-process structs where you control the inputs

---

## 3. `async` / `await` (25 min)

```python
import asyncio
import httpx

async def fetch(url: str) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return r.text

async def main():
    # sequential
    a = await fetch("https://example.com")
    b = await fetch("https://example.com")

    # concurrent — both fetches in flight at once
    a, b = await asyncio.gather(
        fetch("https://example.com"),
        fetch("https://example.com"),
    )

asyncio.run(main())
```

### Mental model
- `async def` makes a **coroutine function**. Calling it returns a coroutine object (does nothing yet).
- `await` yields control to the **event loop** until the awaitable completes.
- The event loop runs in a single OS thread — so async is **concurrent, not parallel**.

> **TS analogy:** Python's `async def` ≈ TS `async function`. Python's coroutine = JS Promise (kind of). `asyncio.gather` ≈ `Promise.all`. The event loop is the same idea.

### Async pitfalls
- **Don't mix sync I/O into async code** — `time.sleep(5)` in an async fn blocks the whole loop. Use `await asyncio.sleep(5)`.
- **Don't `await` a list** — `await [coro1, coro2]` is wrong. Use `asyncio.gather`.
- **Don't forget `await`** — calling `fetch(url)` without `await` returns the coroutine but doesn't run it.

### When NOT to use async
- CPU-bound work — use threads (I/O-bound) or processes (CPU-bound). Async helps with I/O wait, not compute.

---

## 4. GIL — the famous one (10 min)

**One sentence:** CPython has a Global Interpreter Lock — only one thread can execute Python bytecode at a time, even on multi-core machines.

**Implications:**
- Threading is great for **I/O-bound** workloads (network, disk) — the GIL is released during I/O syscalls.
- Threading does NOT speed up **CPU-bound** Python code — use `multiprocessing` or `concurrent.futures.ProcessPoolExecutor`.
- `async`/`await` is a third option — single-threaded cooperative concurrency. Good for I/O. No GIL issue because no threading.

**Trivia for interviewers:** Python 3.13 added an experimental no-GIL build (PEP 703). Still experimental in 3.14. Not yet the default.

---

## 5. Tooling (15 min)

### `uv` — package manager (installed Day 1)

```bash
uv init my-project           # scaffold pyproject.toml
uv add fastapi               # add a dependency
uv add --dev pytest mypy     # dev dependency
uv sync                      # install everything from pyproject.toml
uv run python main.py        # run inside venv
uv run pytest                # run any command
```

> **TS analogy:** `uv add` ≈ `pnpm add`. `uv sync` ≈ `pnpm install`. `uv run` ≈ `pnpm exec`.

### `pytest` basics

```python
# tests/test_math.py
import pytest

def test_basic():
    assert 1 + 1 == 2

def test_raises():
    with pytest.raises(ZeroDivisionError):
        1 / 0

@pytest.mark.parametrize("a,b,expected", [(1, 2, 3), (5, 5, 10)])
def test_add(a, b, expected):
    assert a + b == expected
```

Run: `uv run pytest -v`. Filter: `uv run pytest tests/test_math.py::test_basic`.

### `.env` and config

```bash
# .env
OPENAI_API_KEY=sk-...
APP_ENV=dev
```

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    app_env: str = "dev"

    model_config = {"env_file": ".env"}

settings = Settings()  # reads from env + .env file
```

`pydantic-settings` is the way — typed config with .env loading built in.

---

## 6. FastAPI hello world (40 min) — start the project

### Install + scaffold
```bash
mkdir docsgpt && cd docsgpt
uv init
uv add fastapi uvicorn pydantic-settings
uv add --dev pytest httpx
```

### Minimum app
```python
# main.py
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field

app = FastAPI(title="DocsGPT", version="0.0.1")


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    k: int = Field(default=4, ge=1, le=20)


class AskResponse(BaseModel):
    answer: str
    sources: list[str]


# fake "service" — Day 4 will swap for real retrieval
def get_retriever():
    """A FastAPI dependency. Resolved per-request."""
    return object()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest, retriever=Depends(get_retriever)):
    if "secret" in req.question:
        raise HTTPException(status_code=400, detail="filtered")
    return AskResponse(
        answer=f"stub answer to: {req.question}",
        sources=["https://example.com"],
    )
```

Run it:
```bash
uv run uvicorn main:app --reload
# → open http://localhost:8000/docs   for interactive Swagger UI
```

### Map to NestJS

| NestJS | FastAPI |
|---|---|
| `@Controller('users')` | (no class needed) `app = FastAPI(); @app.get("/users")` |
| `@Get('/:id')` | `@app.get("/{id}")` with `id: int` param |
| `@Body() dto: CreateUserDto` (class-validator) | `req: CreateUser` where `CreateUser(BaseModel)` |
| `@Query() pagination: PaginationDto` | `page: int = Query(default=1, ge=1)` |
| Provider + `@Inject` | `Depends(get_thing)` |
| `Module` | (No equivalent — group via `APIRouter`) |
| Pipe validation | Automatic via Pydantic |
| Interceptors / Filters | `Middleware` + `exception_handler` |
| `ConfigService` | `pydantic-settings` Settings class |
| Swagger module | **Built-in** — `/docs` and `/redoc` auto-generated |

### Path params, query params, body — all from annotations

```python
@app.get("/items/{item_id}")
async def read(
    item_id: int,                              # path param (in URL)
    q: str | None = None,                      # query param (?q=...)
    limit: int = Query(default=10, ge=1, le=100),  # query with constraints
):
    return {"item_id": item_id, "q": q, "limit": limit}
```

FastAPI infers from the **type** and **default** where each parameter comes from. Path-segment names → path params. Pydantic models → request body. Everything else → query.

### Async vs sync endpoints

```python
@app.get("/sync")
def sync_route():            # runs in threadpool
    blocking_io()
    return {}

@app.get("/async")
async def async_route():     # runs on event loop
    await non_blocking_io()
    return {}
```

**Rule:** if you call sync blocking I/O, use `def` (FastAPI offloads to a threadpool). If you use async libraries, use `async def`. **Never** call sync blocking I/O from `async def` — you block the whole event loop.

---

## 7. End-of-Day-3 self-check

- [ ] When are type hints checked? (answer: not at runtime by default; Pydantic checks them at runtime)
- [ ] What's the difference between `async def` and `def` in FastAPI?
- [ ] What's the GIL, and which workloads care?
- [ ] How does `Depends()` resolve a dependency?
- [ ] What does Pydantic give you that `@dataclass` doesn't?
- [ ] Where does FastAPI's automatic OpenAPI come from?

You should now have a `main.py` returning a stub response on `POST /ask`. **Tomorrow we replace the stub with real RAG.**

---

## Pre-Saturday checklist

Before Day 4 starts, you should have:
- [ ] `uv` installed and a `docsgpt/` project with `pyproject.toml`
- [ ] `OPENAI_API_KEY` in `.env`, hard spend cap set in OpenAI dashboard
- [ ] `Tavily` API key (free signup, save for Day 5)
- [ ] `Langfuse` account on cloud (free Hobby tier, save for Day 5)
- [ ] GitHub repo created (private to start, flip to public on Day 5)
- [ ] Render account (free tier, deploy on Day 5)

If any of these are missing, do them tonight — Saturday's 8 hours need to be all coding.

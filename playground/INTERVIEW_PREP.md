# Python + Gen AI Interview Prep — Master Index

Target roles: **Senior Python Engineer** & **Gen AI Engineer**.

Each folder now has a `NOTES.md` (deep-dive notes) and `QUESTIONS.md` (interview Q&A,
from warm-up to senior/staff level). Notes go well beyond the example scripts — they cover
the CPython internals, gotchas, and the Gen-AI-specific angles interviewers probe.

## How to use this

1. Read the folder `NOTES.md` until you can explain each concept *out loud* without notes.
2. Cover the answer in `QUESTIONS.md`, attempt it, then check. Anything you miss → re-read notes.
3. For Gen AI roles, pay special attention to the **🤖 Gen AI angle** callouts — these are
   where fundamentals show up in real LLM/RAG/agent codebases.

## Topic map

| Folder | Topic | Why it matters in interviews |
|--------|-------|------------------------------|
| `01_virtual` | Virtual environments & packaging | Reproducible envs, dependency hell, CUDA/torch pinning |
| `02_dataypes` | Data types, mutability, memory model | The single most-tested area; hashing, interning, `is` vs `==` |
| `03_conditionals` | Control flow, `match`, truthiness | Clean branching, structural pattern matching (3.10+) |
| `04_loops` | Iteration, `zip`/`enumerate`, walrus | Idiomatic loops, lazy iteration, streaming |
| `05_functions` | Scope (LEGB), args/kwargs, closures, recursion | Closures, decorators, mutable-default trap |
| `06_chai_business` | Modules, packages, imports | Project structure, import system, circular imports |
| `07_comprehensions` | Comprehensions & generators | Memory-efficient transforms, lazy pipelines for token streams |

## The 10 questions you must be able to answer cold

1. Mutable vs immutable — give 3 of each and explain what `id()` reveals.
2. `is` vs `==`, and why `a = 256; b = 256; a is b` is `True` but `257` may not be.
3. Why is the mutable-default-argument `def f(x=[])` a bug? How do you fix it?
4. Explain LEGB scope. When do you need `global` vs `nonlocal`?
5. List vs tuple vs set vs dict — when do you reach for each, and what are the Big-O costs?
6. What does the GIL actually protect, and when does it hurt you? (threads vs processes vs async)
7. Generator vs list comprehension — memory and laziness tradeoffs.
8. Shallow vs deep copy — show a bug caused by getting this wrong.
9. `*args`/`**kwargs` and the full argument-passing model (positional-only `/`, keyword-only `*`).
10. How do you make a reproducible Python environment for an ML project?

## Suggested study order

`02 → 03 → 04 → 07 → 05 → 06 → 01` (data model first, then control flow, then the
abstractions; packaging last since it's mostly tooling).

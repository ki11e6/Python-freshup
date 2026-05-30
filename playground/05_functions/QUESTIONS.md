# Functions, Scope & Closures — Interview Questions

### 🔴 Q1. Why is `def f(x=[]):` dangerous? Fix it.
**A.** Default arguments are evaluated **once at definition time** and the same object is
reused across calls, so a mutable default accumulates state between calls. Fix: use a
sentinel — `def f(x=None): x = [] if x is None else x`. This is the most-asked function gotcha.

### 🟢 Q2. Positional vs keyword arguments?
**A.** Positional bind by order; keyword bind by name (any order). You can mix:
positionals first, then keywords. Keyword args improve call-site readability for flags.

### 🟡 Q3. What do `*args` and `**kwargs` collect?
**A.** `*args` gathers extra positional arguments into a **tuple**; `**kwargs` gathers extra
keyword arguments into a **dict**. Used for variadic functions and forwarding args to wrapped
calls (common in decorators and SDK wrappers).

### 🔴 Q4. What do `/` and `*` mean in a function signature?
**A.** In `def f(a, /, b, *, c)`: `a` is **positional-only** (can't be passed by name), `b`
can be either, `c` is **keyword-only** (must be passed by name). `/` marks the end of
positional-only params; `*` (or `*args`) marks the start of keyword-only params.

### 🟢 Q5. Explain the LEGB rule.
**A.** Name resolution order: **Local** (current function), **Enclosing** (outer functions),
**Global** (module), **Built-in** (`len`, `print`, ...). Python searches in that order and
uses the first match.

### 🔴 Q6. `global` vs `nonlocal`?
**A.** `global x` makes assignments inside a function rebind the **module-level** `x`.
`nonlocal x` makes them rebind the **nearest enclosing function's** `x` (used in nested
functions/closures). Without either, assigning to a name makes it local.

### 🟡 Q7. Is Python pass-by-value or pass-by-reference?
**A.** Neither exactly — **pass-by-object-reference** (call-by-sharing). The parameter is
bound to the same object as the argument. Mutating a mutable arg in place is visible to the
caller; rebinding the parameter is not. `edit_chai(cup): cup[1]=42` mutates the caller's list.

### 🔴 Q8. What is a closure? Give a use case.
**A.** A nested function that captures and remembers variables from its enclosing scope even
after that scope returns. Used for factories (`make_multiplier(n)`), stateful callbacks, and
decorators. The captured vars live in `__closure__` cells.

### 🔴 Q9. What's the late-binding closure bug?
**A.**
```python
fns = [lambda: i for i in range(3)]
[f() for f in fns]   # [2, 2, 2], not [0, 1, 2]
```
Closures capture the **variable** `i`, not its value at creation; all see the final `i=2`.
Fix by binding per-iteration: `lambda i=i: i` (default arg captures the current value).

### 🟢 Q10. What does a function return if there's no `return`?
**A.** `None`. A bare `return` and falling off the end both yield `None` (e.g. the `pass`
function in `10_return.py`).

### 🟡 Q11. How does Python return multiple values?
**A.** It returns a **tuple**; the caller unpacks it: `return sold, remaining` →
`s, r = chai_report()`. It's just tuple packing/unpacking, not a special multi-return.

### 🟡 Q12. Pure vs impure function — why prefer pure?
**A.** A pure function's output depends only on its inputs with no side effects. Pure
functions are easy to test, safe to cache (`lru_cache`), and parallel-safe. Impure ones
(mutate globals, do I/O) are harder to reason about. Isolate side effects (LLM calls,
DB writes) at the boundaries.

### 🔴 Q13. What are the limits of recursion in Python?
**A.** Default recursion limit ≈ 1000 frames (`sys.getrecursionlimit`); exceeding it raises
`RecursionError`. Python has **no tail-call optimization**, so deep recursion isn't converted
to iteration. For large depths, rewrite iteratively or use an explicit stack.

### 🟡 Q14. When is a `lambda` appropriate vs a `def`?
**A.** `lambda` for tiny, single-expression, throwaway functions passed inline (e.g.
`sorted(key=lambda x: x.score)`, `filter(...)`). Use `def` for anything with statements,
multiple lines, a docstring, or that's reused/named — easier to debug (lambdas show as
`<lambda>` in tracebacks).

### 🔴 Q15. What's a decorator and how does it relate to closures? (likely follow-up)
**A.** A decorator is a callable that takes a function and returns a replacement, usually via
a closure wrapper: `@timer` ⇒ `func = timer(func)`. Use `functools.wraps` to preserve the
wrapped function's `__name__`/`__doc__`. Examples: `@lru_cache`, `@property`, auth/logging.

### 🟡 Q16. How do you introspect a function?
**A.** `f.__name__`, `f.__doc__` (docstring), `f.__defaults__`, `f.__annotations__` (type
hints), `inspect.signature(f)`, and `help(f)`. Useful for building generic tool wrappers and
auto-generating LLM tool schemas from function signatures.

### 🔴 Q17. (Gen AI) How would you auto-generate a tool-call JSON schema from a Python function?
**A.** Introspect with `inspect.signature` to get parameter names/defaults and
`f.__annotations__` / type hints for types, pull the description from `f.__doc__`, and map
Python types → JSON-schema types. This is exactly what frameworks like LangChain / the
function-calling decorators do under the hood. Pydantic models make the type→schema mapping
robust.

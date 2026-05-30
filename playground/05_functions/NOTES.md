# Functions, Scope & Closures — Notes

> Functions are where most senior questions live: scope, closures, argument model, the
> mutable-default trap, pure vs impure, recursion, and first-class/lambda usage.

## 1. Why functions (DRY, decomposition, readability)

The examples show the four motivations:
- **De-duplication** (`01_duplication.py`): one `print_order` instead of repeating.
- **Decomposing complexity** (`02_complex.py`): `generate_report` orchestrates
  `fetch → filter → summarize`.
- **Information hiding** (`03_hiding.py`): `register_user` hides the steps behind one name.
- **Readability** (`04_readability.py`): `calculate_bill(cups, price)` names intent.

A function is a **first-class object**: assign it, pass it, return it, store it in a list/dict.

## 2. Parameters vs arguments; the full calling model

```python
def make_chai(tea, milk, sugar): ...        # 09_input_params.py
make_chai("Darjeeling", "Yes", "Low")        # positional
make_chai(tea="Green", sugar="Medium", milk="No")  # keyword (order-free)
```

- **Positional** args bind by position; **keyword** args bind by name (any order).
- **Default values**: `def f(order=None)` — defaults make params optional.
- **`*args`** collects extra positionals into a **tuple**; **`**kwargs`** collects extra
  keywords into a **dict** (`special_chai(*ingredients, **extras)`).
- Full signature grammar: `def f(pos_only, /, normal, *args, kw_only, **kwargs)`.
  - `/` → everything before is **positional-only**.
  - `*` (or `*args`) → everything after is **keyword-only**.

🤖 **Gen AI angle:** LLM SDK calls and tool wrappers use `**kwargs` heavily
(`client.chat(model=..., temperature=..., **extra)`); keyword-only params (`*`) force callers
to be explicit about flags like `stream=`.

## 3. The mutable-default-argument trap 🔴 (must know)

```python
# BUG (commented out in 09_input_params.py):
def chai_order(order=[]):
    order.append("Masala")
    print(order)
# Fix:
def chai_order(order=None):
    if order is None:
        order = []
    ...
```

Default values are evaluated **once, at function-definition time**, and the *same* object is
reused on every call. A mutable default (`[]`, `{}`) therefore **persists state across
calls** — `chai_order()` twice would give `['Masala']` then `['Masala', 'Masala']`. Fix:
default to `None` and create the container inside.

## 4. Pass-by-object-reference (mutating args)

```python
def edit_chai(cup):       # 09_input_params.py
    cup[1] = 42
edit_chai(chai)           # caller's list IS mutated → [1, 42, 3]
```

Arguments are passed by **object reference**. Mutating a mutable argument in place affects
the caller; **rebinding** the parameter (`cup = [...]`) does not. Immutable args (int, str,
tuple) can't be mutated, so they appear "pass-by-value".

## 5. Scope — LEGB rule

Name lookup order: **Local → Enclosing → Global → Built-in**.

```python
def chai_counter():           # 06_scopes.py
    chai_order = "lemon"      # Enclosing
    def print_order():
        chai_order = "Ginger" # Local (shadows enclosing)
        print(chai_order)     # Ginger
    print_order()
    print(chai_order)         # lemon (inner's local didn't leak)
```

- A name assigned anywhere in a function is **local** to that function (unless declared
  `global`/`nonlocal`).
- Inner scopes can **read** outer names but can't **rebind** them without a declaration.

## 6. `global` and `nonlocal`

```python
def kitchen():                # 08_global_scope.py
    global chai_type          # rebinds the module-level name
    chai_type = "Irnai"

def update_order():           # 07_nonlocal.py
    chai_type = "Elaichi"
    def kitchen():
        nonlocal chai_type    # rebinds the ENCLOSING function's variable
        chai_type = "Kesar"
    kitchen()                 # update_order's chai_type is now "Kesar"
```

- `global x` → assignments target the **module-global** `x`.
- `nonlocal x` → assignments target the **nearest enclosing function's** `x` (not global).
- Both are usually code smells for shared mutable state — prefer returning values or a class.

## 7. Closures

A nested function that **captures** variables from its enclosing scope and outlives it is a
**closure**. The captured variables live on (via `__closure__` cells). Basis for decorators,
factories, and stateful callbacks:
```python
def make_multiplier(n):
    def mul(x): return x * n   # captures n
    return mul
double = make_multiplier(2)
```
**Late-binding gotcha:** closures capture the *variable*, not its value at definition — a
classic bug when creating closures in a loop (all capture the final loop value); fix with a
default-arg `def f(x, n=n)`.

## 8. return

```python
def chai_status(cups_left):      # 10_return.py
    if cups_left == 0:
        return "Sorry, chai over"
    return "Chai is ready"
    print("chai")                # DEAD CODE — never runs after return
```

- A function with no `return` (or bare `return`) returns **`None`** (`idle_chaiwala`, `pass`).
- `return a, b, c` returns a **tuple**, enabling multiple-return + unpacking:
  `sold, remaining, not_paid = chai_report()` (`10_return.py`, `12_built_in.py`).
- Code after an unconditional `return` is unreachable.

## 9. Pure vs impure functions

```python
def pure_chai(cups):       # 11_types_of_functions.py — depends only on input, no side effects
    return cups * 10

def impure_chai(cups):     # mutates global state → impure (not recommended)
    global total_chai
    total_chai += cups
```

**Pure** = output depends only on inputs, no side effects → testable, cacheable
(`functools.lru_cache`), parallel-safe. Prefer purity; isolate side effects (I/O, network,
LLM calls) at the edges.

🤖 **Gen AI angle:** keep prompt-building and parsing pure; push the non-deterministic LLM
call to the boundary. Pure functions are what you can unit-test and `lru_cache`.

## 10. Recursion

```python
def pour_chai(n):          # 11_types_of_functions.py
    if n == 0:
        return "All cups poured"   # base case
    return pour_chai(n - 1)        # recursive case
```

Every recursion needs a **base case** + progress toward it. Python's default recursion limit
is ~1000 (`sys.setrecursionlimit`) and there's **no tail-call optimization** — deep recursion
→ `RecursionError`. Prefer iteration for deep/large inputs.

## 11. Lambdas & first-class functions

```python
strong_chai = list(filter(lambda chai: chai != "kadak", chai_types))   # 11_types...
```

- `lambda args: expr` — an anonymous, single-expression function. Use for tiny throwaways
  passed to `map`/`filter`/`sorted(key=...)`.
- Prefer a comprehension over `map`/`filter`+`lambda` when it reads better:
  `[c for c in chai_types if c != "kadak"]`.
- `sorted(data, key=lambda x: x["score"], reverse=True)` is the bread-and-butter use.

## 12. Docstrings & introspection

```python
def chai_flavor(flavor="masala"):    # 12_built_in.py
    """Return the flavor of chai."""
    return flavor

chai_flavor.__doc__    # the docstring
chai_flavor.__name__   # 'chai_flavor'
help(len)              # built-in help
```

Docstrings (PEP 257) document purpose/params/return; tools and `help()` read them. Functions
also expose `__name__`, `__defaults__`, `__annotations__` (type hints), `__closure__`.

## 13. Beyond the examples (be ready to mention)
- **Decorators** — functions wrapping functions (`@functools.wraps`, `@lru_cache`,
  `@cached_property`); the #1 follow-up after closures.
- **Type hints** — `def f(x: int) -> str:`; runtime-optional, checked by mypy/pyright.
- **`functools`** — `partial`, `reduce`, `lru_cache`, `wraps`.
- **Generators** (`yield`) — functions that produce lazy iterators (see folder 07).

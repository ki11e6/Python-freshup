# Day 1 — Python Core Foundations

**Time:** 2.5 hours · **Goal:** read and write Python without looking things up.

---

## Quick reference (interview-day skim)

| Concept | One-line answer |
|---|---|
| **Mutable types** | `list`, `dict`, `set`, custom objects |
| **Immutable types** | `int`, `float`, `str`, `bool`, `tuple`, `frozenset`, `None`, `bytes` |
| **`is` vs `==`** | `is` = same object in memory (identity); `==` = same value (equality). Use `is` only for `None`, `True`, `False`. |
| **Default-arg trap** | `def f(x=[]):` — the list is created **once** at function definition, shared across calls. Use `x=None` then `x = x or []`. |
| **`*args` / `**kwargs`** | Collect positional / keyword args into tuple / dict |
| **Truthiness** | Falsy: `False`, `0`, `0.0`, `""`, `[]`, `{}`, `()`, `None`. Everything else truthy. |
| **f-string** | `f"hello {name}, age {age+1}"` — preferred over `%` or `.format()` |
| **List comprehension** | `[x*2 for x in xs if x > 0]` |
| **Dict comprehension** | `{k: v for k, v in pairs}` |
| **Slicing** | `xs[start:stop:step]`, negative indices count from end, `xs[::-1]` reverses |
| **Unpacking** | `a, b, *rest = [1,2,3,4]` → `rest = [3,4]` |
| **Pass by** | Object reference (like JS). Reassignment doesn't affect caller; mutation does. |

---

## 0. Setup (15 min)

Python 3.14 is the current stable release (Oct 2025). Arch ships modern Python — verify what you have.

```bash
# verify — 3.13 or 3.14 both fine
python --version  # should be 3.13+

# install uv (modern, fast Python package manager — like pnpm for Python)
curl -LsSf https://astral.sh/uv/install.sh | sh
exec $SHELL   # reload

# create a scratch project for Day 1-3 exercises
mkdir -p ~/code/python-prep && cd ~/code/python-prep
uv init day1
cd day1
uv run python   # opens REPL inside project venv
```

Editor: use neovim or VSCode. Install the **Python** + **Pylance** extension in VSCode (or `pyright` LSP in neovim).

> **TS analogy:** `uv` ≈ `pnpm`. `pyproject.toml` ≈ `package.json`. `.venv/` ≈ `node_modules/`. `uv run` ≈ `pnpm exec`.

---

## 1. Data types & mutability (30 min)

```python
# primitives (all immutable)
x: int = 42
pi: float = 3.14
name: str = "sharath"
done: bool = True
nothing = None  # like undefined/null in TS

# collections
nums: list[int] = [1, 2, 3]              # mutable, ordered, indexed
point: tuple[int, int] = (10, 20)        # immutable, ordered, indexed
uniq: set[int] = {1, 2, 3}               # mutable, unordered, unique
ages: dict[str, int] = {"a": 1, "b": 2}  # mutable, key→value
frozen = frozenset({1, 2})               # immutable set
```

### Mutability — the #1 Python gotcha for JS devs

```python
a = [1, 2, 3]
b = a            # NOT a copy — both names point to same list
b.append(4)
print(a)         # [1, 2, 3, 4]  — surprise!

# to copy:
b = a.copy()     # shallow
b = a[:]         # also shallow (slice)
import copy
b = copy.deepcopy(a)  # deep
```

**Shallow vs deep:**
- **Shallow** = new outer container, same inner objects
- **Deep** = recursively copies everything

```python
a = [[1, 2], [3, 4]]
b = a.copy()
b[0].append(99)
print(a)  # [[1, 2, 99], [3, 4]]  — inner list is shared!
```

### `is` vs `==`

```python
a = [1, 2, 3]
b = [1, 2, 3]
a == b   # True  (same value)
a is b   # False (different objects)

x = None
x is None   # True — always use `is` for None, True, False
```

**Rule:** `==` for value comparison, `is` for identity (only really useful for `None`).

> **TS analogy:** `==` ≈ `===`, `is` ≈ `Object.is()`. Python has no `==` vs `===` distinction — there's just `==`.

---

## 2. Functions (30 min)

```python
def greet(name: str, greeting: str = "hello") -> str:
    return f"{greeting}, {name}"

greet("sharath")                        # "hello, sharath"
greet("sharath", "hi")                  # positional
greet(name="sharath", greeting="hi")    # keyword
greet(greeting="hi", name="sharath")    # keyword args can reorder
```

### `*args` and `**kwargs`

```python
def log(*args, **kwargs):
    # args = tuple of positional
    # kwargs = dict of keyword
    print(args, kwargs)

log(1, 2, 3, level="info", tag="api")
# (1, 2, 3) {'level': 'info', 'tag': 'api'}
```

> **TS analogy:** `*args` ≈ `...args: any[]`. `**kwargs` has no clean TS equivalent — closest is `options: Record<string, unknown>`.

### The default-argument trap (interview classic)

```python
# BUG: shared list across all calls
def add_item(x, bucket=[]):
    bucket.append(x)
    return bucket

add_item(1)  # [1]
add_item(2)  # [1, 2]  — wat
add_item(3)  # [1, 2, 3]

# FIX:
def add_item(x, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(x)
    return bucket
```

**Why:** default arg values are evaluated **once** when the function is defined, not each call.

### First-class functions & lambdas

```python
def apply(fn, x):
    return fn(x)

apply(lambda v: v * 2, 5)   # 10

# lambdas are limited to a single expression — use `def` for anything multi-line
```

---

## 3. Comprehensions (20 min)

The "Pythonic" way to transform/filter collections. Equivalent to `.map().filter()` in JS.

```python
nums = [1, 2, 3, 4, 5]

# list comp:  [expression for item in iterable if condition]
doubled = [n * 2 for n in nums]                    # [2, 4, 6, 8, 10]
evens   = [n for n in nums if n % 2 == 0]          # [2, 4]
matrix  = [[i*j for j in range(3)] for i in range(3)]  # nested

# dict comp
squared = {n: n*n for n in nums}                   # {1:1, 2:4, ...}

# set comp
uniq_lens = {len(w) for w in ["hi", "yo", "hello"]}  # {2, 5}

# generator expression (lazy — uses parens not brackets)
total = sum(n * n for n in nums)                   # no intermediate list
```

> **TS analogy:** `[n * 2 for n in nums]` ≈ `nums.map(n => n * 2)`. The filter version ≈ `nums.filter(...).map(...)`.

**Interview Q:** "When would you use a generator expression over a list comp?" → when you only need to iterate once and don't need to store all values — saves memory.

---

## 4. Control flow + slicing + unpacking (20 min)

### if / elif / else — Python has no switch (until 3.10's `match`)

```python
if x > 0:
    ...
elif x == 0:
    ...
else:
    ...

# `match` (3.10+) — structural pattern matching
match cmd:
    case "start":  ...
    case "stop":   ...
    case _:        ...  # default
```

### Loops

```python
for i in range(5):           # 0..4
    ...
for i, v in enumerate(xs):   # index + value
    ...
for k, v in d.items():       # dict iteration
    ...
for a, b in zip(xs, ys):     # parallel iteration
    ...

# while
while cond:
    ...
```

### Slicing

```python
xs = [0, 1, 2, 3, 4, 5]
xs[1:4]      # [1, 2, 3]      — stop is exclusive
xs[:3]       # [0, 1, 2]
xs[3:]       # [3, 4, 5]
xs[-2:]      # [4, 5]         — last 2
xs[::2]      # [0, 2, 4]      — every 2nd
xs[::-1]     # [5, 4, 3, 2, 1, 0]  — reverse
```

Strings slice the same way:

```python
"hello"[1:4]   # "ell"
"hello"[::-1]  # "olleh"
```

### Unpacking

```python
a, b, c = [1, 2, 3]
a, *rest = [1, 2, 3, 4]      # rest = [2, 3, 4]
*head, last = [1, 2, 3, 4]   # head = [1, 2, 3], last = 4
a, b = b, a                  # swap, no temp

# dict unpacking
config = {**defaults, **overrides}   # merge
```

### Truthiness

```python
# Falsy:  False, 0, 0.0, "", [], {}, (), None
# All other values are truthy

if items:           # idiomatic — "if non-empty"
    process(items)

# `or` for defaults
name = user_input or "anonymous"
```

---

## 5. Strings (10 min)

```python
name = "sharath"
age = 25

# f-strings (preferred since 3.6)
f"hello {name}, you are {age+1} next year"
f"{value:.2f}"           # 2 decimal places
f"{value:>10}"           # right-align in 10 chars
f"{value=}"              # prints "value=42" — debug helper (3.8+)

# common methods
"  hello  ".strip()      # "hello"
"a,b,c".split(",")       # ["a", "b", "c"]
",".join(["a","b","c"])  # "a,b,c"
"hello".replace("l", "L")  # "heLLo"
"hello".upper()          # "HELLO"
"hello".startswith("he") # True
"42".isdigit()           # True

# slicing works on strings too (they're immutable sequences)
"hello"[1:4]   # "ell"
```

---

## 6. Practice (35 min) — DO THESE

Write each in your REPL or a `.py` file. Don't move on until each works.

### Exercise 1: FizzBuzz with comprehension
```python
# Output a list of 1..30 where multiples of 3 → "Fizz",
# 5 → "Buzz", 15 → "FizzBuzz", rest → the number as string
```

### Exercise 2: Word frequency
```python
# Given: text = "the quick brown fox jumps over the lazy dog the fox"
# Return: dict of word → count, sorted desc by count
# {"the": 3, "fox": 2, ...}
```

### Exercise 3: Default-arg trap fix
```python
# Write a function `register(user, users=None)` that appends user
# to the users list and returns it. Verify multiple calls don't share state.
```

### Exercise 4: Flatten one level
```python
# flatten([[1,2],[3,4],[5]]) → [1, 2, 3, 4, 5]
# Use a comprehension.
```

### Exercise 5: Top-N
```python
# Given a dict of name → score, return the top N names by score.
# top_n({"a": 5, "b": 9, "c": 3}, 2) → ["b", "a"]
# Hint: sorted(d.items(), key=lambda kv: kv[1], reverse=True)
```

---

## End-of-Day-1 self-check

Before closing the laptop, you should be able to **explain in one sentence**:

- [ ] Why does the default-argument list trap happen?
- [ ] What's the difference between `is` and `==`?
- [ ] What's the difference between shallow and deep copy, with an example?
- [ ] What does `*args` collect? What about `**kwargs`?
- [ ] What's a generator expression vs a list comprehension?

If any are shaky, re-read that section before sleeping.

---

## What you skipped (don't worry yet)

- Classes / inheritance / OOP — **Day 2**
- Generators with `yield` — **Day 2**
- Decorators — **Day 2**
- Context managers (`with`) — **Day 2**
- Async / await — **Day 3**
- Type hints in depth — **Day 3**
- Pydantic — **Day 3**

Tomorrow we connect functions → decorators → and start seeing how FastAPI builds on this.

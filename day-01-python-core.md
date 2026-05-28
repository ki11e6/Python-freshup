# Day 1 — Python Core Foundations (Detailed)

**Time:** 2.5 hours (with stretch material for if you finish early)
**Goal:** Read and write Python without lookup. Answer any basic-level Python interview question.
**Scope:** Setup, data types, mutability, variables/references, functions, comprehensions, control flow, slicing, unpacking, strings.
**Out of scope today** (later days): classes (Day 2), decorators (Day 2), context managers (Day 2), generators with `yield` (Day 2), async/await (Day 3), type hints in depth (Day 3), Pydantic (Day 3).

> **All facts verified against:** official Python docs (docs.python.org), PEPs (peps.python.org), and Python Devguide. URLs in the References section at the bottom.

---

## Quick reference (interview-day skim)

| Concept | One-line answer |
|---|---|
| **Python stable version (May 2026)** | 3.14 stable since Oct 2025; 3.13 also fine for production |
| **Mutable types** | `list`, `dict`, `set`, `bytearray`, custom objects |
| **Immutable types** | `int`, `float`, `complex`, `str`, `bool`, `tuple`, `frozenset`, `bytes`, `None` |
| **Hashable** | All immutable built-ins. Mutables are unhashable → can't be dict keys or set members. |
| **`is` vs `==`** | `is` = same object (identity); `==` = same value (equality). Use `is` only for `None`, `True`, `False`. |
| **Dict ordering** | Insertion order is **guaranteed** since 3.7 (language spec, not just CPython). |
| **Small int caching** | CPython interns ints in `[-5, 256]` — `a is b` may unexpectedly be `True` for small ints. Implementation detail; don't rely on it. |
| **Default-arg trap** | Defaults evaluated once at function definition. Use `None` + check inside for mutable defaults. |
| **`*args` / `**kwargs`** | Collect extra positional / keyword args into tuple / dict |
| **Truthiness — falsy values** | `False`, `0`, `0.0`, `0j`, `""`, `[]`, `{}`, `()`, `set()`, `range(0)`, `None`, objects whose `__bool__` returns `False` |
| **f-string (3.6+)** | `f"hello {name}, age {age+1}"` — fastest formatting method |
| **f-string debug (3.8+)** | `f"{value=}"` prints `value=...` |
| **f-string nesting (3.12, PEP 701)** | Quotes inside f-strings can match outer quotes; backslashes allowed; multi-line OK |
| **List comprehension** | `[x*2 for x in xs if x > 0]` |
| **Dict/set comprehension** | `{k: v for k, v in pairs}`, `{x for x in xs}` |
| **Generator expression** | `(x*2 for x in xs)` — lazy, parens not brackets |
| **Slicing** | `xs[start:stop:step]`, negative indices, `xs[::-1]` reverses |
| **Unpacking** | `a, *rest = [1,2,3,4]`, dict merge `{**a, **b}` |
| **Walrus `:=` (3.8+)** | Assignment expression — assigns and returns value: `if (n := len(xs)) > 10:` |
| **`match` (3.10+)** | Structural pattern matching, not just switch |
| **Pass by** | "**Passed by assignment**" (official Python FAQ term). Rebinding doesn't affect caller; mutation does. Sometimes called "pass by object reference" in the community. |
| **`sorted()`** | Returns a new list; **stable** (preserves order of equal items); accepts `key=` callable |
| **PEP 8** | 4 spaces indent; ≤79 chars/line (≤99 if team agrees), **≤72 chars for docstrings/comments**; snake_case for vars/funcs, PascalCase for classes |

---

## 0. Setup (15 min)

### 0.1 Verify Python

```bash
python --version       # Should be 3.13+ (3.14 latest stable)
python3 --version      # Some distros use python3
which python
```

If you have 3.11 or older on Arch, install the latest:
```bash
sudo pacman -S python    # Arch typically ships current stable
```

> **Why version matters:** several features in this doc are version-gated (3.8 walrus, 3.9 lowercase generics, 3.10 `match`, 3.12 f-string upgrades). The interviewer may ask "since when?" — knowing the cutoff dates shows depth.

### 0.2 Install `uv` — modern package manager

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
exec $SHELL        # reload shell so `uv` is on PATH
uv --version
```

### 0.3 Create a scratch project

```bash
mkdir -p ~/code/python-prep && cd ~/code/python-prep
uv init day1
cd day1
ls -la
# pyproject.toml  README.md  main.py  .python-version
```

### 0.4 Run the REPL inside the venv

```bash
uv run python
>>> import sys
>>> sys.version
>>> exit()         # or Ctrl-D
```

> **TS analogy:** `uv` ≈ `pnpm`/`bun`. `pyproject.toml` ≈ `package.json`. `.venv/` ≈ `node_modules/`. `uv run` ≈ `pnpm exec`. `uv add` ≈ `pnpm add`.

### 0.5 Editor

- **VSCode:** install the **Python** extension (includes Pylance LSP).
- **Neovim:** install `pyright` LSP via `mason.nvim`.

That's setup. Move on.

---

## 1. Data types & mutability (40 min)

### 1.1 The built-in types

```python
# Numbers (all immutable)
i: int = 42
f: float = 3.14
c: complex = 1 + 2j
b: bool = True              # bool is a subclass of int — True == 1, False == 0

# Text (immutable)
s: str = "hello"
by: bytes = b"hello"        # immutable byte string

# Collections
lst: list = [1, 2, 3]                # mutable, ordered, indexed, allows duplicates
tup: tuple = (1, 2, 3)               # immutable, ordered, indexed, allows duplicates
st: set = {1, 2, 3}                  # mutable, unordered, unique, hashable elements only
fs: frozenset = frozenset({1, 2})    # immutable set
d: dict = {"a": 1, "b": 2}           # mutable, insertion-ordered (3.7+), hashable keys

# Bytes mutability variants
ba: bytearray = bytearray(b"hello")  # mutable bytes

# Special
nothing: None = None        # like JS null/undefined collapsed into one
```

> **Bool gotcha:** `True == 1` and `False == 0`, and `True + True == 2`. Don't rely on this in real code, but expect interview questions.

### 1.2 Mutable vs immutable — the divide

| Mutable | Immutable |
|---|---|
| `list` | `int`, `float`, `complex` |
| `dict` | `str` |
| `set` | `tuple` |
| `bytearray` | `frozenset` |
| custom classes (unless designed otherwise) | `bytes` |
|  | `None` |
|  | `bool` (it's an int) |

**Why it matters:**
1. **Hashability** — only immutables are hashable, so only immutables can be dict keys / set members.
   ```python
   {(1, 2): "ok"}       # ✅ tuple key
   {[1, 2]: "fail"}     # ❌ TypeError: unhashable type: 'list'
   ```
2. **Default arguments** — mutable defaults are the classic Python footgun (see §3.3).
3. **Aliasing** — assigning a mutable object to a new name doesn't copy it.

### 1.3 Aliasing — the #1 Python surprise for JS devs

```python
a = [1, 2, 3]
b = a            # NOT a copy — both names point to SAME list object
b.append(4)
print(a)         # [1, 2, 3, 4]  — surprise!

# To actually copy:
b = a.copy()     # shallow copy via method
b = a[:]         # shallow copy via full slice
b = list(a)      # shallow copy via constructor
import copy
b = copy.copy(a)     # shallow copy via module
b = copy.deepcopy(a) # deep copy
```

### 1.4 Shallow vs deep copy

- **Shallow** = new outer container, **inner objects still shared**.
- **Deep** = recursively copies everything, no sharing.

```python
a = [[1, 2], [3, 4]]
b = a.copy()             # shallow
b[0].append(99)
print(a)                 # [[1, 2, 99], [3, 4]]  — inner list is shared!
print(b)                 # [[1, 2, 99], [3, 4]]

import copy
c = copy.deepcopy(a)
c[0].append(123)
print(a)                 # unchanged — independent copies
```

> **TS analogy:** shallow ≈ `{...obj}` / `[...arr]`. Deep ≈ `structuredClone(obj)`.

**When to deep copy:** nested mutable structures you want to independently modify. Default to **not deep-copying** — it's expensive (O(n) and recursive); usually shallow + immutable inner data is the right design.

### 1.5 Identity vs equality — `is` vs `==`

- `==` — calls `__eq__`. Value comparison. **Use this 95% of the time.**
- `is` — checks if two names point to the same object in memory (identity). **Use only for `None`, `True`, `False`.**

```python
a = [1, 2, 3]
b = [1, 2, 3]
a == b      # True  — same value
a is b      # False — different objects in memory

x = None
x is None   # True — idiomatic
x == None   # works but lint warns

a = 256
b = 256
a is b      # True (probably)  — CPython caches small ints

a = 257
b = 257
a is b      # False (in REPL) — outside the cache range
```

> **CPython implementation detail:** small integers (`-5` to `256`) are cached and reused. So `is` may return `True` for them by coincidence. This is **not** language-level guaranteed — never rely on it. See Q (Advanced §3).

### 1.6 Hashability

An object is hashable if it has `__hash__` (and it's not `None`) and `__eq__`. Hashable objects can be dict keys or set members.

```python
# Hashable: all immutable built-ins
hash("hello")        # consistent within a process
hash((1, 2, 3))      # tuples are hashable IF their contents are hashable
hash(frozenset({1, 2}))

# Unhashable: mutable built-ins
hash([1, 2, 3])      # TypeError
hash({1, 2})         # TypeError
hash({"a": 1})       # TypeError

# Edge: tuple with mutable contents
hash((1, [2, 3]))    # TypeError — depth matters
```

---

## 2. Variables, references & memory model (15 min)

### 2.1 Python is "passed by assignment"

The official term from the [Python FAQ](https://docs.python.org/3/faq/programming.html#how-do-i-write-a-function-with-output-parameters-call-by-reference) is **"passed by assignment"** (sometimes called "call by assignment"). You'll also see "pass by object reference" in tutorials — that's the community name, not the official one. Use the official term in interviews.

Per the FAQ:

> "Remember that arguments are passed by assignment in Python. Since assignment just creates references to objects, there's no alias between an argument name in the caller and callee, and so no call-by-reference per se."

Operationally:

- **Rebinding** a parameter inside a function **does NOT** affect the caller.
- **Mutating** an object the parameter refers to **DOES** affect the caller (because both see the same object).

```python
def rebind(x):
    x = [99]            # rebinds local name — caller unaffected

def mutate(x):
    x.append(99)        # mutates the actual object — caller sees it

lst = [1, 2, 3]
rebind(lst);  print(lst)   # [1, 2, 3]
mutate(lst);  print(lst)   # [1, 2, 3, 99]
```

> **TS analogy:** identical to JS — primitives behave like values, objects like references, because passing happens by value of the reference.

### 2.2 Names vs objects

In Python, **variables are names bound to objects**, not boxes holding values. `a = [1, 2, 3]` creates the list, then binds the name `a` to it. `b = a` adds another name to the same object.

```python
a = [1, 2, 3]
b = a
import sys
sys.getrefcount(a)    # ≥ 3 (a, b, the temp from getrefcount itself)
id(a) == id(b)        # True — same object
```

`id(obj)` returns the object's identity (in CPython, its memory address).

### 2.3 Garbage collection — one paragraph

CPython uses **reference counting** as the primary mechanism — when an object's refcount drops to 0, it's freed immediately. A generational cyclic GC handles reference cycles (`gc` module). PyPy uses tracing GC instead. **You almost never need to think about this**, but expect a "what kind of GC?" question.

---

## 3. Functions (35 min)

### 3.1 Definition basics

```python
def greet(name: str, greeting: str = "hello") -> str:
    """Return a greeting string."""
    return f"{greeting}, {name}"

greet("sharath")                          # "hello, sharath"
greet("sharath", "hi")                    # positional
greet(name="sharath", greeting="hi")      # keyword args
greet(greeting="hi", name="sharath")      # keyword args can reorder
```

**Docstrings** (the triple-quoted string right after `def`) are the convention — `help(greet)` and tools like Sphinx read them. PEP 257 documents the conventions.

### 3.2 `*args` and `**kwargs`

```python
def log(*args, **kwargs):
    # args   = tuple of positional args
    # kwargs = dict of keyword args
    print(args, kwargs)

log(1, 2, level="info", tag="api")
# (1, 2) {'level': 'info', 'tag': 'api'}
```

At the **call site**, the asterisks **unpack**:

```python
nums = [1, 2, 3]
print(*nums)            # equivalent to print(1, 2, 3)

opts = {"sep": "-", "end": "!\n"}
print("a", "b", "c", **opts)
# a-b-c!
```

> **TS analogy:** `*args` ≈ rest params `...args: any[]`. `**kwargs` has no clean TS equivalent — closest is `options: Record<string, unknown>`.

**Keyword-only and positional-only parameters (3.8+):**

```python
def fn(a, b, /, c, d, *, e, f):
    # a, b — positional-only (must be passed positionally)
    # c, d — positional or keyword
    # e, f — keyword-only (must be passed by name)
    ...

fn(1, 2, 3, d=4, e=5, f=6)        # ✅
fn(1, b=2, c=3, d=4, e=5, f=6)    # ❌ b cannot be keyword
```

### 3.3 The default-argument trap (classic interview gotcha)

```python
# BUG — list shared across all calls
def add_item(x, bucket=[]):
    bucket.append(x)
    return bucket

add_item(1)  # [1]
add_item(2)  # [1, 2]  — wat
add_item(3)  # [1, 2, 3]
```

**Why:** the default value is evaluated **once** at function-definition time, not on each call. The single list is reused.

**Fix:** use `None` as sentinel.

```python
def add_item(x, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(x)
    return bucket
```

This is officially called out in the [Python FAQ](https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects).

### 3.4 First-class functions, lambdas, callables

```python
def apply(fn, x):
    return fn(x)

apply(lambda v: v * 2, 5)         # 10
apply(str.upper, "hello")         # "HELLO"
```

- **Lambdas** are single-expression anonymous functions. Use `def` for anything multi-statement or with annotations.
- Functions are objects — assign them, pass them, store them in lists/dicts.

```python
ops = {"add": lambda a, b: a + b, "sub": lambda a, b: a - b}
ops["add"](2, 3)        # 5
```

### 3.5 Variable scope — LEGB rule

Python looks up names in this order:
1. **L**ocal — current function
2. **E**nclosing — outer function (closures)
3. **G**lobal — module level
4. **B**uilt-in — `print`, `len`, etc.

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        print(x)       # "enclosing" — closure
    inner()
outer()

def reassign():
    global x           # declare we mean the module-level x
    x = "modified"

def nonlocal_demo():
    y = 1
    def bump():
        nonlocal y     # the enclosing y, not a new local
        y += 1
    bump(); bump()
    return y           # 3
```

`global` and `nonlocal` are needed only when you want to **assign** to a name from an outer scope. Reading works without declaration.

---

## 4. Comprehensions (25 min)

The "Pythonic" way to transform and filter. **Faster than `map`/`filter` + lambda**, and more readable than loops.

### 4.1 List comprehension

```python
# Shape: [expression for item in iterable if condition]
nums = [1, 2, 3, 4, 5]

doubled = [n * 2 for n in nums]                # [2, 4, 6, 8, 10]
evens   = [n for n in nums if n % 2 == 0]      # [2, 4]
flagged = ["even" if n % 2 == 0 else "odd"     # ternary inside
           for n in nums]
nested  = [[i*j for j in range(3)]             # nested
           for i in range(3)]
```

### 4.2 Dict comprehension

```python
squared = {n: n*n for n in [1, 2, 3]}          # {1:1, 2:4, 3:9}
inv     = {v: k for k, v in {"a":1,"b":2}.items()}    # {1:'a', 2:'b'}
filtered = {k: v for k, v in d.items() if v > 0}
```

### 4.3 Set comprehension

```python
unique_lengths = {len(w) for w in ["hi", "yo", "hello"]}   # {2, 5}
```

### 4.4 Generator expression

```python
# Same as list comp but with PARENS — lazy, no intermediate list
total = sum(n * n for n in range(1_000_000))   # constant memory

# Inside a function call, the parens can be omitted:
max(len(line) for line in open("file.txt"))
```

> **When to use a generator vs list comp:**
> - **Generator** — iterating once, large data, memory matters
> - **List comp** — need to index, slice, or iterate multiple times

### 4.5 Comprehension vs map/filter/loop

```python
# All three produce [2, 4, 6, 8, 10]
[n * 2 for n in nums if n % 2 == 0]                       # comp — fastest, idiomatic
list(map(lambda n: n * 2, filter(lambda n: n % 2 == 0, nums)))  # map+filter — slower
result = []
for n in nums:
    if n % 2 == 0:
        result.append(n * 2)                              # loop — slowest
```

> **TS analogy:** comp ≈ `.filter().map()` chain. Comp is roughly as fast as a hand-written loop because the body runs in optimized C, not Python.

---

## 5. Control flow + slicing + unpacking (25 min)

### 5.1 If / elif / else

```python
if x > 0:
    sign = "positive"
elif x == 0:
    sign = "zero"
else:
    sign = "negative"

# Ternary (single line)
sign = "positive" if x > 0 else "zero" if x == 0 else "negative"
```

### 5.2 `match` statement (3.10+, PEP 634/635/636)

Not "Python's switch" — it's **structural pattern matching**, more like Rust/OCaml/Scala.

```python
def handle(event):
    match event:
        case {"type": "click", "target": str(t)}:
            return f"click on {t}"
        case {"type": "key", "code": int(n)} if n > 0:
            return f"keycode {n}"
        case [first, *rest]:
            return f"list starting with {first}, then {rest}"
        case Point(x=0, y=0):              # class pattern (if Point defined)
            return "origin"
        case _:
            return "unknown"
```

Features:
- **Literal patterns** — `case 42:`
- **Capture patterns** — `case x:` binds; `case _:` doesn't
- **Sequence patterns** — `case [a, b, *rest]:`
- **Mapping patterns** — `case {"key": value}:`
- **Class patterns** — `case Point(x=0, y=0):`
- **OR patterns** — `case 1 | 2 | 3:`
- **Guard clauses** — `case x if x > 0:`

### 5.3 Loops

```python
# range — half-open interval, lazy
for i in range(5):              # 0, 1, 2, 3, 4
    ...
for i in range(2, 10, 2):       # 2, 4, 6, 8
    ...

# enumerate — index + value
for i, v in enumerate(["a","b","c"], start=1):
    print(i, v)                  # 1 a / 2 b / 3 c

# zip — parallel
for name, age in zip(names, ages):
    ...

# dict iteration
for key in d:                    # keys
    ...
for key, val in d.items():       # pairs
    ...
for val in d.values():
    ...

# while
n = 10
while n > 0:
    n -= 1

# break, continue, else (yes, loops have else)
for x in xs:
    if x == target:
        break
else:
    # runs only if loop completed without break
    print("not found")
```

The **`for...else`** construct is one of Python's quirky features — `else` runs only if the loop wasn't terminated by `break`.

### 5.4 Slicing

```python
xs = [0, 1, 2, 3, 4, 5]

xs[1:4]      # [1, 2, 3]    stop is EXCLUSIVE
xs[:3]       # [0, 1, 2]
xs[3:]       # [3, 4, 5]
xs[-2:]      # [4, 5]       negative = from end
xs[::2]      # [0, 2, 4]    step
xs[::-1]     # [5, 4, 3, 2, 1, 0]   reverse
xs[1:5:2]    # [1, 3]

# Slicing returns a NEW list (shallow copy of the range)
ys = xs[:]   # idiomatic shallow copy

# Assignment via slice — mutates in place
xs[1:3] = [99, 98]     # xs is now [0, 99, 98, 3, 4, 5]
xs[1:3] = []           # delete via slice
```

Strings slice the same way (but return new strings, since strings are immutable):

```python
"hello"[1:4]   # "ell"
"hello"[::-1]  # "olleh"
"hello"[-3:]   # "llo"
```

### 5.5 Unpacking

```python
# Basic
a, b, c = [1, 2, 3]
a, b, c = (1, 2, 3)       # any iterable
a, b = "ab"               # strings too

# Starred — collect rest
a, *rest = [1, 2, 3, 4]      # rest = [2, 3, 4]
*head, last = [1, 2, 3, 4]   # head = [1, 2, 3], last = 4
a, *mid, z = [1, 2, 3, 4, 5] # a=1, mid=[2,3,4], z=5

# Swap, no temp
a, b = b, a

# Unpacking in function calls
def f(a, b, c): ...
xs = [1, 2, 3]
f(*xs)
d = {"a": 1, "b": 2, "c": 3}
f(**d)

# Dict merge (3.5+ syntax, PEP 448)
combined = {**defaults, **overrides}
all_items = [*list1, *list2, *list3]

# Dict merge operators (3.9+, PEP 584)
combined = defaults | overrides    # new dict, override wins
defaults |= overrides              # in-place update
```

### 5.6 Truthiness

```python
# Falsy values (memorize this list — interview classic):
False, 0, 0.0, 0j, "", b"", [], {}, (), set(), range(0), None

# Everything else is truthy.

# Idiomatic
if items:                    # "if non-empty"
    process(items)
if not response.text:        # "if empty"
    raise ValueError()

# Short-circuit evaluation
name = user_input or "anonymous"      # `or` returns the first truthy
value = config and config.get("x")    # `and` returns the first falsy

# Note: `or` / `and` return the operand, not a bool
"" or "hi"     # "hi"
"hi" or "fb"   # "hi"
0 and 5        # 0
1 and 5        # 5
```

A class controls its own truthiness via `__bool__` (or `__len__` if `__bool__` is missing — empty collection → false).

### 5.7 Walrus operator `:=` (3.8+, PEP 572)

Assignment expression — assigns and returns the value. Useful when you want both a check and the value.

```python
# Without walrus
data = read_chunk()
while data:
    process(data)
    data = read_chunk()

# With walrus
while data := read_chunk():
    process(data)

# In list comp — avoid recomputing
result = [y for x in data if (y := expensive(x)) is not None]

# In if — capture for use in body
if (n := len(items)) > 100:
    log.warning(f"too many items: {n}")
```

Don't overuse — it can hurt readability.

### 5.8 Chained comparisons

```python
0 < x < 100             # ✅ Pythonic — equivalent to 0 < x and x < 100
a == b == c             # all three equal
1 < 2 < 3               # True
1 < 2 > 0               # True (legal but odd)
```

Each operand is evaluated only once — useful when expensive.

---

## 6. Strings & f-strings (20 min)

### 6.1 String basics

```python
s = "hello"
s = 'hello'         # single or double quotes — same
s = """multi
line"""             # triple-quoted (preserves newlines)
s = r"raw\nstring"  # no escape processing
s = b"bytes"        # bytes literal
s = rb"raw bytes"   # combine
```

Strings are **immutable sequences of Unicode code points** (str). Bytes are immutable sequences of integers 0-255 (bytes).

### 6.2 Common methods

```python
s = "  Hello, World!  "

s.strip()             # "Hello, World!"
s.lower()             # "  hello, world!  "
s.upper()             # "  HELLO, WORLD!  "
s.split(",")          # ["  Hello", " World!  "]
s.split()             # ["Hello,", "World!"]  — default splits on whitespace runs

",".join(["a", "b"])  # "a,b"
"hello".replace("l", "L")     # "heLLo"
"hello".startswith("he")      # True
"hello".endswith("lo")        # True
"hello".find("ll")            # 2  (returns -1 if not found)
"hello".index("ll")           # 2  (raises ValueError if not found)
"hello".count("l")            # 2
"42".isdigit()                # True
"  hello  ".lstrip()          # "hello  "
"  hello  ".rstrip()          # "  hello"
"abc".center(7, "-")          # "--abc--"
"abc".zfill(6)                # "000abc"
"hello world".title()         # "Hello World"
```

Strings are **immutable** — `s.replace()` returns a new string; the original is unchanged.

### 6.3 String formatting — f-strings (3.6+, preferred)

```python
name, age = "sharath", 25

f"hello {name}, age {age}"          # basic
f"hello {name}, age {age + 1}"      # expressions inline
f"{3.14159:.2f}"                    # "3.14"
f"{42:>10}"                         # "        42"  right-align in 10
f"{42:<10}"                         # "42        "  left-align
f"{42:^10}"                         # "    42    "  center
f"{42:010d}"                        # "0000000042"  zero-pad
f"{1234567:,}"                      # "1,234,567"  thousands sep
f"{0.25:.0%}"                       # "25%"        percent
f"{255:#x}"                         # "0xff"       hex
f"{255:b}"                          # "11111111"   binary
```

**Debug form (3.8+, very useful):**

```python
x = 42
print(f"{x=}")        # x=42
print(f"{x=:.2f}")    # x=42.00
print(f"{x+1=}")      # x+1=43
```

**3.12 (PEP 701) — much looser rules:**
- Reuse the **same quote** inside the f-string body
- **Backslashes** allowed inside braces
- **Multi-line** expressions allowed inside braces
- Nested f-strings work

```python
# Pre-3.12 (broken):  f"hello {d["name"]}"   # SyntaxError
# 3.12+ OK:
print(f"hello {d["name"]}")
print(f"path: {os.path.join('a', '\n')}")
print(f"sum: {sum([
    1, 2, 3,
])}")
```

### 6.4 Older formatting (know they exist)

```python
"hello %s, age %d" % ("sharath", 25)        # %-style — legacy
"hello {}, age {}".format("sharath", 25)    # .format() — verbose
"hello {name}, age {age}".format(name="sharath", age=25)
```

Performance order: **f-string > %-style > .format()**. Use f-strings unless you need a string template stored separately (e.g. user-defined formats — use `str.format` or `string.Template`).

### 6.5 Encoding

```python
"héllo".encode("utf-8")     # b'h\xc3\xa9llo'
b'h\xc3\xa9llo'.decode("utf-8")    # "héllo"

# str → bytes via encode; bytes → str via decode.
# DEFAULT is utf-8. Be explicit when crossing system boundaries.
```

Python 3 strings are **always Unicode**. If you see "encoding errors," you have a `str`/`bytes` confusion.

---

## 7. Common gotchas (quick recap)

1. **Mutable default args** — `def f(x=[])`. Use `None`.
2. **Aliasing** — `b = a` doesn't copy a list/dict.
3. **`is` vs `==`** — `is` is for identity; use `==` for value.
4. **Small int caching** — `a is b` may unexpectedly be `True` for small ints. Implementation detail.
5. **Truthy/falsy `0`** — `if value:` will skip when `value == 0`. Use `if value is not None:` if 0 is meaningful.
6. **`int / int` returns float** — `5 / 2 == 2.5`. Use `//` for integer division: `5 // 2 == 2`.
7. **`range` is half-open** — `range(5)` is 0..4, not 0..5.
8. **Modifying a list while iterating** — `for x in xs: xs.remove(x)` skips elements. Iterate over a copy `for x in xs[:]:`.
9. **Late-binding closures** — `[lambda: i for i in range(3)]` — all lambdas return 2. Use default arg: `lambda i=i: i`.
10. **`==` on floats** — `0.1 + 0.2 == 0.3` is `False`. Use `math.isclose()`.

---

## 8. Practice exercises (35 min — DO THESE)

Write each in REPL or a `.py` file. Don't skip — these expose gaps.

### Exercise 1: FizzBuzz with a list comp
Print 1..30. Multiples of 3 → "Fizz", of 5 → "Buzz", of 15 → "FizzBuzz", else the number.

### Exercise 2: Word frequency
```python
text = "the quick brown fox jumps over the lazy dog the fox"
# Return: dict of word → count, sorted desc by count
# {"the": 3, "fox": 2, ...}
# Hint: use collections.Counter or a plain dict
```

### Exercise 3: Default-arg trap
Write `register(user, users=None)` that appends and returns. Call it 3 times and prove the bucket isn't shared.

### Exercise 4: Flatten one level
`flatten([[1,2],[3,4],[5]])` → `[1, 2, 3, 4, 5]`. Use a nested list comp.

### Exercise 5: Top-N by value
```python
def top_n(d: dict, n: int) -> list:
    """Return top-n keys by value, descending."""
top_n({"a": 5, "b": 9, "c": 3}, 2)   # ["b", "a"]
# Hint: sorted(d.items(), key=lambda kv: kv[1], reverse=True)
```

### Exercise 6: Swap chars in a string (immutability)
Write `swap(s, i, j)` returning a new string with positions i and j swapped. Demonstrates strings are immutable.

### Exercise 7: Sliding window
Given `xs = [1,2,3,4,5]` and `n=3`, return `[[1,2,3], [2,3,4], [3,4,5]]`. Use slicing + list comp.

### Exercise 8: Anagram check
`is_anagram("listen", "silent")` → `True`. Two approaches: sorted strings, or `Counter`.

### Exercise 9: Group by length
```python
words = ["hi", "yo", "bye", "no", "hello"]
# {2: ["hi","yo","no"], 3: ["bye"], 5: ["hello"]}
# Hint: collections.defaultdict
```

### Exercise 10: f-string formatting drill
```python
# Given price=1234.5678 and label="Total"
# Produce: "Total      : $   1,234.57"
# (label left-aligned width 10, then ": ", then $, then 8-wide right-aligned, 2 decimals, thousands sep)
```

---

## 9. End-of-Day-1 self-check

Answer each in **one sentence** out loud:

- [ ] Why does the mutable default-argument trap happen?
- [ ] `is` vs `==` — when do you use which?
- [ ] What's the difference between shallow and deep copy? Give an example where it matters.
- [ ] What do `*args` and `**kwargs` collect? What does `*` and `**` do at a call site?
- [ ] Generator expression vs list comprehension — when each?
- [ ] Name all the falsy values.
- [ ] What does `xs[::-1]` do?
- [ ] What's the difference between `a, b = 1, 2` and `a, *b = 1, 2`?
- [ ] When was dict ordering guaranteed?
- [ ] Why is `a is b` sometimes True for small integers?

If any are shaky, re-read the section before moving to Day 2.

---

# Interview Question Bank — Day 1 topics

Practice format: cover the answer, speak yours aloud in 30-60 sec, then reveal and compare.

## Section A — Basic (10 questions)

### A1. What are the built-in data types in Python?
Numeric: `int`, `float`, `complex`, `bool` (subclass of int). Text: `str`. Bytes: `bytes`, `bytearray`. Sequences: `list`, `tuple`, `range`. Mappings: `dict`. Sets: `set`, `frozenset`. Special: `None`, `NoneType`.

### A2. Mutable vs immutable — give 3 of each.
**Immutable:** `int`, `str`, `tuple`, `frozenset`, `bytes`, `bool`, `None`.
**Mutable:** `list`, `dict`, `set`, `bytearray`, custom classes.
Immutable objects are hashable; can be dict keys / set members.

### A3. What's the difference between a list and a tuple?
- `list` is mutable, `tuple` is immutable
- `list` literal `[1,2,3]`, tuple literal `(1,2,3)` (or `1,2,3`)
- Tuples are hashable if contents are hashable; lists never are
- Tuples are slightly faster and use less memory
- Convention: lists for homogeneous collections; tuples for fixed-size heterogeneous records

### A4. What is `None`?
The singleton representing "no value." Type is `NoneType`. There's exactly one instance — always compare with `is None`, never `== None`. Functions with no `return` implicitly return `None`.

### A5. Explain `is` vs `==`.
`is` checks identity — whether two names point to the **same object**. `==` checks equality — whether two objects have the **same value** (calls `__eq__`). Use `is` only for `None`, `True`, `False`. For everything else, use `==`.

### A6. What does `*args` and `**kwargs` do?
At a function definition, `*args` collects extra positional args into a tuple; `**kwargs` collects extra keyword args into a dict. At a call site, `*` and `**` unpack a sequence/mapping into args.

```python
def f(*args, **kwargs):
    print(args, kwargs)
f(1, 2, x=3)              # (1, 2) {"x": 3}
xs = [1, 2]; f(*xs, x=3)
```

### A7. What's a list comprehension? Give an example.
A concise syntax for creating a list by transforming/filtering an iterable. Shape: `[expr for item in iterable if condition]`. Example: `[n*2 for n in range(5) if n % 2 == 0]` → `[0, 4, 8]`. Generally faster and more idiomatic than `for` loops with `append`.

### A8. What are all the falsy values in Python?
Per the official [Truth Value Testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing) docs:
- `None`, `False`
- **Zero of any numeric type:** `0`, `0.0`, `0j`, `Decimal(0)`, `Fraction(0, 1)`
- **Empty sequences/collections:** `""`, `b""`, `()`, `[]`, `{}`, `set()`, `range(0)`
- Any object whose `__bool__()` returns `False` (or `__len__()` returns `0` if `__bool__` is missing)

### A9. What's the difference between `/` and `//`?
`/` is **true division** — always returns a float (`5 / 2 == 2.5`). `//` is **floor division** — rounds toward negative infinity (`5 // 2 == 2`, `-5 // 2 == -3`). Use `%` for the remainder, or `divmod(a, b)` for both.

### A10. How do you reverse a string?
`s[::-1]` — slice with negative step. Returns a new string (strings are immutable). Alternatives: `"".join(reversed(s))`, but the slice is idiomatic.

---

## Section B — Intermediate (10 questions)

### B1. Explain the mutable default-argument trap.
Default argument values are evaluated **once at function definition**, not on each call. If the default is mutable (list/dict/set), the same object is reused across calls.

```python
def f(x, bucket=[]):
    bucket.append(x); return bucket
f(1)  # [1]
f(2)  # [1, 2]  — shared!
```

Fix: use `None` as sentinel and create a new container inside.

### B2. Shallow vs deep copy — when does it matter?
**Shallow** (`list.copy()`, `copy.copy()`) makes a new outer container but shares inner objects. **Deep** (`copy.deepcopy()`) recursively copies everything. Matters when you have nested mutable structures and want independent modification.

```python
a = [[1,2], [3,4]]
b = a.copy()
b[0].append(99)
# a is also [[1,2,99], [3,4]] — inner list shared
```

### B3. Why might `a is b` be `True` for small integers?
CPython caches small integers in the range `[-5, 256]` — there's exactly one `int` object per value in that range. So `a = 100; b = 100; a is b` is True. **This is a CPython implementation detail, not language-level guarantee** — never rely on it. Use `==`.

### B4. Is dict ordered? Since when?
Yes — insertion order is preserved. In CPython this was an implementation detail from 3.6, but it became a **language-level guarantee** in 3.7. Prior to 3.7, you'd use `collections.OrderedDict` for guaranteed ordering.

### B5. What's the difference between `sort()` and `sorted()`?
- `list.sort()` — in-place, returns `None`, only on lists
- `sorted(iterable)` — returns a new list, works on any iterable
- Both accept `key=` (callable to extract sort key) and `reverse=`
- Both are **stable** — equal items preserve their original order

### B6. What's a generator expression and when would you use one?
Like a list comp but with parens: `(x*2 for x in xs)`. **Lazy** — produces one value at a time, doesn't store the full result. Use when:
- Data is large and intermediate storage is wasteful
- You only need to iterate once
- You're piping into `sum()`, `max()`, `any()`, etc.

```python
total = sum(n*n for n in range(1_000_000))   # O(1) memory
```

### B7. What does the walrus operator `:=` do? When use it?
Added in 3.8 (PEP 572). Assigns and returns the value in one expression. Useful when you need to use a value in a condition AND in the body.

```python
if (n := len(items)) > 10:
    log.warn(f"too many: {n}")

while (line := f.readline()):
    process(line)
```

Use sparingly — can hurt readability.

### B8. Explain the `match` statement. How is it different from a switch?
Added in 3.10 (PEP 634). It's **structural pattern matching**, not a switch — it can match shape, types, sequences, mappings, and class attributes, and bind variables in the process.

```python
match event:
    case {"type": "click", "target": str(t)}:
        return f"click on {t}"
    case [first, *rest]:
        return f"list head {first}"
    case _:
        return "unknown"
```

A switch only dispatches on equality.

### B9. Why are mutable types unhashable?
Because hashability requires that an object's hash never changes over its lifetime (the hash determines bucket placement in dicts/sets). If you could mutate a list and then mutate it back, you'd break dict invariants. So Python disallows hashing of any mutable type.

### B10. How does Python pass arguments — by value or by reference?
Neither, exactly. Python uses **"passed by assignment"** (the official Python FAQ term; also called "pass by object reference" in the community). The function receives a binding to the same object the caller has. **Rebinding** the parameter inside the function doesn't affect the caller; **mutating** the underlying object does. Identical in semantics to JS.

---

## Section C — Advanced (10 questions)

### C1. What's the time complexity of common list/dict/set operations?
**list:** index O(1), append amortized O(1), pop end O(1), pop middle O(n), `in` O(n), insert(0) O(n).
**dict:** lookup, insert, delete — average O(1), worst O(n) (hash collisions).
**set:** `in`, add, remove — average O(1), worst O(n).
**str:** concatenation `a + b` O(n+m); building strings by repeated `+` is O(n²) — use `"".join(parts)` instead.

(Official source: https://wiki.python.org/moin/TimeComplexity)

### C2. How does CPython's garbage collector work?
Two mechanisms:
1. **Reference counting** — every object tracks how many names refer to it; freed instantly when refcount hits 0.
2. **Generational cyclic GC** (`gc` module) — handles reference cycles by tracing. Three generations, with newer objects collected more aggressively.

PyPy uses a tracing GC instead — no refcounting.

### C3. What's string interning? When does CPython intern strings automatically?
String interning stores only **one copy** of certain strings, so `a is b` is True for those. CPython automatically interns:
- All compile-time string literals
- Strings that look like valid identifiers (alphanumeric + underscore)
- Short strings in some contexts

You can force interning with `sys.intern(s)`. **Don't rely on auto-interning** — implementation detail.

### C4. Compare `is`, `==`, and `id()`.
- `id(obj)` returns the object's identity — in CPython, its memory address as a Python int
- `a is b` is equivalent to `id(a) == id(b)`
- `a == b` calls `a.__eq__(b)`, which compares values

`is` is fast (just a pointer comparison); `==` can be arbitrary code.

### C5. What's the cost of `+` vs `.join()` for strings?
Strings are immutable. `a + b` creates a new string of length n+m. Building a string with `+` in a loop is O(n²) — each iteration copies the growing result.

```python
# BAD — O(n²)
s = ""
for word in words:
    s = s + word

# GOOD — O(n)
s = "".join(words)
```

CPython has an optimization where `s += word` may mutate in place if `s` has refcount 1, but **don't rely on it**.

### C6. What is the GIL and what implications does it have for `list.append`?
The **Global Interpreter Lock** ensures only one thread runs Python bytecode at a time. Implication: **individual bytecode operations are atomic** — `list.append`, `dict.__setitem__` won't tear under threading. **But** multi-step operations (`if x not in lst: lst.append(x)`) are not atomic — you still need a lock for compound invariants.

(Python 3.13+ has an experimental no-GIL build per PEP 703, still optional in 3.14.)

### C7. What's the difference between `range()` in Python 2 and 3?
- Python 2: `range(n)` returns a **list**; `xrange(n)` returns a lazy iterator
- Python 3: `range(n)` returns a **range object** (lazy, indexable, supports `len`, `in`); `xrange` removed

The Python 3 `range` is even smarter than `xrange` — it's a sequence-like object with O(1) `len`, `in`, and indexing.

### C8. How does Python decide truthiness for a custom object?
Order of checks:
1. Call `__bool__()` if defined → must return `bool`
2. Else call `__len__()` if defined → `0` is falsy, anything else truthy
3. Else default: truthy

```python
class Cart:
    def __init__(self): self.items = []
    def __len__(self): return len(self.items)

if Cart():       # falsy when empty (via __len__)
    ...
```

### C9. Explain late binding in closures — what's the classic mistake?
Closures capture **variables by name**, not by value. The captured variable is looked up at **call time**, not definition.

```python
funcs = [lambda: i for i in range(3)]
[f() for f in funcs]      # [2, 2, 2] — all see final i

# Fix: bind via default arg (defaults evaluated at def time)
funcs = [lambda i=i: i for i in range(3)]
[f() for f in funcs]      # [0, 1, 2]
```

This is the same gotcha as JS pre-`let` (`var i` in a loop).

### C10. How does Python's integer arithmetic differ from C / Java for large numbers?
Python ints have **arbitrary precision** — no overflow. `2 ** 1000` just works. Internally, CPython uses small-int optimization (machine-word) below a threshold, then switches to a multi-word representation. The Python language guarantees correct results regardless of size; the cost is more CPU per operation for big ints.

```python
>>> 2 ** 200
1606938044258990275541962092341162602522202993782792835301376
```

---

## 10. References — verified May 2026

### Official Python documentation
- **Python language reference:** https://docs.python.org/3/reference/
- **Python tutorial:** https://docs.python.org/3/tutorial/ — sections 3-7 are Day 1 scope
- **Built-in types:** https://docs.python.org/3/library/stdtypes.html
- **Built-in functions:** https://docs.python.org/3/library/functions.html
- **Programming FAQ** (default-arg trap, pass semantics, etc.): https://docs.python.org/3/faq/programming.html
- **Time complexity wiki:** https://wiki.python.org/moin/TimeComplexity

### Style and conventions
- **PEP 8 — Style guide:** https://peps.python.org/pep-0008/
- **PEP 257 — Docstring conventions:** https://peps.python.org/pep-0257/

### Version-specific feature PEPs (cited above)
- **PEP 448** — Additional unpacking generalizations (3.5)
- **PEP 498** — Literal string interpolation (f-strings, 3.6)
- **PEP 572** — Walrus operator `:=` (3.8)
- **PEP 584** — Dict merge `|` operator (3.9)
- **PEP 585** — Built-in generics `list[int]` (3.9)
- **PEP 634/635/636** — Structural pattern matching `match` (3.10)
- **PEP 701** — Syntactic formalization of f-strings (3.12 — multi-line, quote reuse, backslashes)
- **PEP 703** — Making the GIL optional (3.13 experimental, 3.14 optional)

### Tooling
- **`uv` docs:** https://docs.astral.sh/uv/
- **Python releases / status:** https://devguide.python.org/versions/

---

## What you skipped (covered later — don't worry yet)

- Classes / inheritance / OOP → **Day 2**
- Iterators (the protocol) and generators with `yield` → **Day 2**
- Decorators (build one from scratch) → **Day 2**
- Context managers (`with`, `__enter__`/`__exit__`) → **Day 2**
- Exception handling deep dive → **Day 2**
- Type hints in depth (`typing` module) → **Day 3**
- `async` / `await` and the event loop → **Day 3**
- Dataclasses and Pydantic → **Day 3**
- Tooling: pytest, mypy, ruff → **Day 3**

Tomorrow's file: [day-02-python-intermediate.md](day-02-python-intermediate.md).

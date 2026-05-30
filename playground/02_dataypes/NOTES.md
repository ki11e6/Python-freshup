# Data Types, the Object Model & Mutability — Notes

> This is the single most-tested area in Python interviews. Master it cold.

## 1. Everything is an object

In CPython every value is a `PyObject` on the heap with three things:
- **identity** — its address, exposed by `id(x)` (in CPython, the memory address).
- **type** — `type(x)`, immutable for the life of the object.
- **value** — the payload.

A *variable* is just a **name bound to an object** (a reference), not a box holding bytes.
Assignment never copies a value — it rebinds a name.

```python
a = [1, 2, 3]
b = a            # b and a point to the SAME list object
b.append(4)
print(a)         # [1, 2, 3, 4]  ← aliasing
```

## 2. Mutable vs Immutable

| Immutable | Mutable |
|-----------|---------|
| `int`, `float`, `bool`, `complex` | `list` |
| `str`, `bytes` | `dict` |
| `tuple`, `frozenset` | `set`, `bytearray` |
| `range`, `NoneType` | most custom classes |

**Immutable** = the object's value can never change after creation. Operations that
"modify" it actually create a *new* object and rebind the name:

```python
s = "chai"
print(id(s))
s += " latte"     # builds a NEW string, rebinds s
print(id(s))      # different id
```

`chapter1.py` / `chapter2.py` demonstrate this with `id()`: an `int` keeps its id when
merely read; a `set` keeps the *same* id across `.add()` because mutation happens in place.

🤖 **Gen AI angle:** prompt templates and config strings are immutable — every `+=` on a
growing prompt allocates a new string (O(n) each time → O(n²) total). Build with a `list`
of parts + `"".join(...)`, or `io.StringIO`, when assembling large prompts/token streams.

## 3. `is` vs `==`, interning, and the small-int cache

- `==` compares **values** (calls `__eq__`).
- `is` compares **identity** (same object?).

```python
a = 256; b = 256; a is b      # True  — CPython caches ints in [-5, 256]
a = 257; b = 257; a is b      # often False (separate objects)
x = "hi"; y = "hi"; x is y    # often True — short string literals are interned
```

**Rule:** use `==` for value checks; reserve `is` for singletons (`None`, `True`, `False`).
`if x is None:` is correct; `if x == None:` is a smell.

## 4. Numbers

- `int` — arbitrary precision (no overflow). `1_000_000_000` underscores are just visual.
- `float` — IEEE-754 double; **not exact**. `0.1 + 0.2 != 0.3`. See `sys.float_info`.
- `bool` is a **subclass of `int`**: `True == 1`, `False == 0`, so `5 + True == 6`
  (`chapter4.py`, "upcasting"). `isinstance(True, int)` is `True`.
- For exact decimal math use `decimal.Decimal`; for exact ratios use `fractions.Fraction`
  (both imported in `chapter5.py`). Money → never `float`, use `Decimal`.

Operators: `/` true division (always float), `//` floor division, `%` modulo, `**` power
(`chapter3.py`).

🤖 **Gen AI angle:** float non-determinism + GPU reduction order is why LLM outputs aren't
bit-reproducible. For eval metrics and cost math, use `Decimal` or round explicitly.

## 5. Strings, bytes, encoding

- `str` is an immutable sequence of **Unicode code points**.
- `bytes` is an immutable sequence of **integers 0–255** (raw bytes).
- Conversion is explicit: `str.encode("utf-8")` → bytes; `bytes.decode("utf-8")` → str
  (`chapter6.py`, `"Chai Spécial"`).
- Slicing: `s[:8]`, `s[12:]`, `s[::-1]` (reverse). Slices on str/bytes return new objects.

**There is no implicit str↔bytes conversion in Python 3** — mixing them raises `TypeError`.
Network/file/LLM-API boundaries are always bytes; decode at the edge, work in `str` inside.

🤖 **Gen AI angle:** tokenizers operate on bytes (BPE byte-level), and "1 token ≈ 4 chars"
is a rough heuristic. Know that `len(s)` is code points, not bytes, not tokens.

## 6. Sequences: list vs tuple

- **list** — mutable, ordered. Methods: `append`, `extend`, `insert`, `pop`, `remove`,
  `reverse`, `sort` (`chapter8.py`). `+` concatenates (new list), `*` repeats.
- **tuple** — immutable, ordered (`chapter7.py`). Supports unpacking `a, b, c = t` and the
  one-line swap `a, b = b, a` (builds a tuple then unpacks — no temp variable).

**Why tuples?** Hashable (usable as dict keys / set members) if their contents are
hashable; signal "fixed record"; slightly less memory; safe to share.

Big-O (list): index `O(1)`, append amortized `O(1)`, `insert(0,..)`/`pop(0)` `O(n)`,
`x in list` `O(n)`. Need fast ends → `collections.deque`.

## 7. set & frozenset

- **set** — mutable, unordered, **no duplicates**, members must be hashable (`chapter9.py`).
- Operations: union `|`, intersection `&`, difference `-`, symmetric diff `^`.
- Membership `x in s` is **O(1)** average (hash table) vs O(n) for a list — huge for dedup
  and "have I seen this?" checks.
- `frozenset` — immutable, hashable, can be a dict key / set member.

🤖 **Gen AI angle:** dedup retrieved chunks, track seen doc IDs, compute vocab overlap — all
set operations. Use a `set` for the visited-frontier in agent/graph traversal.

## 8. dict

- Mutable mapping; keys must be **hashable**; **insertion-ordered** since 3.7 (language guarantee).
- Create: `{}`, `dict(a=1)`, dict comprehension. Access: `d[k]` (raises `KeyError`),
  `d.get(k, default)` (safe — `chapter10.py`).
- Methods: `keys()`, `values()`, `items()` (live views), `update()`, `pop()`, `popitem()`
  (removes last inserted), `del d[k]`.
- Lookup/insert/delete are **O(1)** average.

The `.get(key, default)` pattern (`chapter10.py`, `04_loops/10_dictionary_case.py`) is the
idiomatic way to avoid `KeyError`; also see `dict.setdefault` and `collections.defaultdict`.

🤖 **Gen AI angle:** dicts are everywhere — JSON API payloads, model `kwargs`, tool-call
arguments, embeddings keyed by id. `defaultdict(list)` for grouping chunks by source.

## 9. namedtuple & friends

`collections.namedtuple("chaiProfile", ["flavor", "aroma"])` (`chapter11.py`) — an immutable
tuple with **named fields**: `p.flavor` instead of `p[0]`. Lightweight, memory-efficient
record. Modern alternatives: `typing.NamedTuple` (typed), `@dataclass` (mutable, methods),
`pydantic.BaseModel` (validation — ubiquitous in Gen AI / FastAPI / LangChain).

## 10. Copying — shallow vs deep

```python
import copy
shallow = copy.copy(obj)        # new outer object, SHARED inner refs
deep    = copy.deepcopy(obj)    # fully independent recursive copy
```

`b = a` is *not* a copy (alias). `a[:]`, `list(a)`, `dict(a)` are shallow copies. The classic
bug: shallow-copying a list of lists, then mutating an inner list mutates "both".

## 11. Type conversion & checking

- Explicit: `int("5")`, `str(5)`, `list("ab") → ['a','b']`, `bool(0) → False`.
- **Truthiness:** `0`, `0.0`, `""`, `[]`, `{}`, `set()`, `None` are falsy; almost everything
  else is truthy (`chapter4.py`: `bool(0)` → `False`).
- Prefer `isinstance(x, int)` over `type(x) is int` (respects subclasses). Note the bool/int
  trap: `isinstance(True, int)` is `True`.

## Quick mutability cheat-sheet for the whiteboard
```
Immutable & hashable:  int float bool str bytes tuple frozenset None range
Mutable & unhashable:  list dict set bytearray  (and most custom objects)
Dict keys / set members MUST be hashable → can't use a list as a key, but a tuple works.
```

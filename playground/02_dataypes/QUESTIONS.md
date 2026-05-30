# Data Types & Memory Model — Interview Questions

Difficulty: 🟢 warm-up · 🟡 mid · 🔴 senior/staff

---

### 🟢 Q1. What's the difference between mutable and immutable types? Give examples.
**A.** Immutable objects can't change value after creation (`int, float, bool, str, bytes,
tuple, frozenset, None`); "modifying" them creates a new object. Mutable objects can change
in place (`list, dict, set, bytearray`, most custom classes). Test it with `id()`: a string
`+=` changes the id; a list `.append()` keeps it.

---

### 🟢 Q2. `is` vs `==`?
**A.** `==` compares value (`__eq__`); `is` compares identity (same object). Use `==` for
value equality, `is` only for singletons like `None`/`True`/`False`.

---

### 🟡 Q3. Why does `a = 256; b = 256; a is b` return `True` but `257` may return `False`?
**A.** CPython pre-caches (interns) small integers in the range **−5 to 256**, so all `256`
names point to one cached object. `257` is created fresh each time, so two `257`s can be
distinct objects. It's a CPython implementation detail — never rely on it; use `==`.

---

### 🟡 Q4. `True + True` — what's the result and why?
**A.** `2`. `bool` is a subclass of `int` (`True == 1`, `False == 0`), so booleans participate
in arithmetic. That's the "upcasting" in `chapter4.py`: `5 + True == 6`. Also why
`isinstance(True, int)` is `True` — a real gotcha when type-checking.

---

### 🟡 Q5. Why is `0.1 + 0.2 == 0.3` `False`? How do you handle money?
**A.** `float` is IEEE-754 binary double; 0.1/0.2/0.3 aren't exactly representable in base-2,
so rounding error makes the sum `0.30000000000000004`. For comparisons use
`math.isclose(a, b)`. For money/exact decimals use `decimal.Decimal("0.1")`; for exact
ratios use `fractions.Fraction`.

---

### 🟢 Q6. list vs tuple — when do you use each?
**A.** `list` = mutable, growing collection of homogeneous items. `tuple` = fixed,
immutable record; hashable (so usable as a dict key / set member), signals "don't mutate",
slightly lighter. Returning multiple values yields a tuple.

---

### 🟡 Q7. How does `a, b = b, a` work without a temp variable?
**A.** The right side `b, a` is evaluated first into a **tuple**, then unpacked into the
left-side names. Pure tuple packing/unpacking — no temporary needed (`chapter7.py`).

---

### 🟡 Q8. Why is `set`/`dict` membership O(1) but `list` membership O(n)?
**A.** `set`/`dict` are hash tables: `x in s` hashes `x` and checks one bucket — average
O(1). A `list` has no index on values, so `x in lst` scans linearly — O(n). Use a set for
"have I seen this?" / dedup; the example dedupes chai with `{chai for chai in ...}`.

---

### 🟡 Q9. What can be a dict key? Why can't a list?
**A.** Keys must be **hashable** (immutable identity-stable hash + `__eq__`). `list` is
mutable and unhashable, so it can't be a key — but a `tuple` of hashable items can. This is
why `frozenset` exists: a hashable set.

---

### 🟢 Q10. `d[k]` vs `d.get(k)`?
**A.** `d[k]` raises `KeyError` if missing; `d.get(k, default)` returns `default` (or `None`)
safely. The discounts example uses `discounts.get(coupon, (0, 0))` to fall back gracefully.
For accumulating, prefer `collections.defaultdict` or `dict.setdefault`.

---

### 🟡 Q11. Are dicts ordered?
**A.** Yes — insertion order is preserved and **guaranteed by the language since 3.7** (it
was a CPython 3.6 implementation detail first). For explicit ordering semantics there's also
`collections.OrderedDict` (adds `move_to_end`, order-sensitive equality).

---

### 🔴 Q12. Shallow vs deep copy — show a bug.
**A.**
```python
import copy
a = [[1, 2], [3, 4]]
b = copy.copy(a)       # shallow: outer new, inner lists SHARED
b[0].append(99)
print(a)               # [[1, 2, 99], [3, 4]]  ← a mutated too!
c = copy.deepcopy(a)   # fully independent
```
`b = a` is just aliasing (no copy). `a[:]`/`list(a)` are shallow. Reach for `deepcopy` when
nested mutable structures must be independent — but it's expensive, so avoid on hot paths.

---

### 🟡 Q13. str vs bytes — how do you convert, and why does it matter?
**A.** `str` = Unicode code points; `bytes` = raw 0–255 ints. Convert explicitly:
`s.encode("utf-8")` ↔ `b.decode("utf-8")`. Python 3 forbids implicit mixing (`TypeError`).
I/O, sockets, and HTTP/LLM API bodies are bytes — decode at the boundary, work in `str`
inside. `len(str)` counts code points, not bytes.

---

### 🔴 Q14. You're assembling a 50k-token prompt by `prompt += chunk` in a loop. What's wrong?
**A.** Strings are immutable, so each `+=` allocates a new string and copies everything —
O(n) per step → **O(n²)** overall. Collect parts in a `list` and `"".join(parts)` once
(O(n)), or use `io.StringIO`. Classic perf question dressed in Gen AI clothing.

---

### 🟡 Q15. What does `id()` return and is it stable?
**A.** A unique integer identifying the object for its lifetime; in CPython it's the memory
address. It's only unique among **currently live** objects — after an object is GC'd, its id
can be reused. Don't persist or compare ids across time.

---

### 🔴 Q16. Explain how variable assignment works in Python (pass-by-?).
**A.** Python is **"pass-by-object-reference"** (a.k.a. call-by-sharing). Names are bound to
objects; assignment rebinds the name, never copies the object. Passing an argument binds the
parameter to the same object. So mutating a mutable arg in a function is visible to the
caller (`05_functions/09_input_params.py`: `edit_chai` sets `cup[1]=42` and the caller's
list changes), but rebinding the parameter (`x = ...`) doesn't affect the caller.

---

### 🔴 Q17. `frozenset` vs `set` — when would you actually use a frozenset?
**A.** When you need set semantics but the value must be **hashable**: e.g. a set of sets,
a dict keyed by a group of tags, caching/memoizing on a collection of items, or a constant
that shouldn't be mutated. `frozenset` is immutable and hashable.

---

### 🟡 Q18. What's truthy/falsy in Python?
**A.** Falsy: `False, None, 0, 0.0, 0j, "", [], {}, set(), ()`, and objects whose
`__bool__`/`__len__` say so. Everything else is truthy. Enables idioms like `if items:` and
`x = val or default`. Caution: `0` and `""` are falsy, so `if x:` differs from
`if x is not None:` — pick deliberately.

---

### 🔴 Q19. `type(x) == int` vs `isinstance(x, int)`?
**A.** `isinstance` respects inheritance and ABCs; `type() ==` is exact-class only.
Prefer `isinstance`. Gotcha: since `bool` subclasses `int`, `isinstance(True, int)` is
`True` — if you must reject bools, check `type(x) is int` or `isinstance(x, bool)` first.

---

### 🔴 Q20. (Gen AI) You get model output as `bytes` from a streaming HTTP response split
mid-character. How do you decode safely?
**A.** A UTF-8 multibyte char can be split across chunks, so naive `.decode()` on each chunk
raises `UnicodeDecodeError`. Use an **incremental decoder** (`codecs.getincrementaldecoder`)
or buffer bytes and decode on complete boundaries. Demonstrates real understanding of the
str/bytes split, not just the API.

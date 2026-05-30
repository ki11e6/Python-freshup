# Comprehensions & Generators — Interview Questions

### 🟢 Q1. What's the general form of a list comprehension?
**A.** `[expr for item in iterable if condition]` — the `expr` maps each item, the optional
`if` filters. Equivalent to a `for`+`append` loop but faster and more concise.

### 🟢 Q2. Name the four comprehension/expression forms.
**A.** List `[...]`, set `{...}`, dict `{k: v ...}`, and generator expression `(...)`. The
first three eagerly build collections; the generator is lazy.

### 🟡 Q3. List comprehension `[...]` vs generator expression `(...)` — the difference?
**A.** A list comp **materializes** all elements in memory and is reusable/indexable. A
generator expression is **lazy** — yields one element at a time, O(1) memory, single-pass
(consumed once), no `len`/indexing. Use a generator for huge or streaming data and one-pass
aggregation.

### 🟡 Q4. When does a set comprehension help?
**A.** When you want uniqueness — it auto-dedupes. `{chai for chai in favourites}` removes
duplicate chais. Also good for building a membership set for O(1) `in` checks.

### 🟡 Q5. Read this nested comprehension:
`{spice for ingredients in recipes.values() for spice in ingredients}`
**A.** It flattens a dict-of-lists: outer loop iterates each recipe's ingredient list, inner
loop iterates each spice, and the `{}` collects them into a unique set. Loop clauses read
left-to-right exactly as nested `for`s would.

### 🔴 Q6. Why is `sum(x for x in data if x > 5)` better than `sum([x for x in data if x > 5])`?
**A.** The generator version never builds the intermediate list — it streams values into
`sum` one at a time (O(1) extra memory). The list version allocates the whole filtered list
first. For large data the generator is strictly better; you can drop the inner brackets when
the generator is the sole argument.

### 🔴 Q7. What does `yield` do?
**A.** It turns a function into a **generator**: each `yield` produces a value and suspends
the function's state (locals, instruction pointer) until the next value is requested,
resuming where it left off. Enables lazy, stateful iteration with arbitrary logic.
`StopIteration` is raised when the function returns.

### 🟡 Q8. Can you iterate a generator twice?
**A.** No — generators are single-pass and exhausted after one iteration. To reuse, either
recreate it or materialize with `list(gen)` (losing the memory benefit). `itertools.tee` can
duplicate an iterator but buffers consumed items.

### 🔴 Q9. (Gen AI) How do generators relate to LLM token streaming?
**A.** Streaming APIs yield tokens/chunks as they arrive; a generator lets you process or
forward each token immediately without buffering the full response — lower latency to first
token and constant memory. Same pattern for chunking documents during RAG ingestion and for
batching datasets that don't fit in memory.

### 🟡 Q10. Does the loop variable leak out of a comprehension?
**A.** No (Python 3) — comprehensions have their own scope, so `[x for x in it]` doesn't bind
`x` in the surrounding scope. A plain `for x in it:` loop *does* leave `x` defined afterward.

### 🟡 Q11. Write a dict comprehension that inverts a dict.
**A.** `{v: k for k, v in d.items()}` — swaps keys and values. (Assumes values are unique and
hashable; collisions keep the last one.)

### 🔴 Q12. When should you NOT use a comprehension?
**A.** When it has side effects (printing, I/O, mutating external state) — use a loop for
effects, comprehensions for building values. Also when nesting + conditions make it
unreadable, or when you need `break`/early-exit logic (a generator + `next` or a loop is
clearer). Readability over cleverness.

### 🟡 Q13. How do `any()`/`all()` with a generator help performance?
**A.** They **short-circuit**: `any(pred(x) for x in data)` stops at the first truthy result,
`all(...)` stops at the first falsy one — without scanning the whole iterable or building a
list. Ideal for "does any record match?" checks over large data.

### 🔴 Q14. What's `yield from` and when do you use it?
**A.** `yield from sub_iterable` delegates iteration to a sub-generator/iterable, yielding all
its values (and transparently forwarding `.send()`/`.throw()`/return value). Used to compose
generators — e.g. flattening nested streams or splitting a large generator into helpers.

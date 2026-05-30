# Loops & Iteration — Interview Questions

### 🟢 Q1. Difference between an iterable and an iterator?
**A.** An **iterable** has `__iter__` and can produce an iterator (list, str, dict, range).
An **iterator** has `__next__` (and `__iter__` returning itself), produces values one at a
time, raises `StopIteration` when done, and is consumed once. `for` calls `iter()` then
`next()` repeatedly.

### 🟢 Q2. Why use `enumerate` instead of `range(len(x))`?
**A.** Cleaner and less error-prone: `for i, v in enumerate(x)` gives both index and value
without manual indexing. `start=` controls the first index.

### 🟡 Q3. What does `zip` do when iterables have different lengths?
**A.** It stops at the **shortest** one (extra items in longer iterables are dropped). Use
`itertools.zip_longest(..., fillvalue=...)` to pad to the longest. `zip` is lazy in Py3.

### 🟡 Q4. Is `range(10**9)` memory-heavy?
**A.** No. `range` is a lazy sequence object that computes values on demand — O(1) memory
regardless of size. It's not a list.

### 🔴 Q5. Explain the `for...else` construct. When does `else` run?
**A.** The `else` block runs **only if the loop finished without executing `break`**. It's a
"search succeeded/failed" idiom: break when found, else-branch handles "not found". It does
NOT mean "if the loop body didn't run" — that's the common misconception.

### 🟢 Q6. `break` vs `continue`?
**A.** `break` exits the entire loop immediately (and skips any `for...else`); `continue`
skips the rest of the current iteration and moves to the next.

### 🟡 Q7. What is the walrus operator and give a real use.
**A.** `:=` assigns within an expression and returns the value. Useful in `while`/`if`
conditions and comprehensions to avoid duplicate calls: `while (line := f.readline()):
process(line)` or `if (n := len(data)) > 1000: warn(n)`.

### 🔴 Q8. Why can't you add/remove dict keys while iterating it?
**A.** Mutating the dict's size during iteration invalidates the internal iterator and
raises `RuntimeError: dictionary changed size during iteration`. Iterate over a snapshot
(`list(d.items())`) or collect changes and apply them after the loop.

### 🟡 Q9. How do you iterate keys vs values vs pairs of a dict?
**A.** `for k in d` (keys, the default), `for v in d.values()`, `for k, v in d.items()`.
The discounts example unpacks a tuple value inline: `percent, fixed = discounts.get(...)`.

### 🔴 Q10. (Gen AI) You're consuming a streaming token generator until it's exhausted.
Idiomatic loop?
**A.**
```python
for token in token_stream:        # cleanest — generator handles StopIteration
    emit(token)
# or with a sentinel when pulling manually:
while (tok := next(token_stream, None)) is not None:
    emit(tok)
```
Generators give constant-memory streaming — you don't materialize all tokens.

### 🟡 Q11. How would you transpose a matrix in one line?
**A.** `list(zip(*matrix))` — unpacking the rows as arguments to `zip` pairs them
column-wise. (Returns tuples; wrap inner in `list` if you need lists.)

### 🔴 Q12. When is a `while` loop better than a `for`?
**A.** When the number of iterations isn't known in advance and depends on a runtime
condition: retry-until-success, polling, reading a stream until EOF, or convergence loops.
Always ensure the body can make the condition false to avoid infinite loops.

### 🔴 Q13. You need the first matching item from a huge sequence. Loop or comprehension?
**A.** Don't build a list. Use a generator with `next`:
`first = next((x for x in data if pred(x)), None)`. It short-circuits at the first match and
uses O(1) memory — vs a list comprehension that scans and stores everything.

### 🟡 Q14. Name three `itertools` tools and what they do.
**A.** `chain` (concatenate iterables lazily), `islice` (slice an iterator without
materializing), `groupby` (group consecutive equal-key items), `product` (cartesian
product), `accumulate` (running totals). They're memory-efficient building blocks.

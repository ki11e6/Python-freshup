# Comprehensions & Generators — Notes

Comprehensions are Python's concise, fast way to build a collection from an iterable. There
are four forms, plus the lazy generator variant.

## 1. List comprehension

```python
iced_tea = [my_tea for my_tea in menu if "Iced" in my_tea]   # 01_list_compre.py
```

General form: `[expr for item in iterable if condition]`.
- Equivalent to a `for` loop with `.append`, but **faster** (optimized C-level loop, no
  repeated method lookup) and clearer.
- Supports multiple `for` clauses (nested) and multiple `if`s:
  `[x*y for x in a for y in b if x != y]`.
- Map+filter at once: the `expr` is the map, the `if` is the filter.

## 2. Set comprehension

```python
unique_chai = {chai for chai in favourite_chais}                       # 02_set_compre.py
unique_spices = {spice for ingredients in recipes.values()
                       for spice in ingredients}                       # nested + flatten
```

`{...}` builds a `set` → automatic **dedup**. The nested version flattens a list-of-lists
(dict values) into a single set of unique spices — note the loop order reads left-to-right
like nested `for`s.

## 3. Dict comprehension

```python
tea_prices_usd = {tea: price / 80 for tea, price in tea_prices_inr.items()}  # 03_dict_compre.py
```

Form: `{key_expr: value_expr for ... in ...}`. Great for transforming/filtering mappings,
inverting a dict (`{v: k for k, v in d.items()}`), or building lookup tables.

## 4. Generator expression (lazy!) 🔑

```python
total_cups = sum(sale for sale in daily_sales if sale > 5)   # 04_genrator_compre.py
```

- `(expr for item in iterable)` — uses **parentheses**, produces a **generator** (an
  iterator), not a list.
- **Lazy**: values are computed **one at a time, on demand**; nothing is stored. Constant
  O(1) memory regardless of input size.
- When passed as the *sole* argument to a function you can drop the extra parens:
  `sum(... for ...)`, `any(...)`, `max(...)`.
- Consumed **once** — iterate again and it's empty.

**List vs generator — the key tradeoff:**
| | list comp `[...]` | generator `(...)` |
|--|------------------|-------------------|
| Memory | materializes all items | one at a time, O(1) |
| Reusable | yes | no (single-pass) |
| Random access / len | yes | no |
| Best for | small/medium, reused, indexed | huge/streaming, one-pass aggregation |

## 5. `yield` generators (functions)

A function with `yield` returns a generator; each `yield` produces a value and **suspends**
state until the next `next()`:
```python
def read_chunks(f, size=1024):
    while (chunk := f.read(size)):
        yield chunk
```
Same laziness as generator expressions but with arbitrary logic. `yield from sub_gen()`
delegates to another generator.

🤖 **Gen AI angle:** this is exactly how **token streaming** works — the SDK yields tokens as
they arrive; you process/forward each without buffering the whole completion. Generators also
power **chunking** large documents for RAG ingestion and **batching** without loading
everything into memory.

## 6. Readability limits

Comprehensions should stay **one logical line of intent**. If you have nested loops + multiple
conditions + a complex expression, a plain `for` loop is more readable. Don't put side
effects (printing, appending elsewhere) inside a comprehension — use a loop for effects,
comprehensions for *building values*.

## 7. Performance notes

- List/set/dict comprehensions are faster than equivalent `for`+`append`/`add` loops.
- They run in their **own scope** (Python 3) — the loop variable doesn't leak out (unlike a
  bare `for` loop, where `item` persists after the loop).
- For aggregation over huge data, prefer a generator into `sum`/`any`/`all`/`min`/`max` to
  avoid building an intermediate list.
- `any(pred(x) for x in data)` / `all(...)` **short-circuit** — stop at the first decisive
  element.

## Quick reference
```
[x for x in it]        list comprehension
{x for x in it}        set comprehension
{k: v for ... in it}   dict comprehension
(x for x in it)        generator expression (lazy, single-pass)
```

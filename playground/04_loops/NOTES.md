# Loops & Iteration — Notes

## 1. for over an iterable

```python
for token in range(1, 11): ...      # 01_token_dispneser.py
for name in orders: ...              # 03_tea_orders.py
```

`for` iterates any **iterable** (anything with `__iter__`): lists, tuples, strings, dicts,
sets, files, generators. Under the hood it calls `iter(obj)` to get an **iterator**, then
`next()` until `StopIteration`.

`range(start, stop, step)` is **lazy** — it doesn't build a list, it computes values on
demand (O(1) memory even for `range(10**9)`).

## 2. enumerate — index + value

```python
for idx, item in enumerate(menu, start=1):   # 04_tea_menu.py
    print(f"{idx} : {item}")
```

Use `enumerate` instead of `for i in range(len(x)): x[i]` — cleaner and less error-prone.
`start=1` for 1-based numbering.

## 3. zip — parallel iteration

```python
for name, amount in zip(names, bills):        # 05_order_summary.py
    print(f"{name} paid {amount}")
```

`zip` pairs elements positionally and **stops at the shortest** iterable. Use
`itertools.zip_longest` to pad to the longest. `zip(*matrix)` transposes. `zip` is lazy
(returns an iterator) in Python 3.

## 4. while loops

```python
while temperature < 100:        # 06_tea-temperature.py
    temperature += 15
```

Use when the iteration count isn't known ahead of time (loop until a condition flips). Risk:
**infinite loops** if the condition never becomes false — make sure the body changes the
condition. `+=` is in-place add.

## 5. break / continue / for-else

```python
for flavour in flavours:                 # 07_put_of_order.py
    if flavour == "Out of Stock":
        continue                          # skip to next iteration
    if flavour == "Discontinued":
        break                             # exit the loop entirely
    print(flavour)
```

- `continue` → skip rest of this iteration.
- `break` → exit the loop immediately (skips the `else`).
- **`for ... else`** (`08_for_else.py`): the `else` runs **only if the loop completed
  without hitting `break`**. Great for search loops: "found it → break; else → not found".
  ```python
  for name, age in staff:
      if age <= 18:
          eligible = name; break
  else:
      print("No one eligible")     # only if no break
  ```
  This trips up most candidates — `else` here means "no break", *not* "if loop didn't run".

## 6. The walrus operator `:=` (assignment expression, 3.8+)

```python
if remainder := value % 5:                       # 09_walrus.py
    print(f"remainder is {remainder}")

while (flavor := input("Choose: ")) not in flavors:
    print(f"{flavor} not available")
```

`:=` **assigns and returns** a value within an expression — lets you bind a variable in an
`if`/`while` condition or comprehension, avoiding a duplicate call or a pre-loop read. Keep
it readable; parenthesize when mixing with other operators.

🤖 **Gen AI angle:** streaming reads — `while (chunk := stream.read()) :` or
`while (tok := next(token_stream, None)) is not None:` to consume until exhausted.

## 7. Iterating dicts

```python
for user in users:                               # 10_dictionary_case.py
    percent, fixed = discounts.get(user["coupon"], (0, 0))   # unpack tuple value
```

- `for k in d` iterates **keys**; `for k, v in d.items()` iterates pairs; `d.values()` for
  values. Tuple values unpack inline: `percent, fixed = (...)`.
- **Don't mutate a dict's size while iterating it** → `RuntimeError`. Iterate over
  `list(d.keys())` if you must add/remove during the loop.

## 8. Idioms & performance

- Prefer iterating the object directly over indexing: `for x in seq` not `for i in range(len(seq))`.
- For transforms, a **comprehension** (folder 07) is faster and clearer than an append loop.
- Need lazy/streaming? Use a **generator** — constant memory, values on demand.
- `itertools` is the power toolkit: `chain`, `islice`, `groupby`, `product`, `accumulate`,
  `count`, `cycle`, `zip_longest` — often the "right answer" to loop-heavy interview problems.
- `sum(... for ...)` / `any(...)` / `all(...)` consume iterables lazily and short-circuit.

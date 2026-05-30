# Conditionals & Control Flow — Notes

## 1. if / elif / else

```python
if cup == "small":
    print("10 rupees")
elif cup == "medium":
    print("15 rupees")
else:
    print("Unknown")
```

- Branches are tested **top-to-bottom**; the first truthy one runs, the rest are skipped.
- The condition is evaluated for **truthiness**, not strict `True` (so `if items:` works on
  any container — empty = falsy).
- `mini_story_1.py`: a bare `if kettle_boiled:` checks the value's truthiness directly —
  don't write `if x == True:`.

## 2. Ternary (conditional expression)

```python
delivery_fees = 0 if order_amount > 300 else 30   # delivery_fees_waiver.py
```

Form: `value_if_true if condition else value_if_false`. It's an **expression** (returns a
value), unlike the `if` statement. Keep it to simple either/or; nesting ternaries hurts
readability.

## 3. Logical operators & short-circuiting

```python
if snack == "cookies" or snack == "samosa":   # snak_suggestion.py
can_serve = water_hot and tea_added            # chapter4-style boolean combine
```

- `and` returns the **first falsy** operand or the last (short-circuits: stops as soon as
  the result is known). `or` returns the **first truthy** operand or the last.
- They return **operands, not just booleans**: `"" or "default"` → `"default"`;
  `x and x.method()` guards against calling on a falsy/None `x`.
- `not` flips truthiness.

🤖 **Gen AI angle:** `config.get("temperature") or 0.7` to supply defaults; `resp and
resp.choices` to guard before indexing into an API response. Beware: `0 or 0.7` gives `0.7`
even though `0` may be a *valid* temperature — use `x if x is not None else default` when
`0`/`""` are legitimate values.

## 4. Nested conditionals

```python
if device_status == "active":      # smart_thermostat.py
    if temperature > 35:
        print("High temperature alert!")
    else:
        print("Temperature is normal")
else:
    print("Device is offline")
```

Works, but deep nesting is a smell. Prefer **guard clauses / early returns** to flatten:
```python
if device_status != "active":
    print("Device is offline"); return
if temperature > 35:
    ...
```

## 5. match / case (structural pattern matching, Python 3.10+)

```python
match seat_type:                   # train_seat.py
    case "sleeper": ...
    case "ac": ...
    case _:                        # wildcard / default
        print("Invalid")
```

- `match` is **not** a C-style switch — it does **structural pattern matching**: can match
  literals, sequences, mappings, classes, and **bind** variables.
- `case _:` is the catch-all (must be last). Cases are tried top-down.
- Powerful patterns:
  ```python
  match command:
      case ["go", direction]:        # sequence + capture
          move(direction)
      case {"action": "tool", "name": name}:   # mapping pattern
          call(name)
      case Point(x=0, y=y):          # class pattern + capture
          ...
      case str() if len(seat_type) > 0:  # guard
          ...
  ```

🤖 **Gen AI angle:** dispatching on tool-call / agent action payloads (often dicts) reads
cleanly with mapping patterns: `case {"tool": "search", "query": q}:`.

## 6. Common pitfalls

- `if x = 5:` is a `SyntaxError` — assignment isn't a condition (use `==`; for assign-in-
  condition use the walrus `:=`, see loops notes).
- Comparing to `None` / `True` / `False` → use `is`, not `==`.
- `if x == True:` is redundant and buggy for non-bool truthy values — use `if x:`.
- Chained comparisons work and are Pythonic: `if 0 <= temp <= 100:`.
- Mutating-while-branching on floats → remember float equality is fuzzy (`==` on floats is
  risky; use `math.isclose`).

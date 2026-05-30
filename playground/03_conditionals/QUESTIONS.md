# Conditionals & Control Flow — Interview Questions

### 🟢 Q1. How does `if`/`elif`/`else` evaluate?
**A.** Top-down; the first branch whose condition is truthy executes and the rest are
skipped. Conditions are evaluated for truthiness, not strict equality to `True`.

### 🟢 Q2. What's a ternary expression? Give the syntax.
**A.** `value_if_true if condition else value_if_false`. It's an expression that returns a
value, e.g. `fees = 0 if amount > 300 else 30`.

### 🟡 Q3. Do `and`/`or` return booleans?
**A.** No — they return one of the **operands**. `and` returns the first falsy operand (or
the last if all truthy); `or` returns the first truthy operand (or the last). And they
**short-circuit** — stop evaluating once the result is determined. Enables `x or default`
and `obj and obj.attr` idioms.

### 🔴 Q4. `temp = config.get("temperature") or 0.7` — what's the subtle bug?
**A.** If the configured temperature is `0` (a valid value), `0 or 0.7` evaluates to `0.7`
because `0` is falsy. The `or` default trick treats valid falsy values as "missing". Fix:
`temp = config["temperature"] if "temperature" in config else 0.7`, or
`temp = t if (t := config.get("temperature")) is not None else 0.7`.

### 🟡 Q5. How do you compare against `None`?
**A.** `if x is None:` / `if x is not None:` — identity check, since `None` is a singleton.
Avoid `== None`.

### 🟡 Q6. How would you flatten deeply nested `if`s?
**A.** Use **guard clauses / early returns**: handle the negative/exit cases first and
return early, so the happy path stays un-indented. Reduces cognitive load and nesting.

### 🟡 Q7. Is Python's `match` the same as a C `switch`?
**A.** No. It's **structural pattern matching** (3.10+): it matches and destructures
literals, sequences, mappings, and class patterns, and binds variables. A `switch` only
compares one value to constants. `case _:` is the wildcard default.

### 🔴 Q8. Show a `match` that destructures a dict and binds a variable.
**A.**
```python
match action:
    case {"tool": "search", "query": q}:
        run_search(q)
    case {"tool": name}:
        run_tool(name)
    case _:
        raise ValueError("unknown action")
```
Mapping patterns match on present keys (extra keys are allowed) and bind values — ideal for
dispatching on agent/tool-call payloads.

### 🟡 Q9. What's the difference between `case _` and `case x`?
**A.** `case _` is the wildcard — matches anything, binds nothing. `case x` also matches
anything but **captures** the value into `x`. A bare name in a case is a capture pattern,
not a comparison to an existing variable (a common surprise).

### 🟢 Q10. Why is `if x == True:` discouraged?
**A.** It's redundant for booleans and wrong for other truthy values (e.g. a non-empty list
is truthy but `!= True`). Use `if x:` for truthiness or `if x is True:` if you truly need
the singleton.

### 🟡 Q11. Can you chain comparisons?
**A.** Yes: `if 0 <= temperature <= 100:` is evaluated as `0 <= temperature and
temperature <= 100`, with `temperature` evaluated once. Pythonic and readable.

### 🔴 Q12. When does short-circuit evaluation matter for correctness (not just speed)?
**A.** When the right operand has side effects or could error: `if user is not None and
user.is_active():` — the `and` prevents calling `.is_active()` on `None`. Order matters;
swapping the operands would raise `AttributeError`.

# Day 2 — Python Intermediate

**Time:** 2.5 hours · **Goal:** OOP, generators, decorators, context managers — the building blocks every Python framework uses.

---

## Quick reference (interview-day skim)

| Concept | One-line answer |
|---|---|
| `__init__` vs `__new__` | `__new__` creates the instance; `__init__` initializes it. You almost never override `__new__`. |
| `@classmethod` | First arg is `cls` (the class). Used for alternate constructors. `Foo.from_dict(d)` pattern. |
| `@staticmethod` | No implicit first arg. Just a function namespaced under the class. |
| `@property` | Turns a method into an attribute access (`obj.x` not `obj.x()`). |
| MRO | Method Resolution Order — Python 3 uses **C3 linearization**. Inspect via `Foo.__mro__`. |
| `super()` | Calls the next class in MRO. In Python 3, just `super().method()` — no args needed. |
| Iterator | An object with `__iter__` and `__next__`. Raises `StopIteration` when done. |
| Generator | A function with `yield`. Auto-implements iterator protocol. Lazy. |
| Decorator | A callable that takes a function and returns a function. `@foo` is sugar for `f = foo(f)`. |
| Context manager | An object with `__enter__` and `__exit__`. Used with `with` statement. Or use `@contextmanager`. |
| `try / except / else / finally` | `else` runs only if no exception; `finally` always runs |
| Custom exception | Subclass `Exception`. Never subclass `BaseException` directly. |
| Duck typing | "If it walks like a duck..." — Python checks behavior, not type |
| `__slots__` | Restricts attributes to a fixed set; saves memory; no per-instance `__dict__` |

---

## 1. Classes & OOP (40 min)

### Basic class

```python
class User:
    # class attribute (shared across all instances)
    species = "homo sapiens"

    def __init__(self, name: str, age: int):
        # instance attributes
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"hi, I'm {self.name}"

    def __repr__(self) -> str:
        # called by repr() and shown in REPL — make it useful
        return f"User(name={self.name!r}, age={self.age})"

    def __str__(self) -> str:
        # called by str() and print() — human-readable
        return f"{self.name} ({self.age})"


u = User("sharath", 25)
print(u)        # sharath (25)
print(repr(u))  # User(name='sharath', age=25)
```

> **TS analogy:** `self` is `this`. `__init__` is `constructor`. `__repr__` has no JS equivalent — it's for debug printing.

### `@classmethod` vs `@staticmethod` vs `@property`

```python
class User:
    def __init__(self, name, age):
        self.name = name
        self._age = age

    @property
    def age(self):
        """Accessed as user.age (not user.age())"""
        return self._age

    @age.setter
    def age(self, value):
        if value < 0:
            raise ValueError("age cannot be negative")
        self._age = value

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Alternate constructor — uses cls so subclasses work correctly."""
        return cls(data["name"], data["age"])

    @staticmethod
    def is_valid_age(value: int) -> bool:
        """Utility function — doesn't need self or cls."""
        return 0 <= value < 150
```

**When to use which (interview Q):**
- `@property` — computed/validated attribute access
- `@classmethod` — alternate constructor or anything needing the class itself (e.g. `cls()`)
- `@staticmethod` — utility function that logically belongs to the class but doesn't use class state

### Inheritance + MRO (5 min)

```python
class Animal:
    def speak(self): return "..."

class Dog(Animal):
    def speak(self): return "woof"

class Puppy(Dog):
    def speak(self):
        parent = super().speak()
        return f"small {parent}"

Puppy.__mro__
# (Puppy, Dog, Animal, object)
```

**Multiple inheritance: Python uses C3 linearization** — deterministic order based on inheritance graph. Avoid deep multiple inheritance; prefer composition. But know that mixins (like `UserMixin`, `LoggingMixin`) are a common pattern.

### `__slots__` (mention only — for interview "have you heard of...")

```python
class Point:
    __slots__ = ("x", "y")    # no per-instance __dict__
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
p.z = 5    # AttributeError
```

Why it matters: significant memory savings when you have millions of small objects. Used by `dataclass(slots=True)`.

---

## 2. Exception handling (15 min)

```python
try:
    result = risky()
except ValueError as e:
    # specific exception type
    log.error(f"bad value: {e}")
    raise   # re-raise current exception, preserving traceback
except (KeyError, IndexError) as e:
    # multiple types in one except
    return None
else:
    # runs ONLY if no exception was raised — uncommon but useful
    log.info("succeeded")
finally:
    # always runs — for cleanup
    cleanup()
```

### Custom exceptions
```python
class NotFoundError(Exception):
    """Raised when an entity is not found."""

class UserNotFoundError(NotFoundError):
    def __init__(self, user_id: int):
        super().__init__(f"user {user_id} not found")
        self.user_id = user_id

raise UserNotFoundError(42)
```

> **Interview Q:** "What's the difference between `raise` and `raise e`?" → `raise` re-raises the current exception with its original traceback; `raise e` raises that exception and adds a new traceback frame. Use bare `raise` inside `except`.

### Exception chaining
```python
try:
    parse(data)
except ValueError as e:
    raise RuntimeError("config invalid") from e   # preserves cause chain
```

---

## 3. Iterators & Generators (25 min)

### Iterator protocol
```python
class CountUp:
    def __init__(self, end):
        self.end = end
        self.n = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.n >= self.end:
            raise StopIteration
        self.n += 1
        return self.n

for x in CountUp(3):   # 1, 2, 3
    print(x)
```

### Generators — much easier
```python
def count_up(end):
    n = 0
    while n < end:
        n += 1
        yield n

list(count_up(3))   # [1, 2, 3]
```

A generator function returns a **generator object** (an iterator) when called. Execution pauses at each `yield` and resumes on next `next()` call.

### Why use them?
- **Lazy evaluation** — values produced one at a time, not stored in memory
- **Composable** — chain them like Unix pipes
- **Used everywhere internally** — `range()`, file iteration, FastAPI's `StreamingResponse`

```python
def read_lines(path):
    with open(path) as f:
        for line in f:           # file objects are iterators
            yield line.strip()

def non_empty(lines):
    for line in lines:
        if line:
            yield line

# Composition — no intermediate lists, even for huge files
count = sum(1 for _ in non_empty(read_lines("huge.txt")))
```

### `yield from`
```python
def chained():
    yield from [1, 2, 3]
    yield from range(4, 6)

list(chained())   # [1, 2, 3, 4, 5]
```

---

## 4. Decorators (35 min) — critical for FastAPI

A decorator is just **a function that takes a function and returns a function**.

```python
def log_calls(fn):
    def wrapper(*args, **kwargs):
        print(f"calling {fn.__name__}")
        result = fn(*args, **kwargs)
        print(f"done {fn.__name__}")
        return result
    return wrapper

@log_calls
def add(a, b):
    return a + b

add(2, 3)
# calling add
# done add
# 5
```

`@log_calls` is exactly the same as `add = log_calls(add)`. Sugar.

### Preserving function metadata
```python
from functools import wraps

def log_calls(fn):
    @wraps(fn)    # copies __name__, __doc__, signature
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper
```

**Always use `@wraps`** in decorators you write — otherwise `add.__name__` becomes `"wrapper"` and you lose debugging.

### Parameterized decorator (3 layers)

```python
def retry(times: int):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if attempt == times - 1:
                        raise
        return wrapper
    return decorator

@retry(times=3)
def flaky():
    ...
```

The pattern: outer function takes the *args*, inner function takes the *function*, innermost wraps.

### Class-based decorators (briefly)
```python
class CountCalls:
    def __init__(self, fn):
        self.fn = fn
        self.count = 0
    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.fn(*args, **kwargs)

@CountCalls
def hello(): print("hi")

hello(); hello()
print(hello.count)   # 2
```

> **TS analogy:** very similar to TS class decorators (experimental feature) but used much more widely.

### Why FastAPI uses these
Every `@app.get("/path")` is a decorator that registers the function as a route handler. Every `@field_validator` in Pydantic is one too.

---

## 5. Context managers (20 min)

The `with` statement guarantees cleanup, even on exception.

```python
with open("file.txt") as f:
    data = f.read()
# file is closed here, even if read() raised
```

### Implementing one — class style
```python
class Timer:
    def __enter__(self):
        import time
        self.start = time.time()
        return self                    # what `as` binds to
    def __exit__(self, exc_type, exc_val, tb):
        print(f"took {time.time() - self.start:.2f}s")
        # return True to suppress exception; False/None to propagate

with Timer() as t:
    expensive_thing()
```

### Implementing one — generator style (cleaner)
```python
from contextlib import contextmanager

@contextmanager
def timer():
    import time
    start = time.time()
    try:
        yield
    finally:
        print(f"took {time.time() - start:.2f}s")

with timer():
    expensive_thing()
```

Code **before** `yield` runs on enter; code **after** runs on exit. The `try/finally` ensures exit logic runs even on exception.

### Multiple context managers
```python
with open("in.txt") as inp, open("out.txt", "w") as out:
    out.write(inp.read().upper())
```

> **Where this matters in your interview:** FastAPI's `lifespan` (startup/shutdown logic) uses `@asynccontextmanager`. Database session per request is usually a context manager. LangChain callbacks/tracers use context managers. Know it cold.

---

## 6. Practice (35 min)

### Exercise 1: Build a `@cached` decorator
```python
# Caches the function's return value by args.
# @cached
# def slow(n): ...
# Second call with same n returns instantly.
# Hint: use a dict keyed on args
```

### Exercise 2: Implement Fibonacci as a generator
```python
def fib():
    """Infinite generator: 0, 1, 1, 2, 3, 5, 8, ..."""
    ...

# Test:
from itertools import islice
list(islice(fib(), 10))   # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### Exercise 3: Build a `@timed` context manager (both ways)
```python
# 1. As a class with __enter__/__exit__
# 2. As a function with @contextmanager
# Both should print elapsed time on exit.
```

### Exercise 4: `User` class with validation
```python
# class User with name (str) and age (int via @property setter that rejects <0).
# @classmethod from_dict(cls, d) constructor.
# __repr__ returns User(name='...', age=...)
# Raises UserNotFoundError (your custom exception) on User.find(id) miss.
```

### Exercise 5: Recreate `@lru_cache` lightly
```python
# A decorator factory: @memoize(maxsize=128) that caches up to maxsize entries
# and evicts the oldest when full. Use collections.OrderedDict.
```

---

## End-of-Day-2 self-check

- [ ] Why does `@wraps` matter?
- [ ] When would you use `@classmethod` vs `@staticmethod`?
- [ ] What's the difference between an iterator and a generator?
- [ ] How does a `with` statement guarantee cleanup?
- [ ] What does `super()` do?
- [ ] What's the difference between `raise` and `raise e`?

---

## What you skipped (covered tomorrow)

- Type hints in depth — **Day 3**
- `async`/`await` — **Day 3**
- `dataclass` and Pydantic — **Day 3**
- `asyncio` event loop — **Day 3**
- Tooling: `uv`, `pytest`, `mypy` — **Day 3**
- FastAPI hello world — **Day 3**

Tomorrow you'll see decorators + context managers in action via FastAPI.

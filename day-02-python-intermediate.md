# Day 2 — Python Intermediate (Detailed)

**Time:** 2.5 hours (with stretch material if you finish early)
**Goal:** OOP, exceptions, iterators/generators, decorators, context managers — the building blocks every Python framework uses.
**Scope:** Classes, inheritance, MRO, dunder methods, exceptions, iterator protocol, generators (`yield`, `yield from`), decorators (incl. `functools`), context managers (incl. `contextlib`).
**Out of scope today** (Day 3): type hints in depth, async/await, Pydantic, dataclasses, tooling.

> **All facts verified against** official Python docs (docs.python.org) and PEPs. URLs at the bottom.

---

## Quick reference (interview-day skim)

| Concept | One-line answer |
|---|---|
| **`__new__` vs `__init__`** | `__new__` creates the instance (static method, returns it); `__init__` initializes it. You rarely override `__new__`. |
| **`@classmethod`** | First arg is `cls` (the class). Used for alternate constructors. `User.from_dict(d)`. |
| **`@staticmethod`** | No implicit first arg. Function namespaced under the class. |
| **`@property`** | Method exposed as attribute access (`obj.x`, not `obj.x()`). Add `@x.setter` and `@x.deleter` for write/delete. |
| **MRO** | Method Resolution Order — Python 3 uses **C3 linearization**. Inspect via `Cls.__mro__` or `Cls.mro()`. Guarantees consistent ordering across multiple inheritance. |
| **`super()`** | No-arg form (Python 3): walks the MRO. Calls the next class's method. Don't pass args unless you know what you're doing. |
| **`__slots__`** | Class-level tuple of allowed attribute names. Disables per-instance `__dict__`. Saves memory; restricts dynamic attrs. |
| **Iterable vs iterator** | Iterable has `__iter__()` returning an iterator. Iterator has `__next__()` returning the next value (raises `StopIteration`). All iterators are iterable (they return self). |
| **Generator** | A function with `yield` returns a generator object — an iterator that pauses/resumes. |
| **`yield from x`** (3.3, PEP 380) | Delegates to a sub-iterator. The sub-iterator's return value becomes the `StopIteration.value`. |
| **`gen.send(v)` / `throw(exc)` / `close()`** | Resume sending a value back; inject an exception; trigger `GeneratorExit`. |
| **Decorator** | A callable taking a function and returning a function. `@foo` is sugar for `f = foo(f)`. Always use `@functools.wraps(fn)`. |
| **`functools.wraps`** | Copies `__name__`, `__doc__`, `__module__`, `__qualname__`, `__dict__`, `__wrapped__` to the wrapper. |
| **`functools.lru_cache` / `cache`** | Memoize. `lru_cache(maxsize=N)` is bounded; `cache` (3.9+) is unbounded shortcut. |
| **Context manager** | Object with `__enter__` / `__exit__(exc_type, exc_val, tb)`. Used with `with`. `__exit__` returning `True` suppresses the exception. |
| **`@contextmanager`** | `contextlib` decorator: turn a generator into a context manager. Code before `yield` = enter; code after = exit. Use `try/finally`. |
| **`@asynccontextmanager`** (3.7+) | Async version, for `async with`. |
| **`try / except / else / finally`** | `else` runs only on success (no exception); `finally` always runs. |
| **`raise X from Y`** (PEP 3134) | Chains exceptions — sets `__cause__`. Bare `raise` keeps `__context__`. |
| **Exception groups** (3.11, PEP 654) | `ExceptionGroup` + `except*` to handle multiple exceptions at once. |
| **`abc.ABC` / `@abstractmethod`** | Subclasses must implement abstract methods or instantiation fails. |
| **Never subclass `BaseException`** directly | Subclass `Exception` for normal errors. `BaseException` is parent of `SystemExit`/`KeyboardInterrupt`. |

---

## 1. Classes & OOP (50 min)

### 1.1 Basic class

```python
class User:
    """A user account."""

    # CLASS attribute — shared across all instances
    species = "homo sapiens"

    def __init__(self, name: str, age: int):
        # INSTANCE attributes — per object
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"hi, I'm {self.name}"

    def __repr__(self) -> str:
        # For developers / debug. Goal: unambiguous, eval-able when possible.
        return f"User(name={self.name!r}, age={self.age})"

    def __str__(self) -> str:
        # For humans (print, str()). If absent, falls back to __repr__.
        return f"{self.name} ({self.age})"


u = User("sharath", 25)
print(u)         # sharath (25)         — uses __str__
print(repr(u))   # User(name='sharath', age=25)  — uses __repr__
```

**Convention:** always define `__repr__`. Only define `__str__` when you need a human-readable form different from `__repr__`. The `!r` format spec calls `repr()` on an arg.

> **TS analogy:** `self` ≈ `this`. `__init__` ≈ `constructor`. No JS equivalent for `__repr__`; closest is overriding `Symbol.for("nodejs.util.inspect.custom")` in Node.

### 1.2 `__new__` vs `__init__` — the real construction

`__new__` actually **creates** the instance. `__init__` **initializes** it (the instance already exists).

```python
class Foo:
    def __new__(cls, *args, **kwargs):
        print(f"creating {cls.__name__}")
        instance = super().__new__(cls)
        return instance
    def __init__(self, x):
        print(f"initializing with x={x}")
        self.x = x

Foo(42)
# creating Foo
# initializing with x=42
```

When you'd override `__new__`:
- **Implementing immutable types** that subclass built-ins (`str`, `int`, `tuple`) — you must initialize in `__new__` because `__init__` is too late
- **Singletons** (return the same instance every time)
- **Caching/interning**

For ~99% of code, you never override `__new__`.

### 1.3 `@classmethod` vs `@staticmethod` vs `@property`

```python
class User:
    def __init__(self, name, age):
        self.name = name
        self._age = age          # convention: leading _ = "private-ish"

    @property
    def age(self) -> int:
        """Read as user.age (no parens)."""
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        if value < 0:
            raise ValueError("age cannot be negative")
        self._age = value

    @age.deleter
    def age(self) -> None:
        del self._age

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Alternate constructor. cls is the class — works correctly in subclasses."""
        return cls(data["name"], data["age"])

    @staticmethod
    def is_valid_age(value: int) -> bool:
        """Utility that doesn't touch self or cls."""
        return 0 <= value < 150
```

**Which to use:**
- **`@property`** — computed or validated attribute access
- **`@classmethod`** — alternate constructor; anything needing `cls`
- **`@staticmethod`** — utility logically scoped to the class, but no class state

> **3.11+ note:** chaining `@classmethod` and `@property` (to create class-level properties) was **deprecated in 3.11 and removed in 3.13** — it always had subtle bugs. If you need class-level read-only attributes, use a regular `@classmethod` or a module-level constant.

### 1.4 `__slots__` — memory optimization

By default, every instance gets a `__dict__` (dynamic attribute storage). For many small objects this is wasteful.

```python
class Point:
    __slots__ = ("x", "y")       # only these attrs allowed
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
p.z = 5    # AttributeError: 'Point' object has no attribute 'z'
```

**Benefits:**
- ~40-50% memory savings for small classes (millions of instances)
- Slightly faster attribute access
- Catches typos (`p.X = 1` errors instead of silently creating a new attribute)

**Trade-offs:**
- Can't add new attributes dynamically
- Can't have class-level defaults for `__slots__` attrs
- Multiple inheritance with `__slots__` is finicky
- Subclasses without `__slots__` get a `__dict__` back (defeats the saving)

### 1.5 Dunder (magic) methods — the highlights

| Dunder | Purpose |
|---|---|
| `__init__` | Initialize a new instance |
| `__new__` | Create the instance (rarely overridden) |
| `__repr__` | Debug representation (always define) |
| `__str__` | Human representation (optional) |
| `__eq__`, `__hash__` | Equality + hashability. Override together. |
| `__lt__`, `__gt__`, `__le__`, `__ge__`, `__ne__` | Ordering. Or use `@functools.total_ordering`. |
| `__len__`, `__bool__` | Length and truthiness |
| `__contains__` | `x in obj` |
| `__iter__`, `__next__` | Iteration |
| `__getitem__`, `__setitem__`, `__delitem__` | `obj[k]` access |
| `__call__` | Make instance callable: `obj()` |
| `__enter__`, `__exit__` | Context manager |
| `__add__`, `__mul__`, ... | Arithmetic operators |
| `__getattr__` | Fallback when normal lookup fails (NOT `__getattribute__`) |
| `__setattr__` | Intercept every attribute set |
| `__post_init__` | (For `@dataclass`) — runs after auto-generated `__init__` |

**`__eq__` + `__hash__` rule:** if you override `__eq__`, Python sets `__hash__` to `None` (making your class unhashable). To keep hashability, also override `__hash__`. The contract: `a == b` implies `hash(a) == hash(b)`.

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __eq__(self, other):
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)
    def __hash__(self):
        return hash((self.x, self.y))
```

---

## 2. Inheritance, MRO, ABCs (25 min)

### 2.1 Single inheritance

```python
class Animal:
    def __init__(self, name):
        self.name = name
    def speak(self) -> str:
        return "..."

class Dog(Animal):
    def speak(self) -> str:
        return "woof"

class Puppy(Dog):
    def speak(self) -> str:
        parent = super().speak()
        return f"small {parent}"

Puppy("rex").speak()    # "small woof"
Puppy.__mro__
# (Puppy, Dog, Animal, object)
```

### 2.2 `super()` — the no-arg form

Python 3 lets you write `super()` without arguments. It uses the magic `__class__` cell that the compiler inserts in any method that references `super`. Equivalent to `super(Puppy, self)` here.

```python
class A:
    def hi(self): return "A"

class B(A):
    def hi(self): return "B + " + super().hi()    # "B + A"
```

In `__init__`, **always call `super().__init__()`** when subclassing — otherwise the parent's setup is skipped.

### 2.3 Multiple inheritance + MRO (C3 linearization)

```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass

D.__mro__
# (D, B, C, A, object)
```

Python uses **C3 linearization** — a deterministic algorithm that produces a consistent order respecting:
1. A class precedes its parents
2. Order of bases in the `class D(B, C):` declaration is preserved
3. If a consistent ordering doesn't exist, Python raises `TypeError` at class creation

> **Why care:** in multiple inheritance, `super()` walks the MRO — calling `super().method()` from `D` runs `B`'s method, not `A`'s. Cooperative multiple inheritance ("diamond pattern") relies on this. The official docs reference [Michele Simionato's article](https://docs.python.org/3/howto/mro.html).

### 2.4 Abstract Base Classes (`abc` module)

For enforcing that subclasses must implement specific methods.

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...
    @abstractmethod
    def perimeter(self) -> float: ...

class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return 3.14159 * self.r ** 2
    def perimeter(self): return 2 * 3.14159 * self.r

Shape()      # TypeError — can't instantiate abstract
Circle(5)    # works
```

**Variations:**
- `@abstractmethod` works with `@classmethod`, `@staticmethod`, `@property` — stack them.
- Use ABCs sparingly. Often `typing.Protocol` (Day 3) is better — structural / duck typing.

### 2.5 `__init_subclass__` — hook for subclass creation (3.6, PEP 487)

Called automatically when a subclass is created.

```python
class Plugin:
    registry = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin.registry.append(cls)

class MyPlugin(Plugin): pass
class AnotherPlugin(Plugin): pass

Plugin.registry    # [<class 'MyPlugin'>, <class 'AnotherPlugin'>]
```

Useful for plugin systems, ORM-style auto-registration. Cleaner than metaclasses for the common cases.

---

## 3. Exception handling (20 min)

### 3.1 Basic `try / except / else / finally`

```python
try:
    result = risky()
except ValueError as e:
    log.error(f"bad value: {e}")
    raise                         # re-raise current exception (preserves traceback)
except (KeyError, IndexError) as e:
    return None
else:
    # runs ONLY if no exception was raised — uncommon but useful
    log.info("succeeded")
finally:
    # always runs — for cleanup, even after `return` or unhandled raise
    cleanup()
```

### 3.2 The exception hierarchy

```
BaseException
 ├── SystemExit          ← from sys.exit()
 ├── KeyboardInterrupt   ← Ctrl-C
 ├── GeneratorExit       ← generator.close()
 └── Exception           ← what your code should catch / subclass
      ├── ArithmeticError
      ├── LookupError    (parent of KeyError, IndexError)
      ├── ValueError
      ├── TypeError
      ├── OSError
      ├── RuntimeError
      ├── StopIteration
      └── ...many more
```

**Rule:** **never** subclass `BaseException` directly. Always subclass `Exception` (or a more specific subclass). `BaseException` is the parent of system-exit-y things you usually don't want to swallow.

```python
try:
    risky()
except Exception:        # catches user exceptions, not Ctrl-C/SystemExit
    handle()
```

`except:` (bare) or `except BaseException:` catches everything including Ctrl-C — almost always wrong.

### 3.3 Custom exceptions

```python
class NotFoundError(Exception):
    """Raised when an entity is not found."""

class UserNotFoundError(NotFoundError):
    def __init__(self, user_id: int):
        super().__init__(f"user {user_id} not found")
        self.user_id = user_id

raise UserNotFoundError(42)
```

Conventions:
- Suffix with `Error` (rarely `Exception` or `Warning`)
- Include relevant context as attributes (here `self.user_id`)
- Group related exceptions under a base class for blanket catches

### 3.4 Exception chaining — `raise X from Y` (PEP 3134, 3.0)

```python
try:
    parse(data)
except ValueError as e:
    raise RuntimeError("config invalid") from e
```

This sets `__cause__` on the new exception. Python prints both tracebacks:

```
ValueError: bad data
The above exception was the direct cause of the following exception:
RuntimeError: config invalid
```

**`__cause__` vs `__context__`:**
- `__cause__` — set by explicit `raise X from Y`. Means Y *caused* X.
- `__context__` — set automatically when a new exception is raised inside `except`. Means Y *happened during handling of* X.
- `raise X from None` — suppresses context entirely (cleaner traceback for library wrappers).

### 3.5 `raise` vs `raise e`

Inside `except`:
- **`raise`** — re-raises the current exception, **preserving the original traceback**. Use this.
- **`raise e`** — raises the exception object, but **adds a new traceback frame** at the `raise e` line. Less clean.

### 3.6 Exception groups + `except*` (3.11, PEP 654)

For situations (e.g. concurrent tasks) where multiple exceptions happen at once and you want to handle them granularly.

```python
try:
    raise ExceptionGroup("multiple", [
        ValueError("bad value"),
        TypeError("bad type"),
        ValueError("another bad value"),
    ])
except* ValueError as eg:
    print(f"got {len(eg.exceptions)} ValueErrors")
except* TypeError as eg:
    print(f"got {len(eg.exceptions)} TypeErrors")
```

`except*` extracts matching exceptions from the group; unmatched ones re-raise as a smaller group. Used heavily by `asyncio.TaskGroup` (also 3.11).

For most code: you don't need this. Know it exists.

---

## 4. Iterators & generators (30 min)

### 4.1 The iterator protocol

```python
# Iterable — has __iter__ returning an iterator
# Iterator — has __next__, raises StopIteration when exhausted

# Hand-rolled iterator
class CountUp:
    def __init__(self, end):
        self.end = end
        self.n = 0
    def __iter__(self):
        return self                 # iterators return themselves
    def __next__(self):
        if self.n >= self.end:
            raise StopIteration
        self.n += 1
        return self.n

for x in CountUp(3):
    print(x)                        # 1, 2, 3
```

**Iterable vs iterator:**
- **Iterable** — any object that `__iter__` produces an iterator from. Lists, dicts, sets, strings, files, generators.
- **Iterator** — has `__next__`. Consumable once. Calling `iter()` on an iterator returns the iterator itself.

```python
lst = [1, 2, 3]
it = iter(lst)         # get an iterator from the iterable
next(it)               # 1
next(it)               # 2
next(it)               # 3
next(it)               # StopIteration
```

### 4.2 Generators — easier iterators with `yield`

```python
def count_up(end):
    n = 0
    while n < end:
        n += 1
        yield n

g = count_up(3)
type(g)                # <class 'generator'>
list(g)                # [1, 2, 3]
```

A function with `yield` returns a **generator object** when called. Execution pauses at each `yield` and resumes on the next `next()`.

### 4.3 Why use generators?

- **Lazy** — produce one value at a time, no intermediate storage
- **Composable** — chain like Unix pipes
- **Used everywhere internally** — `range`, file iteration, FastAPI `StreamingResponse`, LangChain `.stream()`

```python
def read_lines(path):
    with open(path) as f:
        for line in f:        # file objects are themselves iterators
            yield line.strip()

def non_empty(lines):
    for line in lines:
        if line:
            yield line

# Composition — no intermediate lists, even for huge files
count = sum(1 for _ in non_empty(read_lines("huge.txt")))
```

### 4.4 `yield from` (3.3, PEP 380)

Delegate iteration to a sub-iterator. The sub's `return` value becomes `StopIteration.value`.

```python
def chained():
    yield from [1, 2, 3]
    yield from range(4, 6)

list(chained())    # [1, 2, 3, 4, 5]
```

Inside the sub-generator, you can `return value` — that value propagates as `StopIteration.value` (used internally by `asyncio` for coroutines pre-async-await).

### 4.5 Generator methods — `send`, `throw`, `close`

These turn generators into a **bidirectional communication channel** (the basis of "coroutines").

```python
def echo():
    while True:
        received = yield                # yield receives a value
        print(f"got {received}")

g = echo()
next(g)              # prime: advance to first yield
g.send("hi")         # got hi
g.send("world")      # got world
g.close()            # raises GeneratorExit inside the generator
```

- **`gen.send(value)`** — resumes the generator; `yield` expression evaluates to `value`. (Plain `next(gen)` is `gen.send(None)`.)
- **`gen.throw(exc)`** — raises `exc` at the current `yield`. The generator can catch it or propagate.
- **`gen.close()`** — raises `GeneratorExit` at the current `yield`, asking the generator to clean up.

You rarely write generators that use these; `asyncio` and frameworks do.

---

## 5. Decorators (40 min)

### 5.1 The mental model

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

`@log_calls` above is **exactly equivalent** to `add = log_calls(add)`. Sugar.

### 5.2 Always use `functools.wraps`

Without it, the wrapped function loses `__name__`, `__doc__`, signature inspection breaks, and stack traces get confusing.

```python
from functools import wraps

def log_calls(fn):
    @wraps(fn)                          # copies fn's metadata to wrapper
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper
```

`functools.wraps` copies: `__module__`, `__name__`, `__qualname__`, `__annotations__`, `__doc__`, `__dict__` (and `__type_params__` since 3.12), and sets `__wrapped__` (so you can recover the original function).

### 5.3 Parameterized decorator — the 3-layer pattern

A decorator that itself takes arguments needs an extra layer of nesting.

```python
def retry(times: int, exceptions=(Exception,)):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            last = None
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last = e
            raise last
        return wrapper
    return decorator

@retry(times=3, exceptions=(ConnectionError,))
def flaky():
    ...
```

Pattern: outer takes the decorator args → middle takes the function → inner is the wrapper.

### 5.4 Class-based decorators

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
print(hello.count)     # 2
```

Useful when you need state across calls (you have it on `self`).

### 5.5 Stacking decorators

```python
@dec_a
@dec_b
def f(): ...
# equivalent to: f = dec_a(dec_b(f))
# decorators apply bottom-up
```

### 5.6 `functools` highlights

```python
from functools import wraps, lru_cache, cache, partial, reduce, total_ordering

# Memoize
@lru_cache(maxsize=128)        # bounded LRU
def fib(n): ...

@cache                          # 3.9+ unbounded shortcut for lru_cache(maxsize=None)
def fib2(n): ...

# Partial application
def add(a, b, c): return a + b + c
add5 = partial(add, 5)          # add5(b, c) == add(5, b, c)

# Reduce
reduce(lambda a, b: a + b, [1, 2, 3, 4])    # 10
# (use sum(), all(), any(), math.prod() when applicable — reduce is last resort)

# Total ordering — auto-fill comparison methods
@total_ordering
class Version:
    def __init__(self, major, minor): self.major, self.minor = major, minor
    def __eq__(self, o): return (self.major, self.minor) == (o.major, o.minor)
    def __lt__(self, o): return (self.major, self.minor) < (o.major, o.minor)
    # __total_ordering fills in __le__, __gt__, __ge__, __ne__
```

### 5.7 Where this matters in your stack
- Every FastAPI `@app.get("/path")` is a decorator that registers a route handler
- Every Pydantic `@field_validator` is a decorator
- `@pytest.fixture`, `@pytest.mark.parametrize` — decorators
- LangChain's `@tool` — decorator

---

## 6. Context managers (25 min)

### 6.1 `with` statement guarantees cleanup

```python
with open("file.txt") as f:
    data = f.read()
# f.close() is called here, even if read() raised
```

Behind the scenes, `with` calls `__enter__` on entry and `__exit__` on exit (always — exception or not).

### 6.2 Class-based context manager

```python
import time

class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self                          # what `as` binds to
    def __exit__(self, exc_type, exc_val, tb):
        self.elapsed = time.perf_counter() - self.start
        # Return True to SUPPRESS the exception; False/None to PROPAGATE
        return False

with Timer() as t:
    expensive_thing()
print(f"took {t.elapsed:.2f}s")
```

`__exit__` signature:
- `exc_type` — exception class, or `None` if normal exit
- `exc_val` — exception instance
- `tb` — traceback object
- **Return `True`** — exception is suppressed (don't propagate)
- **Return `False`/`None`** — exception propagates normally

### 6.3 Generator-based context manager — `@contextmanager`

Usually cleaner.

```python
from contextlib import contextmanager
import time

@contextmanager
def timer():
    start = time.perf_counter()
    try:
        yield                                 # what `as` binds to (or None)
    finally:
        elapsed = time.perf_counter() - start
        print(f"took {elapsed:.2f}s")

with timer():
    expensive_thing()
```

- Code **before** `yield` runs on enter
- Code **after** `yield` runs on exit
- `try/finally` around `yield` ensures the cleanup runs even on exception
- To suppress the exception, catch it inside the `try` and don't re-raise

### 6.4 `contextlib` helpers

```python
from contextlib import contextmanager, asynccontextmanager, closing, suppress, ExitStack, nullcontext

# closing — call .close() on exit (for objects without context manager support)
with closing(urlopen("https://example.com")) as page:
    data = page.read()

# suppress — silently ignore specific exceptions
with suppress(FileNotFoundError):
    os.remove("temp.txt")

# nullcontext — placeholder when you sometimes want a context manager and sometimes don't
ctx = lock if needs_lock else nullcontext()
with ctx:
    work()

# ExitStack — dynamic, variable number of CMs
with ExitStack() as stack:
    files = [stack.enter_context(open(p)) for p in paths]
    # all files closed on exit, even if one open() fails
```

### 6.5 `@asynccontextmanager` (3.7+)

Async version for `async with`.

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    # startup
    yield {"resource": ...}
    # shutdown
```

This is what **FastAPI's `lifespan=`** uses.

### 6.6 Multiple context managers — one `with`

```python
with open("in.txt") as inp, open("out.txt", "w") as out:
    out.write(inp.read().upper())
```

3.10+ allows parenthesized multi-line:

```python
with (
    open("in.txt") as inp,
    open("out.txt", "w") as out,
    Timer() as t,
):
    ...
```

---

## 7. Common gotchas (recap)

1. **Forgetting `super().__init__()`** in subclasses → parent's `__init__` skipped, attributes missing.
2. **Mutating an attribute in `__init__` of a frozen dataclass** → error.
3. **Overriding `__eq__` without `__hash__`** → class becomes unhashable.
4. **Using a generator twice** → second iteration is empty (generators are single-use).
5. **`yield` inside a generator that's already in a `try/finally`** → cleanup may not run if you stop iterating early without closing.
6. **Decorator without `@wraps`** → introspection broken.
7. **Catching `Exception` and swallowing** → hides real bugs. Catch the narrowest type.
8. **Bare `except:`** → also catches `Ctrl-C` and `SystemExit`. Almost always wrong.
9. **Modifying a class while iterating its MRO** — don't.
10. **`__init__` returning a value** → must return `None`. Use `__new__` if you need to return something else.

---

## 8. Practice exercises (45 min — DO THESE)

### Exercise 1: `@cached` decorator
Build a memoizing decorator. Cache results keyed on `args` (assume hashable). No `**kwargs` support needed.

```python
@cached
def slow(n):
    print("computing", n)
    return n * 2

slow(5)   # computing 5; returns 10
slow(5)   # returns 10 (no print — cached)
```

### Exercise 2: Fibonacci generator
```python
def fib():
    """Infinite generator: 0, 1, 1, 2, 3, 5, 8, ..."""

from itertools import islice
list(islice(fib(), 10))    # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### Exercise 3: `@timed` context manager (both styles)
Build one as a class with `__enter__/__exit__`, and one with `@contextmanager`. Both print elapsed time.

### Exercise 4: `User` class with validation
- Properties: `name` (non-empty str), `age` (0-150, set via property)
- `@classmethod from_dict(cls, d)` constructor
- `__repr__` returning `User(name='...', age=...)`
- `__eq__` + `__hash__` based on `(name, age)`
- Custom exception `UserNotFoundError(user_id)` raised by `User.find(id)`

### Exercise 5: Lightweight `lru_cache`
```python
def memoize(maxsize=128): ...
# decorator factory. Cache up to maxsize entries; evict the oldest when full.
# Hint: collections.OrderedDict — move_to_end + popitem(last=False)
```

### Exercise 6: ABC + concrete subclass
```python
from abc import ABC, abstractmethod
# Shape ABC with abstract area() and perimeter().
# Concrete Rectangle(width, height) and Circle(radius).
# Verify you can't instantiate Shape directly.
```

### Exercise 7: Generator pipeline
Build three generators: `read_lines(path)`, `non_empty(lines)`, `lowercase(lines)`. Compose into a single pipeline. Count lowercase non-empty lines in a file using just `sum(1 for _ in pipeline)`.

### Exercise 8: Exception chaining
Write a `load_config(path)` function. If the file is missing, raise a custom `ConfigError("missing")` chained from the original `FileNotFoundError` using `from`. Verify the traceback shows both.

### Exercise 9: Context manager that suppresses
Build `@contextmanager`-based `suppress_errors(*excs)` that swallows any of the given exception types. Hint: a `try/except` around the `yield`, not in a `finally`.

### Exercise 10: Decorator with metadata
Build `@timed(threshold_ms=N)` — logs only if execution took longer than `threshold_ms`. Three-layer decorator. Test that `timed.__wrapped__` recovers the original function (proves you used `@wraps`).

---

## 9. End-of-Day-2 self-check

Answer each in one sentence:

- [ ] Why use `@wraps` in a decorator?
- [ ] When `@classmethod` vs `@staticmethod`?
- [ ] Iterator vs generator — pick differences.
- [ ] How does `with` guarantee cleanup even on exception?
- [ ] `__new__` vs `__init__` — what does each do?
- [ ] What does `super()` (no args) actually do in Python 3?
- [ ] `raise` vs `raise e` — which preserves the traceback?
- [ ] What's `__exit__`'s return value mean if `True` vs `False`?
- [ ] What's the C3 linearization MRO algorithm guarantee?
- [ ] Why never subclass `BaseException` directly?

---

# Interview Question Bank — Day 2 topics

## Section A — Basic (10 questions)

### A1. What's the difference between `__init__` and `__new__`?
`__new__` is a static method that creates and returns the instance; `__init__` initializes that already-created instance. You almost never override `__new__` — only when implementing immutable subclasses, singletons, or caching.

### A2. What does `self` mean?
The conventional name for the first parameter of an instance method — Python passes the instance automatically when you call `obj.method()`. Equivalent to `this` in JS/TS. There's no language-level requirement to call it `self`, but PEP 8 mandates it.

### A3. What's the difference between `@classmethod` and `@staticmethod`?
`@classmethod` receives the class as `cls` (implicit first arg). `@staticmethod` gets no implicit first arg — it's just a function namespaced under the class. Use `@classmethod` for alternate constructors; `@staticmethod` for utilities.

### A4. What does `@property` do?
Turns a method into an attribute access — call `obj.name`, not `obj.name()`. Lets you intercept get/set/delete with `@x.setter` and `@x.deleter`. Useful for computed values, validation, or transparently switching to lazy/cached attributes without breaking the API.

### A5. What's a decorator?
A callable that takes a function and returns a (usually wrapped) function. `@my_decorator` above `def f(): ...` is exactly `f = my_decorator(f)`. Used heavily in FastAPI/Flask routing, caching, logging, access control.

### A6. What's the difference between `try/except/else/finally`?
- `try` — block to monitor
- `except` — handle specific exception types
- `else` — runs **only if** no exception happened in `try`
- `finally` — runs **always**, even on exception or early return

### A7. What's a generator?
A function with `yield` instead of `return`. Calling it returns a generator object — an iterator that pauses at each `yield` and resumes on next `next()`. Useful for lazy evaluation and producing values one at a time.

### A8. What's a context manager?
An object that defines runtime context for the `with` statement — `__enter__` runs on entry, `__exit__` runs on exit (even on exception). Used for resource management: file handles, locks, DB sessions.

### A9. What does `super()` do?
Calls the parent class's method in inheritance. In Python 3, the no-arg form `super()` automatically figures out the class and instance — equivalent to `super(MyClass, self)`. It walks the MRO so works correctly with multiple inheritance.

### A10. What's a lambda?
A single-expression anonymous function. `lambda x, y: x + y` is equivalent to `def _(x, y): return x + y`. Used inline as `key=` / `filter` predicates / map functions. Use `def` for anything multi-line or needing a docstring/annotation.

---

## Section B — Intermediate (10 questions)

### B1. Why always use `@functools.wraps` in a decorator?
Without it, the wrapper loses the decorated function's `__name__`, `__doc__`, `__qualname__`, `__annotations__`, and signature info — breaks introspection, debuggers, doctests, and FastAPI/Pydantic schemas. `@wraps(fn)` copies all this and sets `__wrapped__` for recovery.

### B2. Explain the iterator protocol.
- **Iterable** — has `__iter__()` returning an iterator. Examples: lists, dicts, strings.
- **Iterator** — has `__next__()` returning the next value and raises `StopIteration` when done. All iterators are also iterable (`__iter__` returns self), so they work in `for` loops.

### B3. What's the difference between `raise` and `raise e`?
Inside an `except` block:
- `raise` — re-raises the **current** exception, **preserves traceback**. Standard re-raise.
- `raise e` — raises `e`, **adds a new traceback frame** at the `raise e` line. Same exception, slightly noisier traceback.

Always use bare `raise` to re-raise.

### B4. What's exception chaining? Difference between `__cause__` and `__context__`?
- `raise X from Y` sets `X.__cause__ = Y` ("Y *caused* X"). Shows "*The above exception was the direct cause of the following*."
- `X.__context__` is set automatically when X is raised while handling Y. Shows "*During handling of the above exception, another exception occurred*."
- `raise X from None` clears the context — cleaner traceback for library code that wraps internal exceptions.

### B5. What's MRO and why does it matter?
**Method Resolution Order** — the deterministic order Python searches for a method up the inheritance chain. Python 3 uses **C3 linearization**, which guarantees:
1. A class comes before its parents
2. Order in `class D(B, C)` is preserved
3. The order is consistent across the entire hierarchy

Inspect with `Cls.__mro__`. `super()` walks the MRO.

### B6. Why might overriding `__eq__` without `__hash__` cause problems?
If you override `__eq__`, Python automatically sets `__hash__` to `None`, making the class unhashable (can't be in sets / used as dict keys). The contract is `a == b ⇒ hash(a) == hash(b)`. To keep hashability, also override `__hash__` (typically `return hash((self.x, self.y))`).

### B7. What does `__slots__` do and what are the trade-offs?
A class-level tuple listing the only attributes instances are allowed to have. Removes per-instance `__dict__` (significant memory savings for many objects), slightly faster attribute access, catches typos.

Trade-offs: can't dynamically add attributes; can't have class-level defaults; multiple inheritance with `__slots__` is finicky; subclasses without `__slots__` regain `__dict__`.

### B8. What does `yield from` do?
`yield from iterable` delegates to a sub-iterator — yields all of its values, and the sub-iterator's `return value` becomes the outer generator's `StopIteration.value`. Added in 3.3 (PEP 380), originally to support coroutine composition before `async`/`await`.

### B9. Why prefer a context manager over a try/finally?
A context manager:
- Encapsulates the setup+cleanup pair, reusable
- Reads top-down (`with`) instead of "find the finally clause"
- Composable (`@contextmanager`, `ExitStack` for dynamic counts)
- Standard in the ecosystem — file handles, locks, sessions, transactions

You'd still use raw `try/finally` for one-off cleanup that doesn't merit a dedicated CM.

### B10. What's the difference between `@contextmanager` and a class-based context manager?
`@contextmanager` (from `contextlib`) turns a generator into a CM:
- Code before `yield` = `__enter__` body
- The yielded value = what `as` binds to
- Code after `yield` (in a `finally` block) = `__exit__` body

Pros: less boilerplate. Cons: can't easily handle exception suppression (must `try/except` inside).

Class-based gives explicit control over `__exit__`'s return value to suppress exceptions.

---

## Section C — Advanced (10 questions)

### C1. What does the no-arg `super()` magic actually do?
The compiler inserts an implicit `__class__` cell variable into any method that references `super()`. At runtime, `super()` reads `__class__` and `self` (the first arg) from the calling frame to figure out which class and instance to use. Equivalent to writing `super(__class__, self)` but the compiler does it for you.

Reference: [super() docs](https://docs.python.org/3/library/functions.html#super).

### C2. How does C3 linearization work conceptually?
Given a class C with parents `P1, P2, ...`, the MRO is computed as:
```
L[C] = C + merge(L[P1], L[P2], ..., [P1, P2, ...])
```
where `merge` repeatedly takes the head of the first list whose head doesn't appear in the tail of any other list. If no valid head exists, Python raises `TypeError` — the inheritance graph is inconsistent.

This guarantees: (1) parents come after children, (2) declaration order is preserved, (3) the result is consistent across the whole graph (monotonic).

### C3. What happens if you `yield` inside a `try/finally` and the caller never exhausts the generator?
The `finally` won't run until the generator is **garbage-collected** (or you explicitly `gen.close()`). If your cleanup is important (closing a file, releasing a lock), don't rely on GC. Either:
- Use a `with` statement inside the generator instead
- Call `gen.close()` explicitly
- Wrap the generator usage in a context manager

### C4. How are coroutines (pre-`async`) implemented via generators?
Before `async`/`await` (3.5+), coroutines were generators that `yield`ed futures. The event loop drove them by `.send(result)` for each yield. `yield from another_gen` was the way to compose. `@asyncio.coroutine` made the pattern explicit. Today, `async def` and `await` compile down to similar machinery but with first-class language support.

### C5. What's a descriptor? How does `@property` work?
A descriptor is any object implementing `__get__`, `__set__`, or `__delete__`. When you access `obj.x`, Python checks the class dict for `x` — if it's a descriptor, Python calls `__get__(obj, type)` instead of returning the descriptor itself.

`@property` is essentially a descriptor class with `__get__` calling your getter. `@classmethod` and `@staticmethod` are also implemented as descriptors.

### C6. What's the difference between `@abstractmethod` and `typing.Protocol`?
- **`@abstractmethod`** (with `abc.ABC`) — nominal subtyping. You must explicitly subclass the ABC AND implement the methods, or instantiation raises.
- **`typing.Protocol`** — structural subtyping. Any class with the right methods is considered to "implement" the protocol, even without inheriting it. Like TS interfaces / Go interfaces. Better fit for Python's duck typing.

Use Protocols for type-checking; use ABCs when you want runtime enforcement.

### C7. What's `__init_subclass__` and when would you use it?
A class method (no `@classmethod` needed) called automatically when a subclass is created. Added in 3.6 (PEP 487).

```python
class Plugin:
    registry = []
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin.registry.append(cls)
```

Replaces most use-cases of metaclasses with something readable. Used for: plugin registries, validation of subclass structure, ORM-style auto-registration.

### C8. What's an exception group? When was it added?
**`ExceptionGroup`** (3.11, PEP 654) wraps multiple unrelated exceptions raised together (typical in concurrent code with `asyncio.TaskGroup`). The new `except*` syntax extracts matching exceptions from the group while leaving the rest re-raised in a smaller group.

```python
try:
    raise ExceptionGroup("multi", [ValueError(1), TypeError(2)])
except* ValueError as eg:
    ...
except* TypeError as eg:
    ...
```

### C9. How does `functools.lru_cache` interact with mutable arguments?
`lru_cache` uses `hash(args)` as the cache key — arguments **must be hashable** (immutable). Calling a `lru_cache`'d function with a `list` or `dict` argument raises `TypeError: unhashable type`. Workaround: convert to `tuple` or `frozenset` first, or use a different memoization strategy.

Also, `lru_cache` doesn't deep-copy results — if the cached return value is mutable and the caller modifies it, subsequent callers see the modification.

### C10. When do `__cause__` and `__context__` matter in production debugging?
They're how you trace "what really happened" when one exception wraps another. Tools like Sentry display both chains. If a library does `raise BadRequest from internal_exc`, you see the user-friendly `BadRequest` plus the internal cause. If you only see `__context__` (the auto-set chain), the wrap was accidental — usually you want explicit `from` (or `from None` to hide noise). Reading tracebacks well is a senior skill — being able to articulate the difference signals seniority.

---

## 10. References — verified May 2026

### Official Python docs
- **Classes:** https://docs.python.org/3/tutorial/classes.html
- **Data model (dunders):** https://docs.python.org/3/reference/datamodel.html
- **Built-in exceptions:** https://docs.python.org/3/library/exceptions.html
- **`abc` module:** https://docs.python.org/3/library/abc.html
- **`functools`:** https://docs.python.org/3/library/functools.html
- **`contextlib`:** https://docs.python.org/3/library/contextlib.html
- **`itertools`:** https://docs.python.org/3/library/itertools.html
- **MRO HOWTO (Simionato):** https://docs.python.org/3/howto/mro.html
- **`super()` reference:** https://docs.python.org/3/library/functions.html#super

### PEPs cited
- **PEP 318** — Function decorators
- **PEP 343** — `with` statement
- **PEP 380** — `yield from` (3.3)
- **PEP 3134** — Exception chaining `raise ... from ...` (3.0)
- **PEP 442** — Safe object finalization
- **PEP 487** — `__init_subclass__` (3.6)
- **PEP 654** — Exception groups + `except*` (3.11)

---

## What you skipped (Day 3)

- Type hints in depth (`typing`, generics, `Protocol`, `TypedDict`) → **Day 3**
- `async`/`await`, asyncio, the event loop → **Day 3**
- Dataclasses (`@dataclass`, `field`, `__post_init__`) → **Day 3**
- Pydantic v2 models, validators, serialization → **Day 3**
- `pytest`, `mypy`, `ruff`, `uv` workflows → **Day 3**
- FastAPI hello world → **Day 3**

Tomorrow's file: [day-03-python-advanced-fastapi-intro.md](day-03-python-advanced-fastapi-intro.md).

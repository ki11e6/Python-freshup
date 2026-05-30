# Modules, Packages & the Import System — Notes

This folder is a mini-project showing **how Python code is organized into modules and
packages**.

```
06_chai_business/
├── main.py                 # entry point
├── recipes/                # a PACKAGE (has __init__.py)
│   ├── __init__.py         # marks the dir as a package; can re-export
│   └── flavors.py          # a MODULE with functions
└── utils/
    └── discounts.py
```

## 1. Module vs Package

- **Module** = a single `.py` file (`flavors.py`). Importing it runs it once and gives you a
  namespace object.
- **Package** = a directory of modules. Traditionally marked by an `__init__.py`
  (`recipes/__init__.py`). Since 3.3, dirs without `__init__.py` can be **namespace packages**,
  but an explicit `__init__.py` is still the norm for regular packages (note: `utils/` here
  lacks one — a real-world bug if you try `from utils.discounts import ...`).

## 2. Import styles (from `main.py`)

```python
import recipes.flavors
recipes.flavors.ginger_chai()              # fully-qualified

from recipes.flavors import ginger_chai, elachai_chai
ginger_chai()                               # direct name

from recipes.flavors import ginger_chai as gc   # alias
import recipes.flavors as flavors               # module alias
```

- `import x` → binds the module name; access members via `x.member`.
- `from x import y` → binds `y` directly into your namespace.
- **Avoid `from x import *`** — pollutes the namespace, hides origins, and only exports names
  listed in `__all__` (or all non-underscore names).

## 3. What `__init__.py` does

- Marks a directory as a (regular) package.
- Runs **once** when the package is first imported — good for package-level setup and
  re-exporting a clean public API:
  ```python
  # recipes/__init__.py
  from .flavors import ginger_chai, elachai_chai   # now: from recipes import ginger_chai
  __all__ = ["ginger_chai", "elachai_chai"]
  ```
- An empty `__init__.py` (as here) is valid — just marks the package.

## 4. How import resolution works

1. Check `sys.modules` cache — **modules are imported only once per process** (re-import is a
   cache hit; that's why top-level module code runs a single time).
2. Search `sys.path`: the script's dir / CWD, then `PYTHONPATH`, then site-packages.
3. Compile to bytecode (`__pycache__/*.pyc`) and execute the module body to build its namespace.

## 5. Absolute vs relative imports

```python
from recipes.flavors import ginger_chai     # absolute (preferred)
from .flavors import ginger_chai            # relative (within a package)
from ..utils.discounts import apply         # parent-relative
```

Absolute imports are clearer and the default recommendation. Relative imports (`.`/`..`) only
work **inside a package** and fail if you run the file as a top-level script.

## 6. `if __name__ == "__main__":`

```python
def main(): ...
if __name__ == "__main__":
    main()
```

When a file is **run directly**, its `__name__` is `"__main__"`; when **imported**, it's the
module name. This guard lets a file act as both a runnable script and an importable module
without executing the script logic on import. (The example `main.py` would normally call its
entry logic under this guard.)

## 7. Running it correctly

From the `06_chai_business/` dir, run as a module so package imports resolve:
```bash
python -m main            # or: python main.py from inside the dir
```
Running a file deep inside a package directly often breaks relative imports — prefer
`python -m package.module` from the project root.

## 8. Common pitfalls (interview gold)

- **Circular imports**: module A imports B which imports A → `ImportError`/partially-initialized
  module. Fix by restructuring, importing inside a function (deferred import), or moving shared
  code to a third module.
- **Missing `__init__.py`** (like `utils/` here): `from utils.discounts import x` may fail
  depending on how/where you run it.
- **Shadowing stdlib**: naming your file `random.py` / `tokenizers.py` shadows the real
  package — surprising import errors.
- **Module-level side effects**: heavy work at import time runs on every import path; keep it
  behind `main()` / lazy.

🤖 **Gen AI angle:** real LLM apps are packages — `app/{chains,prompts,tools,clients}/`. Lazy
imports matter when a heavy dep (`torch`, `transformers`) shouldn't load until needed (cold
start / serverless). Keep API keys/config out of import-time side effects.

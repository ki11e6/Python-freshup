# Modules, Packages & Imports — Interview Questions

### 🟢 Q1. Module vs package?
**A.** A module is a single `.py` file; a package is a directory of modules (traditionally
containing `__init__.py`). Packages can nest to form a hierarchy (`recipes.flavors`).

### 🟢 Q2. What does `__init__.py` do?
**A.** Marks a directory as a regular package and runs once on first import. Commonly used to
re-export a clean public API (`from .flavors import ginger_chai`) and define `__all__`. Can
be empty.

### 🟡 Q3. `import x` vs `from x import y` vs `from x import *`?
**A.** `import x` binds the module (access via `x.y`). `from x import y` binds `y` directly.
`from x import *` dumps names into your namespace — avoid it: it obscures origins and risks
collisions; it only imports names in `__all__` (or non-underscore names).

### 🟡 Q4. Why does a module's top-level code run only once even if imported many times?
**A.** After first import, the module object is cached in `sys.modules`; subsequent imports
return the cached object without re-executing the body. This is why import-time side effects
fire once per process.

### 🔴 Q5. What's a circular import and how do you fix it?
**A.** Module A imports B which (directly or transitively) imports A. During the partial
initialization, a needed name may not exist yet → `ImportError`/`AttributeError`. Fixes:
restructure to break the cycle, move shared code into a third module, or defer the import
inside the function that needs it.

### 🟡 Q6. Absolute vs relative imports?
**A.** Absolute: `from recipes.flavors import ginger_chai` — full path from the project root,
clearest and preferred. Relative: `from .flavors import ginger_chai` (same package), `..` for
parent — only valid inside a package and break when the file is run as a top-level script.

### 🔴 Q7. Explain `if __name__ == "__main__":`.
**A.** `__name__` is `"__main__"` when a file is executed directly and the module's name when
imported. The guard runs script logic only on direct execution, so the file is safely
importable (no side effects) and runnable.

### 🟡 Q8. How does Python find a module to import?
**A.** It checks `sys.modules` (cache), then searches `sys.path` (script dir/CWD, then
`PYTHONPATH`, then installed site-packages), compiles to bytecode in `__pycache__`, and
executes the module body to build its namespace.

### 🟡 Q9. The `utils/` folder here has no `__init__.py`. Is that a problem?
**A.** Potentially. Without `__init__.py` it's at best a namespace package; `from
utils.discounts import ...` may fail depending on where you run from and how `sys.path` is
set. For a regular package, add an `__init__.py`.

### 🔴 Q10. Why might naming a file `tokenizers.py` or `random.py` break your imports?
**A.** It **shadows** the stdlib/third-party module of the same name on `sys.path`, so
`import random` (or a transitive import) picks up your file instead — causing confusing
`ImportError`s or missing attributes. Don't name modules after existing packages.

### 🔴 Q11. (Gen AI) Why use lazy/deferred imports for heavy ML deps?
**A.** Importing `torch`/`transformers` is slow and memory-heavy. In a CLI, web handler, or
serverless function, importing them at module top-level inflates cold-start time even when
the code path doesn't need them. Import inside the function that actually uses the model so
the cost is paid only on demand.

### 🟡 Q12. How would you structure a production Gen AI app as packages?
**A.** Something like `app/{clients, prompts, chains, tools, schemas, config}/` each a
package with `__init__.py` exposing a small public API, a thin `main.py`/`api.py` entry
point under `if __name__ == "__main__":`, config/secrets loaded lazily (not at import time),
and absolute imports throughout.

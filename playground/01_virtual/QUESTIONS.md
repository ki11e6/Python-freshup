# Virtual Environments & Packaging — Interview Questions

### 🟢 Q1. What problem do virtual environments solve?

**A.** Per-project dependency isolation. Each venv has its own `site-packages`, so projects
can pin conflicting versions of the same package without affecting each other or the system
Python. Kills "works on my machine" issues.

### 🟢 Q2. How do you create and activate one?

**A.** `python -m venv .venv`, then `source .venv/bin/activate` (Linux/macOS) or
`.venv\Scripts\activate` (Windows). `deactivate` to exit. Activation just edits `PATH`/env
vars to point at the venv interpreter.

### 🟡 Q3. `==` vs `>=` in requirements.txt?

**A.** `==` pins an exact version → reproducible (use for deployable apps). `>=`/`~=` allow
ranges → flexible (use for libraries you publish, to avoid over-constraining consumers).

### 🟡 Q4. What's wrong with `pip freeze > requirements.txt` as your only manifest?

**A.** It flattens direct + transitive dependencies into one undifferentiated list, so you
can't tell what you actually asked for vs what got pulled in. Maintenance and upgrades get
painful. Better: declare direct deps separately (`requirements.in` / `pyproject.toml`) and
generate a locked file via `pip-compile`, poetry, or uv.

### 🟡 Q5. Should the `.venv/` folder be committed to git?

**A.** No. It's large, platform-specific, and not relocatable. Git-ignore it and commit the
manifest/lockfile so anyone can recreate the env.

### 🟡 Q6. `pip install x` vs `python -m pip install x`?

**A.** `python -m pip` runs pip from the *currently active* interpreter, guaranteeing the
package lands in that Python's environment. Bare `pip` may resolve to a different pip on
`PATH`. The `-m` form is the safe habit.

### 🔴 Q7. (Gen AI) Why is pinning extra critical for ML/LLM projects?

**A.** Deep-learning stacks have tight ABI/version coupling: a `torch` wheel is built for a
specific CUDA version, `transformers` expects compatible `torch`/`tokenizers`/`numpy`, and
mismatches cause silent numerical differences or import/runtime failures. You must pin exact
versions and capture the CUDA/driver assumptions (often via Docker or conda) to reproduce
training/inference behavior.

### 🔴 Q8. What is an editable install and when do you use it?

**A.** `pip install -e .` installs your package via a link to the source tree, so code edits
are picked up without reinstalling. Used while developing a library/package locally,
especially in a monorepo or when iterating on a shared module.

### 🟡 Q9. What is `pyproject.toml` and why did it replace `setup.py`?

**A.** A standardized (PEP 518/621) declarative file for build-system requirements and
project metadata. It decouples building from executing arbitrary `setup.py` code, is
tool-agnostic (poetry, hatch, setuptools, uv all read it), and is now the recommended
packaging entry point.

### 🔴 Q10. How would you make an ML experiment fully reproducible?

**A.** Pin Python + all deps in a lockfile (with hashes), containerize system deps (CUDA,
libs) in a Dockerfile, set random seeds across Python/NumPy/framework, version data and
model artifacts (DVC/object store, git-ignored from the repo), and record hardware. Note the
caveat that GPU floating-point reduction order can still prevent bit-exact reproducibility.

### 🟢 Q11. Name some alternatives to `venv` + `pip`

**A.** `poetry`, `pipenv`, `pip-tools`, `uv` (fast Rust-based), and `conda`/`mamba` (which
also manage non-Python binaries — popular in data/ML for CUDA & native libs).

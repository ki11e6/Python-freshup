# Virtual Environments & Packaging — Notes

## 1. Why virtual environments exist

A venv is an **isolated Python installation** (its own `site-packages`) so each project pins
its own dependency versions without polluting the system Python or other projects. Solves
"works on my machine" / dependency-hell: project A needs `requests==2.33`, project B needs
`requests==2.20`.

```bash
python -m venv .venv          # create
source .venv/bin/activate     # activate (Linux/macOS)
.venv\Scripts\activate        # activate (Windows)
deactivate                    # exit
```

Activation just prepends `.venv/bin` to `PATH` and sets `VIRTUAL_ENV`. The venv is **not**
relocatable and should be **git-ignored** — you commit the *manifest*, not the packages.

## 2. requirements.txt and pinning

`01_virtual/requirements.txt`:
```
Flask==3.1.3
requests==2.33.1
```

- `==` **pins exact** versions → reproducible builds. Use for apps/deployments.
- `>=`, `~=` (compatible release), `<` → flexible ranges. Use for libraries.
- Install: `pip install -r requirements.txt`. Freeze current env: `pip freeze > requirements.txt`.

**Pitfall:** `pip freeze` dumps the *entire* transitive tree, mixing your direct deps with
their dependencies — hard to maintain. Better: keep direct deps in `requirements.in`, compile
the locked set with `pip-compile` (pip-tools), or use a lockfile-based tool.

🤖 **Gen AI angle:** ML stacks are pinning-sensitive — `torch`, `transformers`, CUDA, and
`numpy` must be version-compatible (e.g. a torch build is tied to a CUDA version). Always
pin exact versions and record the CUDA/driver assumptions.

## 3. Modern tooling landscape (know the names)

| Tool | What it is |
|------|-----------|
| `venv` + `pip` | Built-in baseline; what most interviews assume |
| `pip-tools` | `pip-compile` produces a fully-pinned lockfile from `.in` files |
| `pipenv` | Pipfile + Pipfile.lock, combines venv + dependency mgmt |
| `poetry` | `pyproject.toml` + `poetry.lock`, build + publish + deps |
| `uv` | Rust-based, very fast pip/venv replacement; increasingly the default |
| `conda`/`mamba` | Handles non-Python binaries (CUDA, MKL) — common in ML/data |

`pyproject.toml` (PEP 518/621) is the modern standard for declaring build system and
project metadata, replacing `setup.py`/`setup.cfg` for most cases.

## 4. Reproducibility checklist (ML project)

1. Pin Python version (`.python-version` / `pyproject`).
2. Pin all deps with a **lockfile** (hashes ideally).
3. Record system deps (CUDA, system libs) — often a `Dockerfile`.
4. Set seeds, but know GPU float reductions still aren't bit-exact.
5. `.venv/` and model weights → `.gitignore`; large artifacts → DVC / object storage.

## 5. Common interview gotchas

- `pip install X` vs `python -m pip install X` — the latter guarantees you hit the pip tied
  to the *active* interpreter (avoids installing into the wrong Python).
- Activating the venv vs just calling `.venv/bin/python` directly (both work; the latter is
  handy in scripts/CI and needs no activation).
- Editable installs: `pip install -e .` symlinks your package so code edits take effect
  without reinstalling — essential when developing a library.

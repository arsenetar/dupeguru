# Building from Source & Testing

This guide explains how to set up your development environment, build native C/Rust modules, run the application, and execute unit tests for **de-dup**.

---

## Environment Setup

### 1. Create Virtual Environment with uv (Python 3.12+)
```bash
# Recommended with uv (e.g. Python 3.14.7):
uv venv --python 3.14.7 env
source env/bin/activate
uv pip install -e .[dev]

# Or standard Makefile build:
make
```

### Platform-Specific Guides
* **[macOS / OS X Build Guide](../build/macos.md)**: Details for macOS (Apple Silicon & Intel), Xcode setup, and native `.app` packaging.

---

## Makefile Targets

| Target | Command | Description |
| :--- | :--- | :--- |
| `make` | `make all` | Builds all components (Rust engine, C modules, virtualenv). |
| `make rust` | `cd rust_engine && cargo build --release` | Compiles the Rust engine library (`core/dupeguru_rust.so`). |
| `make run` | `./env/bin/python run.py` | Launches the native desktop application (`pywebview` shell). |
| `make desktop` | `./env/bin/python -u run_desktop.py` | Launches the native desktop application (`pywebview` shell). |
| `make web` | `./env/bin/python -u run_web.py` | Launches the standalone HTML Web Console server. |
| `make test` | `./env/bin/pytest` | Runs the 560+ automated unit tests. |

---

## Running Automated Tests

Run the test suite with `pytest`:

```bash
VIRTUAL_ENV=env ./env/bin/pytest
```

To run a specific test module:
```bash
VIRTUAL_ENV=env ./env/bin/pytest core/tests/fs_test.py
```

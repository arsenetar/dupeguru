# Building from Source & Testing

This guide explains how to set up your development environment, build native C/Rust modules, run the application, and execute unit tests for **de-dup**.

---

## Environment Setup

### 1. Create Virtual Environment
```bash
python3 -m venv --system-site-packages ./env
source ./env/bin/activate
pip install -r requirements.txt -r requirements-extra.txt
```

---

## Makefile Targets

| Target | Command | Description |
| :--- | :--- | :--- |
| `make` | `make all` | Builds all components (Rust engine, C modules, virtualenv). |
| `make rust` | `cd rust_engine && cargo build --release` | Compiles the Rust engine library (`core/dupeguru_rust.so`). |
| `make run` | `./env/bin/python run.py` | Launches the PyQt5 desktop GUI application. |
| `make web` | `./env/bin/python -u run_web.py` | Launches the HTML Web Console server. |
| `make test` | `./env/bin/pytest` | Runs the 520+ automated unit tests. |

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

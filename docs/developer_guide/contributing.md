# Contributing Standards & Guidelines

We welcome contributions to **de-dup**! Follow these guidelines to ensure code quality, test coverage, and formatting consistency.

---

## Code Formatting & Style

This repository enforces strict code formatting standards using `black`, `flake8`, and `pre-commit`.

### Pre-commit Hooks
Run pre-commit checks before submitting code:

```bash
PATH="./env/bin:$PATH" pre-commit run --all-files
```

* **Python Formatting**: `black` with 120-character line limit.
* **Linting**: `flake8` compliance.
* **Rust Formatting**: `cargo fmt` inside `rust_engine/`.

---

## Commit Guidelines

* Use clean, imperative commit messages prefixed with standard tags:
  - `feat`: New feature or user-facing capability.
  - `fix`: Bug fix.
  - `perf`: Performance optimization.
  - `docs`: Documentation updates.
  - `refactor`: Structural refactoring without behavior change.

---

## Performance & Robustness Guidelines

1. **Cache Database Resetting**:
   - For Redis/Valkey cache resetting, invoke `FLUSHDB` / `FLUSHDB ASYNC` directly instead of iterating keys via `SCAN` + `DEL`.
   - For resetting large local SQLite cache files, close the connection, unlink the file on disk (`os.remove`), and reconnect to achieve sub-20ms reset times and instant disk space reclamation.

2. **Linux Non-UTF-8 Filename Safety**:
   - Always sanitize string file paths containing potential surrogate escapes (`\udc00`–`\udfff`) before passing them to PyO3 Rust bindings or serializing to JSON.
   - Use `s.encode("utf-8", errors="surrogateescape").decode("utf-8", errors="replace")` to prevent `UnicodeEncodeError` crashes.

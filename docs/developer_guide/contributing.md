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

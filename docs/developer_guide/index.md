# Developer Guide

Welcome to the **de-dup Developer Guide**. This documentation provides in-depth architectural technical references for developers looking to inspect, maintain, or extend the codebase.

---

## Guide Topics

* **[System Architecture](architecture.md)**
  Overview of the Model-View-Presenter (MVP) pattern, Broadcaster pub-sub system, and Python-Rust architecture.
* **[Rust Engine Pipeline](rust_engine.md)**
  Deep dive into `rust_engine/`, PyO3 native bindings, Rayon parallel crawler (`collect_files_parallel`), and SIMD hasher (`hash_files_parallel`).
* **[Component Catalog](components.md)**
  Walkthrough of `core/`, `hscommon/`, `web/`, `run_desktop.py`, and native C/Rust extensions.
* **[Data Flow & Lifecycles](data_flow.md)**
  Step-by-step lifecycles of directory discovery, size-batch hashing, duplicate matching, and result window rendering.
* **[Building from Source](building.md)**
  Instructions for compiling C and Rust extensions, environment setup, and Makefile targets.
* **[Contributing Standards](contributing.md)**
  Code formatting guidelines (`black`, `flake8`), pre-commit hooks, and writing `pytest` unit tests.

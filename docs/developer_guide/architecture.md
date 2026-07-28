# System Architecture & Design Patterns

**de-dup** enforces a clean separation of concerns using a **Model-View-Presenter (MVP)** architectural pattern, augmented by a custom **Broadcaster** pub-sub message system and a native **Rust Engine** interface layer.

---

## Architectural Diagram

```mermaid
graph TD
    subgraph Frontend Interfaces
        QtUI[PyQt5 Desktop UI]
        WebConsole[HTML Web Console]
        RESTServer[REST HTTP Server]
    end

    subgraph Presenter Layer
        Adapter[WebViewAdapter / Qt Presenter]
        Broadcaster[hscommon Broadcaster]
    end

    subgraph Business Logic Core
        App[core/app.py - DupeGuru Core]
        Scanner[core/scanner.py - Matching Engine]
        DirTree[core/directories.py - Directory Model]
    end

    subgraph Native Engine & Database
        PyO3[PyO3 Bridge]
        RustEngine[Rust Parallel Rayon Engine]
        CacheDB[(SQLite WAL / Valkey Redis)]
    end

    QtUI --> Adapter
    WebConsole --> RESTServer
    RESTServer --> Adapter
    Adapter --> Broadcaster
    Broadcaster --> App
    App --> Scanner
    App --> DirTree
    DirTree --> PyO3
    PyO3 --> RustEngine
    RustEngine --> CacheDB
```

---

## Key Design Principles

1. **Double Decoupling**: Frontend UI implementations (PyQt5, Web UI, CLI) never interact directly with low-level data structures. They communicate through `hscommon.gui` presenter contracts and `Broadcaster` notifications.
2. **Native Extension Layer (PyO3)**: Heavy CPU-bound and disk-bound tasks (file crawling, checksum calculation, database persistence) delegate to compiled Rust shared libraries (`dupeguru_rust.so`).
3. **Headless Execution Compatibility**: The core application logic (`core/app.py`) can run in headless server environments without requiring X11, Wayland, or Qt display servers.

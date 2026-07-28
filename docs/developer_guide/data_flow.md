# Data Flow & Lifecycle Analysis

This document describes the runtime execution lifecycles and data flow pipelines within **de-dup**.

---

## 1. Application Boot Lifecycle

```mermaid
sequenceDiagram
    participant User
    participant WebServer as web/server.py
    participant App as core/app.py
    participant FilesDB as core/fs.py
    participant RustEngine as dupeguru_rust

    User->>WebServer: run_web.py --port 8080
    WebServer->>App: Instantiate DupeGuru(web_view)
    App->>FilesDB: fs.filesdb.connect(hash_cache_file)
    FilesDB->>RustEngine: RustFilesDB::new(path_str)
    RustEngine-->>FilesDB: Return Rust SQLite / Valkey handle
    WebServer-->>User: HTTP Server ready at http://localhost:8080
```

---

## 2. Scan Execution Pipeline

```mermaid
sequenceDiagram
    participant User
    participant REST as /api/scan
    participant Job as ThreadedJobPerformer
    participant Dir as core/directories.py
    participant Rust as dupeguru_rust
    participant Scanner as core/scanner.py

    User->>REST: POST /api/scan {clear_cache: True}
    REST->>Job: Spawn async scan thread
    Job->>Dir: _get_files(selected_dirs)
    Dir->>Rust: collect_files_parallel(roots)
    Rust-->>Dir: Return Vec<(path, size, mtime)>
    Dir->>Scanner: Pass scannable File objects
    Scanner->>Rust: hash_files_parallel(candidates)
    Rust-->>Scanner: Return MD5 hashes
    Scanner-->>REST: Duplicate groups created
```

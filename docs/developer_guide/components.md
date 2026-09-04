# Component Catalog

This document details the primary directory structure and component packages of **de-dup**.

---

## Source Tree Overview

* **`core/`**: Central application models, scanning pipelines, database engines, and services.
  - `core/domain/`: Domain dataclasses and DTOs (`FileDTO`, `DuplicateGroupDTO`, `ScanTaskDTO`, `TaskStatus`).
  - `core/pipeline/`: Single-responsibility scan stages (`FileDiscovery`, `ContentHasher`, `DuplicateMatcher`, `CrossDBMatcher`).
  - `core/storage/`: SQLite database engines (`DBEngine`, `TaskRepository`, `DBVerifier`).
  - `core/service/`: High-level orchestration services (`TaskRunner`, `FileDeletionService`).
  - `core/paths.py`: Platform-independent pure Python path resolution (`get_appdata_path`, `get_cache_path`).
  - `core/pe/`: Picture Edition C-extension pixel-block matcher.
* **`rust_engine/`**: Rust native module source (`dupeguru_rust`).
* **`web/`**: REST HTTP server and glassmorphic Web UI client assets.
  - `web/server.py`: Multi-threaded HTTP server (`ThreadedHTTPServer`), REST endpoints (`/api/status`, `/api/scan`, `/api/directories`), and streaming progress state.
  - `web/static/`: Static CSS styling, JavaScript single-page application (`app.js`), icons, and HTML template.
* **`run_desktop.py`**: Native desktop shell utilizing `pywebview` with `DesktopBridgeAPI` exposing OS file dialogs.
* **`hscommon/`**: Reusable cross-platform abstractions, job progress reporting (`Job`, `ThreadedJobPerformer`), desktop utilities, and localization helpers.

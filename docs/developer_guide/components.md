# Component Catalog

This document details the primary directory structure and component packages of **de-dup**.

---

## Source Tree Overview

* **`core/`**: Central application models, scanner matching engines, and database abstraction wrappers.
  - `core/app.py`: Main `DupeGuru` application state manager.
  - `core/fs.py`: File system abstraction layer, `FilesDB` database wrapper, and cache engine dispatcher.
  - `core/directories.py`: Directory tree traversal, state tracking (Reference, Excluded, Normal), and file collection.
  - `core/scanner.py`: Candidate size-grouping, block hashing, match filtering, and result group generation.
  - `core/pe/`: Picture Edition C-extension pixel-block matcher.
* **`rust_engine/`**: Rust native module source (`dupeguru_rust`).
* **`web/`**: REST HTTP server and glassmorphic Web UI client assets.
  - `web/server.py`: Multi-threaded HTTP server (`ThreadedHTTPServer`), REST endpoints (`/api/status`, `/api/scan`, `/api/directories`), and streaming progress state.
  - `web/static/`: Static CSS styling, JavaScript single-page application (`app.js`), icons, and HTML template.
* **`qt/`**: PyQt5 desktop frontend layouts and dialog presenters.
* **`hscommon/`**: Reusable GUI object definitions (`TextField`, `ProgressWindow`), job progress reporting (`Job`, `ThreadedJobPerformer`), desktop utilities, and localization helpers.

# de-dup

> [!NOTE]
> **de-dup** is a high-performance cross-platform duplicate file scanner. It was forked from [dupeGuru](https://github.com/arsenetar/dupeguru) and is maintained at [https://github.com/TinLe/de-dup.git](https://github.com/TinLe/de-dup.git).
>
> Key enhancements in **de-dup**:
> - **Lock-Free Rust Engine**: Multi-threaded directory crawler and SIMD hasher (`dupeguru_rust`).
> - **HTML Web Console**: Responsive dark-mode web application for headless/remote server deployment.
> - **Scalable Cache Database**: Instant 18ms SQLite file unlinking and 5ms Valkey/Redis cache scaling.

**de-dup** is a cross-platform (Linux, macOS, Windows) tool to find and remove duplicate files on your computer. It includes a modern HTML Web UI Console as well as a native desktop shell powered by `pywebview`.

---

## 📚 Documentation Site

Our comprehensive documentation is organized into two main guides:

* **[User Guide](docs/user_guide/index.md)**:
  - [Quick Start & Installation](docs/user_guide/quickstart.md)
  - [HTML Web Console & Desktop Guide](docs/user_guide/web_console.md)
  - [Scanning Modes & Algorithms](docs/user_guide/scan_modes.md)
  - [Database & Caching](docs/user_guide/caching_and_database.md)
  - [FAQ & Troubleshooting](docs/user_guide/faq.md)

* **[Developer Guide](docs/developer_guide/index.md)**:
  - [System Architecture](docs/developer_guide/architecture.md)
  - [Rust Engine Pipeline](docs/developer_guide/rust_engine.md)
  - [Component Catalog](docs/developer_guide/components.md)
  - [Data Flow & Lifecycles](docs/developer_guide/data_flow.md)
  - [Building from Source](docs/developer_guide/building.md)
  - [Contributing Standards](docs/developer_guide/contributing.md)

### Building the Static Documentation Site locally:
```bash
make docs-serve    # Serves the documentation site locally with MkDocs
make docs-build    # Builds static HTML site to site/ directory
```

---

## ⚡ Quick Start

### Prerequisites
* **Python 3.10+**
* **Rust & Cargo** (for compiling the native Rust shared library)

### Build & Launch

```bash
git clone https://github.com/TinLe/de-dup.git
cd de-dup

# Build native C & Rust modules and setup virtual environment
make

# Launch the Native Desktop Application (pywebview shell)
make run

# Or launch as a standalone background Web Console server
make web
```

---

## 🚀 Key Features

### 1. Native Desktop Shell & HTML Web Console
- **pywebview Native Shell**: Native window frame on Windows 11 (WebView2), macOS (WebKit), and Linux (WebKitGTK) with native OS file dialogs.
- **Glassmorphic UI**: Responsive dark-mode interface designed for web browsers, desktop windows, and headless servers.
- **Duplicate Results Studio**: Dedicated high-density duplicate management studio with interactive path previews, directory hierarchy tags, and one-click batch marking.
- **Cross-Database Deduplication**: Compare duplicate sets across multiple isolated scan databases without merging or altering original scan metadata.
- **Remote / Headless Server Support**: Run scans on remote servers or NAS devices with non-blocking REST APIs and background progress polling.
- **Config Management**: Adjust similarity thresholds, regex matching, and ignored hardlinks dynamically.

### 2. Lock-Free Rust Engine & Cache Scaling
- **Rayon Parallel Crawler**: Multi-threaded directory walker collects files in parallel across all CPU cores.
- **SIMD Hasher**: Parallel block checksum calculator processes candidates without Python GIL lock delays.
- **Direct PyO3 FFI Dictionary Mapping**: Zero-copy structured data marshaling across Python 3.10 through 3.14.7.
- **Instant Cache Reset**: 18ms SQLite file unlinking and 5ms Valkey/Redis `FLUSHDB` operations.

---

## 🛠️ Repository Structure

* `core/`: Core business logic, scanning pipeline (`discovery`, `hasher`, `matcher`), database engines, and services.
* `rust_engine/`: Rust native extension source (`dupeguru_rust.so`).
* `web/`: Multi-threaded REST HTTP server (`server.py`) and static glassmorphic Web UI client assets.
* `run_desktop.py`: Native desktop shell entrypoint utilizing `pywebview` with native OS file dialog bridges.
* `docs/`: Comprehensive User Guide and Developer Guide documentation site source.
* `hscommon/`: Reusable cross-platform abstractions, job progress performers, and localization utilities.

---

## 📄 License & Credits

**de-dup** is licensed under the [GPLv3 License](LICENSE).
Original codebase created by Hardcoded Software and maintained by Andrew Senetar ([dupeGuru](https://github.com/arsenetar/dupeguru)).
Forked and enhanced by [Tin Le](https://github.com/TinLe/de-dup.git).

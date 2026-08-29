# de-dup

> [!NOTE]
> **de-dup** is a high-performance cross-platform duplicate file scanner. It was forked from [dupeGuru](https://github.com/arsenetar/dupeguru) and is maintained at [https://github.com/TinLe/de-dup.git](https://github.com/TinLe/de-dup.git).
>
> Key enhancements in **de-dup**:
> - **Lock-Free Rust Engine**: Multi-threaded directory crawler and SIMD hasher (`dupeguru_rust`).
> - **HTML Web Console**: Responsive dark-mode web application for headless/remote server deployment.
> - **Scalable Cache Database**: Instant 18ms SQLite file unlinking and 5ms Valkey/Redis cache scaling.

**de-dup** is a cross-platform (Linux, macOS, Windows) tool to find and remove duplicate files on your computer. It includes a traditional PyQt5 Desktop GUI application as well as a modern HTML Web UI Console.

---

## 📚 Documentation Site

Our comprehensive documentation is organized into two main guides:

* **[User Guide](docs/user_guide/index.md)**:
  - [Quick Start & Installation](docs/user_guide/quickstart.md)
  - [HTML Web Console Guide](docs/user_guide/web_console.md)
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
* **PyQt5** (for Desktop GUI mode)

### Build & Launch

```bash
git clone https://github.com/TinLe/de-dup.git
cd de-dup

# Build native C & Rust modules and setup virtual environment
make

# Launch the HTML Web UI Console (Recommended for Web/Server execution)
make web

# Or launch the Desktop GUI Application
make run
```

---

## 🚀 Key Features

### 1. HTML Web UI Console
- **Glassmorphic UI**: Responsive dark-mode interface designed for web browsers.
- **Remote / Headless Server Support**: Run scans on a remote Linux server or NAS and access results via browser.
- **Config Management**: Adjust similarity thresholds, regex matching, and ignored hardlinks dynamically.

### 2. Lock-Free Rust Engine & Cache Scaling
- **Rayon Parallel Crawler**: Multi-threaded directory walker collects files in parallel across all CPU cores.
- **SIMD Hasher**: Parallel block checksum calculator processes candidates without Python GIL lock delays.
- **Instant Cache Reset**: 18ms SQLite file unlinking and 5ms Valkey/Redis `FLUSHDB` operations.

---

## 🛠️ Repository Structure

* `core/`: Core business logic, scanner matching engine, and database abstraction wrappers.
* `rust_engine/`: Rust native extension source (`dupeguru_rust.so`).
* `web/`: Multi-threaded REST HTTP server (`server.py`) and static glassmorphic Web UI client assets.
* `qt/`: PyQt5 desktop frontend layouts and presenters.
* `docs/`: Comprehensive User Guide and Developer Guide documentation site source.
* `hscommon/`: Reusable GUI object abstractions, job progress performers, and localization utilities.

---

## 📄 License & Credits

**de-dup** is licensed under the [GPLv3 License](LICENSE).
Original codebase created by Hardcoded Software and maintained by Andrew Senetar ([dupeGuru](https://github.com/arsenetar/dupeguru)).
Forked and enhanced by [Tin Le](https://github.com/TinLe/de-dup.git).

# Building de-dup for macOS

This guide explains how to build **de-dup** and run its native `pywebview` desktop UI on macOS (Apple Silicon and Intel).

---

## Prerequisites

* **OS X / macOS 26.x or newer (macOS 15+ / Darwin 24+)**
* **Python 3.12+** (Python 3.12, 3.13, or 3.14 recommended via Homebrew or [python.org](https://www.python.org/))
* **Xcode Command Line Tools** or full Xcode:
  ```bash
  xcode-select --install
  ```
* **Rust & Cargo** (for compiling the native parallel engine `dupeguru_rust`):
  ```bash
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  ```

---

## Building from Source

de-dup uses a standard Python virtual environment and compiles the native Rust extension automatically via the `Makefile`:

```bash
cd de-dup

# Creates virtualenv, compiles C and Rust extensions, builds localization
make
```

---

## Running the Application

### 1. Native Desktop UI (pywebview)
Launches the lightweight desktop shell embedding the glassmorphic console in a native macOS WebKit window with native Finder dialogs:

```bash
make run
```

### 2. Standalone HTML Web Console
Runs the REST backend server in the background and opens your default browser:

```bash
make web
```

---

## Packaging a macOS App Bundle

To bundle de-dup into a standalone `.app` bundle:

1. Install packaging dependencies:
   ```bash
   ./env/bin/pip install -r requirements-extra.txt
   ```
2. Run the packager:
   ```bash
   ./env/bin/python package.py
   ```
   This generates `de-dup.app` inside the `dist/` directory.

---

## Running Automated Tests

Run the full pytest suite:

```bash
./env/bin/pytest
```

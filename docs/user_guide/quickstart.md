# Quick Start & Installation Guide

This page covers installation, prerequisites, building from source, and running **de-dup**.

---

## Prerequisites

* **Python 3.12+** (Python 3.12, 3.13, or 3.14 recommended)
* **Rust & Cargo** (for compiling the high-performance native Rust pipeline)

### Linux Dependencies (Debian / Ubuntu / Arch)
```bash
# Ubuntu / Debian
sudo apt update
sudo apt install python3-venv python3-dev build-essential cargo libwebkit2gtk-4.1-dev

# Arch Linux
sudo pacman -S python rust webkit2gtk-4.1
```

---

## Building from Source

Build **de-dup** with the provided `Makefile`:

```bash
git clone https://github.com/TinLe/de-dup.git
cd de-dup

# Build all modules (Python virtualenv, Rust engine, C modules)
make
```

---

## Running de-dup

de-dup offers two execution interfaces:

### 1. Native Desktop Application (pywebview)
Launch the native desktop window with native OS folder picker dialogs:

```bash
make run
```

### 2. Standalone HTML Web Console (Headless / Server Mode)
Launch the REST Web Server and automatically open the web application in your default browser:

```bash
make web
```

To run on a specific port (e.g. port `9090`):
```bash
./env/bin/python run_web.py --port 9090
```

---

## Running Tests

Verify your installation with the automated test suite:

```bash
make test
```

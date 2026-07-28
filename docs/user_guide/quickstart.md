# Quick Start & Installation Guide

This page covers installation, prerequisites, building from source, and running **de-dup**.

---

## Prerequisites

* **Python 3.8+** (Python 3.12 or 3.13 recommended)
* **Rust & Cargo** (for compiling the high-performance native Rust pipeline)
* **PyQt5** (required for the Desktop GUI mode)

### Linux Dependencies (Debian / Ubuntu / Arch)
```bash
# Ubuntu / Debian
sudo apt update
sudo apt install python3-pyqt5 pyqt5-dev-tools python3-venv python3-dev build-essential cargo

# Arch Linux
sudo pacman -S python-pyqt5 rust
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

### 1. HTML Web Console (Recommended for Headless & Servers)
Launch the REST Web Server and automatically open the web application in your default browser:

```bash
make web
```

To run on a specific port (e.g. port `9090`):
```bash
./env/bin/python run_web.py --port 9090
```

### 2. Desktop GUI Application (PyQt5)
Launch the traditional desktop application:

```bash
make run
```

---

## Running Tests

Verify your installation with the automated test suite:

```bash
make test
```

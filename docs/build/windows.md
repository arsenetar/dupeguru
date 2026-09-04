# Building de-dup for Windows 10 & 11

This guide explains how to build **de-dup** and run its native `pywebview` desktop UI on Windows.

---

## Prerequisites

* **[Python 3.10+](https://www.python.org/downloads/)** (Python 3.12, 3.13, or 3.14 recommended)
* **[Rust & Cargo](https://rustup.rs/)** (for compiling the native parallel engine `dupeguru_rust`)
* **[Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)** (C++ Build Tools workload with Windows 10/11 SDK)
* **[NSIS](https://nsis.sourceforge.io/)** (optional, for creating Windows installer executables)
* **[MSYS2](https://www.msys2.org/)** (optional, if using the `Makefile` workflow)

---

## Building from Source

### Method A: With Makefile (via MSYS2 or Git Bash)

1. Open the MSYS2 or Git Bash terminal:
   ```bash
   cd /path/to/de-dup
   make
   ```
2. Launch the application:
   ```bash
   make run
   ```

### Method B: Native Windows PowerShell / CMD

1. Create and activate a Python virtual environment:
   ```powershell
   cd de-dup
   py -3 -m venv .\env
   .\env\Scripts\activate
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Compile the C extension modules and Rust engine:
   ```powershell
   python build.py --modules
   cd rust_engine
   cargo build --release
   copy target\release\dupeguru_rust.dll ..\core\dupeguru_rust.pyd
   cd ..
   ```
4. Run the application:
   ```powershell
   python run.py
   ```

---

## Running the Application

### 1. Native Desktop UI (pywebview)
Embeds the glassmorphic HTML/JS interface inside a native Windows WebView2 (Edge Chromium) window with native Windows Explorer folder selection dialogs:

```powershell
python run.py
```

### 2. Standalone HTML Web Console
Runs the REST backend server and opens your default browser:

```powershell
python run_web.py
```

---

## Generating Windows Installer Packages

To generate a standalone Windows installer using NSIS:

1. Install extra packaging requirements:
   ```powershell
   pip install -r requirements-extra.txt
   ```
2. Run the packager:
   ```powershell
   python package.py
   ```

---

## Running Automated Tests

Run the full pytest suite:

```powershell
pytest
```

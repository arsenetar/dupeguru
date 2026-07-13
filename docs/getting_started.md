# Getting Started with dupeGuru

Welcome to **dupeGuru**! This guide will help you build dupeGuru from source, run the desktop application, use the new HTML Web Console, understand duplicate detection concepts, and manage configurations.

---

## 1. Prerequisites & Installation

Before building dupeGuru, ensure your development environment satisfies the required platform dependencies.

### System Package Requirements
- **macOS**: Python 3.8+ (from Homebrew or pyenv) and standard macOS developer command-line tools.
- **Linux (Debian/Ubuntu)**:
  ```bash
  sudo apt-get install python3-pyqt5 pyqt5-dev-tools python3-venv python3-dev build-essential
  ```
- **Windows**: Install Python 3.8+ and MSVC build tools. See [Windows.md](file:///Users/tinle/src/tinle/opensource/dupeguru/Windows.md) for detailed steps.

---

## 2. Quick Start (Using Make)

dupeGuru is equipped with a self-bootstrapping `Makefile` that automatically handles virtual environment creation, C modules compilation, and dependencies installation.

### Step 1: Set Up Development Environment (Optional)
If you plan to contribute, run the interactive setup helper to configure pre-commit hooks, `uv`, and OS-level package dependencies:
```bash
make dev-setup
```

### Step 2: Clone and Compile
Navigate to the root directory and build the project:
```bash
make
```
This target:
1. Installs/updates the virtual environment inside `./env` using `uv` (or `pip`).
2. Compiles high-performance C extension modules (`core/pe/_block.so`, `core/pe/_cache.so`).
3. Compiles Qt translation and resource files.

### Step 2: Run the Application
You can now run dupeGuru using either of its interface layers:

#### Option A: PyQt5 Desktop Application
Run the native Qt application:
```bash
make run
```

#### Option B: HTML Web Console
Start the local REST server and open the Web Console in your default browser:
```bash
make web
```
By default, the Web Console runs on `http://localhost:8080`. To launch it on a custom port:
```bash
./env/bin/python run_web.py --port 9090
```

---

## 3. Core Concepts & Workflow

Whether using the Desktop UI or the Web UI, the workflow remains identical:

### 1. Configure Scan Directories
Add the folders you wish to scan:
- In the **Web UI**, click **Add** next to any directory in the "Browse Folders" panel, or type/paste an absolute path and click **+**.
- *Note*: Added folders immediately show up in the **Target Directories** list. This list is saved to your standard configuration file and automatically restored when restarting the application.

### 2. Configure Scan Preferences
Before initiating a scan, customize parameters in the **Scan Preferences** sidebar card:
- **Filter Hardness**: Defines the duplicate threshold (e.g. 95% similarity match).
- **Checkpoint Frequency**: Controls how often the scanner writes metadata to the SQLite database (defaults to every 100 files). Keep it low for network-mounted drives.
- **Mix File Kind**: Toggles whether standard files of different file extensions (like `.jpg` and `.png`) should be matched.

### 3. Hashing, Checkpoints & Resumption
During scanning, file metadata and hashes are written and committed to the SQLite database (`hash_cache.db` at `~/.local/share/dupeGuru/hash_cache.db` on Linux).
- **Directory Walk Snapshotting**: As the scanner recursively walks directories (Phase 1 & 2), discovered file metadata is snapshotted immediately into the database. Once a subdirectory walk completes, it is flagged as scanned. If the scan is interrupted, you don't need to re-walk completed directories on disk next time.
- **Choose Scan Mode Dialog**: When starting a scan, you are prompted to choose:
  - **Resume Scan (Use Cache)**: Reuses existing checkpoints for both the directory walk and file content hashes, resuming the scan near-instantaneously from where it was stopped.
  - **Start Fresh (Clear Cache)**: Clears the cache database completely and scans all folders and files from the beginning.
- **Cache Database Viewer**: Click the **Cache Database Viewer** tab in the Web UI to view, search, and paginate through all file metadata currently cached in the SQLite database.

### 4. Review & Delete Matches
Once the duplicate scan completes, the results are listed:
- **Reference File**: One file in each duplicate group is selected as the "Reference" (kept by default).
- **Duplicate Files**: Duplicate matches are marked for action.
- **Action**: Click **Delete Marked Files** to permanently remove marked duplicates.
- **Save Scans**: You can save results to a `.dupegururesults` file (via **Save Results** in the results header) and reload them later using the **Load Scan** button in the sidebar.

---

## 4. Configuration Storage Paths

Configuration parameters are stored in the following standardized directories:

- **macOS & Linux**: `~/.config/dupeGuru/settings.ini`
- **Windows**: `%APPDATA%\dupeGuru\settings.ini` (or standard Registry keys)
- **Portable Mode**: `settings.ini` next to the executable.

*Note: Changes made in the Web Console preferences panel directly update this standard file, syncing options with the Qt UI.*

---

## 5. Release & Maintenance Workflows

For project maintainers, a release automation script is available:
- **Check Status**: `make release-status` (compares version and changelog).
- **Release Flow**:
  ```bash
  python scripts/release_helper.py release <new_version>
  ```
  This automatically bumps version metadata inside `core/__init__.py`, prepends release dates to the `help/changelog` file, runs the entire unit test suite (`pytest`), commits changes, and tags the git release (`v<version>`).

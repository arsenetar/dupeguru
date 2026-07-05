# dupeGuru Code Component Catalog

This document details the packages, modules, and file components of the **dupeGuru** codebase.

---

## 1. Core Logic Package (`core/`)

The [core/](file:///Users/tinle/src/tinle/opensource/dupeguru/core) package contains all the business logic, parsing, filesystem abstraction, and duplicate grouping algorithms.

### 1.1 App Coordination & State
- **[core/app.py](file:///Users/tinle/src/tinle/opensource/dupeguru/core/app.py)**: The central manager `DupeGuru` (subclassing `Broadcaster`). It connects and holds references to the directory list, scan results, ignore list, and exclude lists. It also kicks off and coordinates all asynchronous tasks (jobs) like scans, copies, and moves.
- **[core/markable.py](file:///Users/tinle/src/tinle/opensource/dupeguru/core/markable.py)**: A helper class implementing checkbox-like marking state tracking (invert, toggle, select all/none).
- **[core/directories.py](file:///Users/tinle/src/tinle/opensource/dupeguru/core/directories.py)**: Manages targeted folders and their scanning states (`NORMAL`, `REFERENCE`, or `EXCLUDED`).
- **[core/results.py](file:///Users/tinle/src/tinle/opensource/dupeguru/core/results.py)**: Holds groups of duplicate files and handles filtering, marking updates, sorting descriptors, and problem tracking.
- **[core/ignore.py](file:///Users/tinle/src/tinle/opensource/dupeguru/core/ignore.py)**: An XML-persisted database storing pairs of file paths that should not be flagged as duplicates.
- **[core/exclude.py](file:///Users/tinle/src/tinle/opensource/dupeguru/core/exclude.py)**: Manages regular expressions for files or directories that the scanner should skip.

### 1.2 File Hashing & Comparison Engine
- **[core/fs.py](file:///Users/tinle/src/tinle/opensource/dupeguru/core/fs.py)**: Implements the `FilesDB` singleton, a SQLite database (`hash_cache.db`) that caches file sizes, modification times, and hashes (MD5 or xxHash) to prevent re-reading file content on subsequent scans. It also contains the `File` class, which lazily reads metadata and computes hashes when accessed.
- **[core/scanner.py](file:///Users/tinle/src/tinle/opensource/dupeguru/core/scanner.py)**: Declares the base `Scanner` class that maps scanning types, controls options (like ignoring hardlinks or matching mixed file extensions), and compiles candidate pairs.
- **[core/engine.py](file:///Users/tinle/src/tinle/opensource/dupeguru/core/engine.py)**: Core fuzzy-string and exact-content matching functions.
  - `getwords()`: normalizes and tokenizes filenames.
  - `compare()`: calculates name similarity percentage.
  - `getmatches_by_contents()`: matches files using partial (first few blocks) or full hashes.
  - `Group`: groups pairs of duplicates transitively (if A matches B and B matches C, they are grouped together).
- **[core/prioritize.py](file:///Users/tinle/src/tinle/opensource/dupeguru/core/prioritize.py)**: Criterion classes (e.g., folder depth, extension, filename length, numeric endings) to automatically choose which file in a duplicate group should be the "reference" (preserved file) and which are duplicates (marked for deletion).

---

## 2. Edition-Specific Subsystems

dupeGuru supports three distinct run modes. Each mode inherits from and overrides the core engine classes.

### 2.1 Standard Edition (`core/se/` and `qt/se/`)
Used for generic file scanning (matching by filename, content, or folder content).
- **[core/se/scanner.py](file:///Users/tinle/src/tinle/opensource/dupeguru/core/se/scanner.py)**: Supports `FILENAME`, `CONTENTS`, and `FOLDERS` scan options.
- **[core/se/fs.py](file:///Users/tinle/src/tinle/opensource/dupeguru/core/se/fs.py)**: Implements basic file layout and display metrics (size formatting).
- **[qt/se/](file:///Users/tinle/src/tinle/opensource/dupeguru/qt/se)**: Contains the standard-edition Qt details dialogue and preferences options.

### 2.2 Music Edition (`core/me/` and `qt/me/`)
Analyzes audio files, matching by tag metadata (artist, album, title, genre) or contents.
- **[core/me/fs.py](file:///Users/tinle/src/tinle/opensource/dupeguru/core/me/fs.py)**: Implements `MusicFile` subclassing `File`. It integrates the **Mutagen** library to parse and extract audio metadata tags, length, bitrate, and samplerate.
- **[core/me/scanner.py](file:///Users/tinle/src/tinle/opensource/dupeguru/core/me/scanner.py)**: Supports scan options like `TAG` (matching metadata field values) and custom sorting overrides (ranking higher bitrate or file size first).

### 2.3 Picture Edition (`core/pe/` and `qt/pe/`)
Performs fuzzy picture matching using average color differences of pixel blocks, support for image rotations, and EXIF metadata original timestamp comparisons.
- **[core/pe/photo.py](file:///Users/tinle/src/tinle/opensource/dupeguru/core/pe/photo.py)**: Defines the base class `Photo` containing orientation decoding and EXIF metadata retrieval.
- **[core/pe/matchblock.py](file:///Users/tinle/src/tinle/opensource/dupeguru/core/pe/matchblock.py)**: The core of the fuzzy image-matching algorithm. It splits images into chunks and performs multi-core parallel comparisons using Python's `multiprocessing` package.
- **[core/pe/cache_sqlite.py](file:///Users/tinle/src/tinle/opensource/dupeguru/core/pe/cache_sqlite.py)**: A dedicated SQLite cache (`cached_pictures.db`) containing pre-calculated pixel block values.
- **High-Performance C Modules (`core/pe/modules/`)**:
  - `block.c`: Implements average color calculations and block comparisons in native C to accelerate scanning.
  - `block_osx.m`: macOS Objective-C Cocoa image block drawing helper (historically used).
  - `cache.c`: Fast cache structure helpers.

---

## 3. Shared Library Utilities (`hscommon/`)

[hscommon/](file:///Users/tinle/src/tinle/opensource/dupeguru/hscommon) is a shared utility layer.

- **[hscommon/notify.py](file:///Users/tinle/src/tinle/opensource/dupeguru/hscommon/notify.py)**: Declares the custom `Broadcaster` and `Listener` infrastructure that drives decoupled UI state notifications.
- **[hscommon/gui/](file:///Users/tinle/src/tinle/opensource/dupeguru/hscommon/gui)**: Generic GUI presenter classes:
  - `table.py`: Implements list/sequence abstractions for tables.
  - `tree.py`: Implements parent/child tree hierarchy models.
  - `selectable_list.py`: Manages item selection indexes.
- **[hscommon/jobprogress/](file:///Users/tinle/src/tinle/opensource/dupeguru/hscommon/jobprogress)**: Provides progress windows and progress-tracking models for long-running batch jobs (e.g. collecting file structures, computing hashes, deleting directories).

---

## 4. View & View Adapter layer (`qt/`)

The [qt/](file:///Users/tinle/src/tinle/opensource/dupeguru/qt) package contains all the PyQt5-specific widgets, views, and adaptor models.

- **[qt/app.py](file:///Users/tinle/src/tinle/opensource/dupeguru/qt/app.py)**: Instantiates the Qt `QApplication`, registers global hooks, binds the core application presenter class `DupeGuruModel`, and shows the initial main directory selection window.
- **[qt/table.py](file:///Users/tinle/src/tinle/opensource/dupeguru/qt/table.py)**: Adapts core presenter tables (`GUITable`) to Qt's `QAbstractTableModel` interface.
- **[qt/tree_model.py](file:///Users/tinle/src/tinle/opensource/dupeguru/qt/tree_model.py)**: Adapts core presenter tree structures (`GUITree`) to Qt's `QAbstractItemModel` interface.
- **[qt/results_model.py](file:///Users/tinle/src/tinle/opensource/dupeguru/qt/results_model.py)**: Connects standard duplicate list presenters to the `ResultWindow` `QTableView`.
- **[qt/directories_dialog.py](file:///Users/tinle/src/tinle/opensource/dupeguru/qt/directories_dialog.py)**: Dialog widget displaying scannable paths, allowing folders to be dragged-and-dropped and scan modes to be configured.

---

## 5. HTML Web Console & REST Server Components (`web/`)

The [web/](file:///Users/tinle/src/tinle/opensource/dupeguru/web) package contains the standalone web server and responsive Web Console components.

- **[run_web.py](file:///Users/tinle/src/tinle/opensource/dupeguru/run_web.py)**: The entry point to start the headless HTTP REST server. Parses port configurations and invokes the web listener.
- **[web/server.py](file:///Users/tinle/src/tinle/opensource/dupeguru/web/server.py)**: Built using the standard library's `http.server.BaseHTTPRequestHandler`.
  - Exposes REST API endpoints (`GET /api/status`, `POST /api/scan`, `GET/POST /api/config`, `GET/POST/DELETE /api/directories`).
  - Embeds `WebViewAdapter` representing the core presentation layer.
  - Implements browser non-caching HTTP response headers (`Cache-Control`, `Pragma`, `Expires`).
- **[web/static/index.html](file:///Users/tinle/src/tinle/opensource/dupeguru/web/static/index.html)**: The modern Web Console layout, containing the folders browser, targets sidebar list, scan progress tracker, preference forms, results table, and the glassmorphic toast notification container.
- **[web/static/app.css](file:///Users/tinle/src/tinle/opensource/dupeguru/web/static/app.css)**: A custom Vanilla CSS styling system. Implements colors, dark-mode styling, cards layout, glassmorphism, responsive grids, and fade/slide animations.
- **[web/static/app.js](file:///Users/tinle/src/tinle/opensource/dupeguru/web/static/app.js)**: Client-side JS application coordinating AJAX network fetch calls with cache busters (`?_t=timestamp`), rendering dynamic folder checkmarks (`✓ Added`), polling status updates, updating progress bars, and rendering duplicate matches.

---

## 6. Automation & Maintenance Scripts (`scripts/`)

- **[scripts/release_helper.py](file:///Users/tinle/src/tinle/opensource/dupeguru/scripts/release_helper.py)**: An automated release utility to check release readiness, run unit tests, bump metadata versions, update the changelog with today's date, and compile Git tags.
- **[scripts/migrate_config.py](file:///Users/tinle/src/tinle/opensource/dupeguru/scripts/migrate_config.py)**: A migration script designed to read legacy macOS defaults lists and web settings JSON files, merge them, write them to the new standard location (`~/.config/dupeGuru/settings.ini`), and cleanly delete old files.

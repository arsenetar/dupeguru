# Rust Engine & Native Pipeline

The **Rust Engine** (`rust_engine/`) provides high-performance, multithreaded backend primitives compiled directly into a native shared module (`dupeguru_rust.so`).

---

## Engine Modules

### 1. `RustFilesDB`
Implements the high-speed cache interface for SQLite and Valkey/Redis backends.
* **SQLite WAL Engine**: Utilizes `rusqlite` with `PRAGMA busy_timeout = 30000` and thread-safe Mutex synchronization.
* **Valkey/Redis Engine**: Connects via `redis-rs` and executes 5ms `FLUSHDB` operations for instant database clearing.

### 2. Parallel Directory Crawler (`collect_files_parallel`)
* **Crate Stack**: `walkdir` + `rayon`.
* **Execution**: Walks multi-root directory trees across all available CPU logical cores concurrently without acquiring Python GIL locks.
* **Signature**:
  ```rust
  pub fn collect_files_parallel(
      roots: Vec<String>,
      min_size: u64,
      max_size: Option<u64>,
  ) -> PyResult<Vec<(String, u64, f64)>>
  ```

### 3. Parallel File Hasher (`hash_files_parallel`)
* **Crate Stack**: `md5` + `rayon` + `std::io::BufReader`.
* **Execution**: Computes partial sampling or full MD5 checksums across thousands of candidate files in parallel.
* **Signature**:
  ```rust
  pub fn hash_files_parallel(
      paths_and_sizes: Vec<(String, u64)>,
      sample_size: usize,
  ) -> PyResult<Vec<(String, String)>>
  ```

### 4. Zero-Copy Cross-DB Deduplication (`cross_db_compare`)
* **Crate Stack**: `rusqlite` + `rayon` + `pyo3::types::{PyDict, PyList}`.
* **Execution**: Attaches or reads multiple isolated scan SQLite databases in parallel across CPU threads, groups matches by checksum, and constructs structured Python `PyDict` objects directly without intermediate tuple unpacking.
* **Signature**:
  ```rust
  pub fn cross_db_compare<'py>(
      py: Python<'py>,
      db_paths: Vec<String>,
  ) -> PyResult<Vec<Bound<'py, PyDict>>>
  ```

---

## 5. Scanner Pipeline Integration (Phase 4)

* **Directory Crawling Integration ([core/directories.py](file:///home/tin/src/opensource/dupeguru/core/directories.py#L104-L128))**:
  When `HAS_RUST` is active, `_get_files` delegates top-level directory discovery directly to `dupeguru_rust.collect_files_parallel()`, populating `fs.filesdb` and yielding scannable files in parallel.
* **Pre-Hashing Candidate Integration ([core/engine.py](file:///home/tin/src/opensource/dupeguru/core/engine.py#L305-L314))**:
  `getmatches_by_contents()` invokes `dupeguru_rust.hash_files_parallel()` to pre-calculate MD5 checksums across all logical CPU cores via Rayon SIMD processing before match grouping.

---

## 6. CI/CD & Automated Packaging (Phase 5)

* **Automated Module Build ([build.py](file:///home/tin/src/opensource/dupeguru/build.py#L117-L130))**: `python build.py --modules` automatically compiles `rust_engine` in release mode (`cargo build --release`) and copies `libdupeguru_rust.so` / `dupeguru_rust.pyd` into `core/`.
* **Multi-Platform CI/CD ([.github/workflows/build_rust_wheels.yml](file:///home/tin/src/opensource/dupeguru/.github/workflows/build_rust_wheels.yml))**: Automated GitHub Actions workflows compile and verify Rust native modules across Linux (x86_64) and macOS / OS X (Apple Silicon & Intel).

---

## 7. PyO3 0.29 Interoperability & Path Safety

The Rust engine targets **PyO3 0.29.2**, supporting Python 3.12 through Python 3.14.7.
* **Build Python Binding**: `build.py` and `Makefile` set `PYO3_PYTHON` to ensure `cargo` compiles against the active virtual environment ABI.
* **Path Sanitization**: Python paths containing non-UTF-8 bytes (surrogate escapes like `\udce0` on Linux) are sanitized prior to PyO3 function calls using:
```python
def _clean_path_str(path) -> str:
    s = str(path)
    return s.encode("utf-8", errors="surrogateescape").decode("utf-8", errors="replace")
```
This guarantees `PyUnicode_AsUTF8AndSize` string conversions never throw `UnicodeEncodeError`.

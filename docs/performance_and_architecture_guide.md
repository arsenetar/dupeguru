# de-dup Performance & Architecture Best Practices Guide

This document outlines core architectural patterns, SQLite optimization guidelines, threading rules, and UI responsiveness standards enforced across the `de-dup` codebase.

---

## 1. Concurrency & Web Server Threading Model

### Rule 1.1: Non-Blocking HTTP Handler Threads
* **Requirement**: HTTP request handlers in `web/server.py` (`do_GET`, `do_POST`, `do_DELETE`) MUST NEVER execute long-running loops, file content hashing, candidate duplicate matching, or heavy file deletions on the request handler thread.
* **Implementation**: All intensive tasks must be dispatched to background worker threads via `TaskRunner` / `TaskExecution`. Handlers must return an immediate JSON response (within < 10ms) containing `is_scanning: true` or task state.

### Rule 1.2: Status Polling Isolation (Zero SQL during Polling)
* **Requirement**: The web console polls `GET /api/status` every 500ms. Polling must NEVER trigger full-table SQL scans (`SELECT COUNT(*) FROM files`) or un-cached disk reads.
* **Implementation**: `TaskExecution` tracks progress percentages, file counts, and hashed counts in memory (`self._hashed_count_cache`). While a background worker thread is active, `get_dto()` serves values directly from memory, eliminating database lock contention between background writes and status checks.

### Rule 1.3: Thread Safety for Shared State
* **Requirement**: Shared global state (e.g. `app_state`, `selected_directories`) accessed across concurrent request threads spawned by `ThreadedHTTPServer` must be protected by thread locks (`threading.Lock`) or atomic updates.

---

## 2. SQLite Database Optimization & Concurrency

### Rule 2.1: Connection Timeout & WAL Mode
* **Requirement**: Every SQLite connection opened via `DBEngine` must set:
  ```python
  PRAGMA journal_mode = WAL;
  PRAGMA synchronous = NORMAL;
  PRAGMA busy_timeout = 60000;  # 60-second busy timeout
  ```
* **Rationale**: WAL (Write-Ahead Logging) mode allows concurrent readers and writers. Setting `busy_timeout = 60000` ensures that transient lock contention is resolved gracefully by SQLite's internal retry engine without throwing `database is locked`.

### Rule 2.2: Index Acceleration
* **Requirement**: All tables queried over large file datasets (1,000,000+ rows) MUST have indices on join and filtering columns:
  - `files(size)` (`idx_files_size`)
  - `files(digest_partial)` (`idx_files_digest_partial`)
  - `files(digest)` (`idx_files_digest`)
  - `duplicate_entries(group_id)` (`idx_dupe_entries_group`)
  - `duplicate_entries(file_path)` (`idx_dupe_entries_file`)

### Rule 2.3: CTE Query Optimization for Candidate Duplicates
* **Requirement**: Avoid unindexed subqueries like `WHERE size IN (SELECT size FROM files GROUP BY size HAVING COUNT(*) > 1)`.
* **Standard Pattern**: Use Common Table Expressions (CTEs) or indexed joins:
  ```sql
  WITH candidate_sizes AS (
      SELECT size FROM files WHERE size > 0 GROUP BY size HAVING COUNT(*) > 1
  )
  SELECT f.path, f.size, f.mtime_ns, f.digest_partial, f.digest
  FROM files f
  JOIN candidate_sizes cs ON f.size = cs.size
  ORDER BY f.size DESC, f.path ASC;
  ```

---

## 3. Duplicate Detection Pipeline Efficiency

### Rule 3.1: Unique Size Filtering
* **Requirement**: Files with unique byte sizes (`COUNT(*) == 1`) can NEVER be duplicates.
* **Implementation**: `DBEngine.get_candidate_duplicate_files()` filters candidates by `size > 0 AND COUNT(*) > 1`. Unique-size files are excluded from content hashing entirely.

### Rule 3.2: Two-Stage Hashing (Partial Digest First)
* **Requirement**: When calculating file content digests:
  1. Calculate partial hash (`digest_partial`, reading 16 KB) for candidate files sharing size.
  2. Group candidate files by `(size, digest_partial)`.
  3. Calculate full hash (`digest`) ONLY for candidate files that share both size AND partial digest.
* **Rationale**: Skipping full-file reads on multi-gigabyte files with distinct partial hashes speeds up processing on large datasets by orders of magnitude.

### Rule 3.3: Batch Flush Transactions & Retry Guards
* **Requirement**: `ContentHasher` flushes partial and full hashes to SQLite in batches (2,000 items) wrapped in a transaction with a 5-attempt retry loop.

---

## 4. Frontend & User Experience

### Rule 4.1: Live Feedback & Immediate Response
* **Requirement**: Interactive buttons ("View Results", "Refresh Scan", "Launch Scan") must immediately set loading states (`⏳ Loading...`), disable further clicks, and display toast feedback.
* **Implementation**: Active scanning tasks must render live percentage bars, status messages, and candidate file counts via `pollProgress()`.

### Rule 4.2: Zero-Duplicate Scan Persistence
* **Requirement**: Completed scans with 0 duplicate groups must persist state (`scan_metadata` key `status = completed`) and populate SQLite `duplicate_groups`.
* **Implementation**: `has_saved_duplicate_groups()` checks table existence and completed status metadata, allowing zero-duplicate scans to load instantly (< 1ms).

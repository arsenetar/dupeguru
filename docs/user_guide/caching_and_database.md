# Database & Caching

**de-dup** features an advanced dual-engine caching architecture designed for scanning millions of files without running out of memory.

---

## Storage Backends

### 1. High-Speed Local SQLite (Default)
By default, de-dup creates a local SQLite database at `~/.local/share/dupeGuru/hash_cache.db`.
* **Rust SQLite Engine**: Powered by Rust `rusqlite` with WAL (Write-Ahead Logging) mode.
* **Instant Cache Resets**: When starting a Fresh scan, de-dup performs instant file unlinking (`os.remove`) to reset the database in **18 milliseconds** and free gigabytes of hard drive space.

### 2. Valkey / Redis Engine (Network & Cluster Scaling)
For multi-node setups or extreme-scale datasets, set the `DUPEGURU_CACHE_URL` environment variable to point to a Valkey or Redis server:

```bash
export DUPEGURU_CACHE_URL="redis://:password@192.168.2.249:6379/1"
make web
```

Or via `Makefile`:
```bash
make web USE_REDIS=1 REDIS_HOST=192.168.2.249:6379 REDIS_PASS=secretpassword
```

---

## Cache Resumption & Performance Features

* **Subdirectory Checkpoints**: Scanned folders are marked as completed in the database. Interrupting and re-running a scan skips already-hashed subtrees.
* **Cache Converter Script**: Convert caches between SQLite and Valkey using:
  ```bash
  python scripts/convert_cache.py <source_db> <destination_db>
  ```

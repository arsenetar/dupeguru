# Frequently Asked Questions & Troubleshooting

### Q: What is the relationship between de-dup and dupeGuru?
**de-dup** is an optimized, high-performance re-architected fork of dupeGuru. It introduces a Rust parallel crawler, SIMD hasher, Valkey/Redis cache scaling, a modern HTML5/JS UI with native pywebview desktop shell integration, and a standalone Web Console mode for headless/remote server deployment.

### Q: Why does clearing a fresh scan database take only 18 ms?
We implemented instant file unlinking on disk for SQLite databases and 5ms `FLUSHDB` for Valkey/Redis, eliminating long table deletion stalls on multi-gigabyte cache files.

### Q: How are non-UTF-8 filenames handled on Linux?
Linux file paths with non-UTF-8 bytes (surrogate escapes like `\udce0`) are automatically sanitized using `surrogateescape` -> `replace` before entering PyO3 or JSON web streams, preventing server crashes.

### Q: How do I run de-dup as a desktop application vs a remote server?
- **Desktop Application**: Run `python run.py` (or `python run_desktop.py`) to launch the native pywebview desktop window.
- **Remote / Headless Server**: Run `python run_web.py --port 8080` on your remote machine and access the interface from any browser on your network.

# Frequently Asked Questions & Troubleshooting

### Q: What is the relationship between de-dup and dupeGuru?
**de-dup** is an optimized, high-performance fork of [dupeGuru](https://github.com/arsenetar/dupeguru). It introduces a Rust parallel crawler, SIMD hasher, Valkey/Redis cache scaling, and a glassmorphic HTML Web Console client for headless/remote server deployment.

### Q: Why does clearing a fresh scan database take only 18 ms?
We implemented instant file unlinking on disk for SQLite databases and 5ms `FLUSHDB` for Valkey/Redis, eliminating long table deletion stalls on multi-gigabyte cache files.

### Q: How are non-UTF-8 filenames handled on Linux?
Linux file paths with non-UTF-8 bytes (surrogate escapes like `\udce0`) are automatically sanitized using `surrogateescape` -> `replace` before entering PyO3 or JSON web streams, preventing server crashes.

### Q: How do I run de-dup on a remote server?
Run `make web` or `python run_web.py --port 8080` on your remote machine, and access the interface from any browser on your network.

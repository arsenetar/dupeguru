# HTML Web Console Guide

The **HTML Web Console** in **de-dup** provides a full-featured browser interface for managing duplicate scans, rendering results, and adjusting preferences without needing a graphical desktop display.

---

## Features

* **Glassmorphic Responsive UI**: Modern dark-mode interface built with Vanilla CSS and responsive design principles.
* **Direct Directory Browser**: Browse and select local or network paths directly from the web browser interface.
* **Live Progress Reporting**: Live status updates showing collected files, current folder paths, and progress percentage.
* **Instant Database Resumption**: Automatically saves scan state to the local cache engine (SQLite or Valkey/Redis).
* **Paginated Results Viewer**: Server-side pagination loads 50 duplicate groups at a time to prevent browser lag.

---

## Launching the Web Console

```bash
make web
```

The Web Console automatically starts on `http://localhost:8080` and opens your browser.

### Command-Line Flags

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--port` | Integer | `8080` | Specifies the HTTP port for the web server. |

Example:
```bash
./env/bin/python run_web.py --port 8090
```

---

## Configuration Settings

You can adjust scan options directly in the sidebar settings panel:

* **Filter Hardness**: Sets the similarity threshold (default `95%`). Lower values match looser duplicates.
* **Mix File Kinds**: When enabled, allows matching across different file extensions with identical contents.
* **Ignore Hardlink Matches**: Skips files that share the exact same physical inode on disk.
* **Checkpoints**: Frequency of database progress commits (default every `100` files).

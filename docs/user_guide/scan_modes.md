# Scanning Modes & Algorithms

**de-dup** offers three specialized scanning modes tailored to different types of file collections:

---

## 1. Standard Edition (SE)

Designed for general files, documents, archives, and codebases.

### Matching Modes:
* **Contents (Exact)**: Hashes file contents using MD5/xxHash block matching. 100% byte-for-byte accuracy.
* **Filename**: Matches files based on similarity of filenames, ignoring extensions or folder structures.

---

## 2. Music Edition (ME)

Designed for audio collections (`.mp3`, `.flac`, `.m4a`, `.ogg`, `.wav`).

### Matching Modes:
* **Audio Content**: Analyzes raw audio stream samples, ignoring ID3 tags or metadata differences.
* **Fields**: Matches tracks by comparing ID3 tags (Artist, Title, Album, Track Number, Duration).

---

## 3. Picture Edition (PE)

Designed for photo and image collections (`.png`, `.jpg`, `.jpeg`, `.gif`, `.heic`, `.webp`).

### Matching Modes:
* **Visual Content**: Uses a C/Rust native pixel-block matching algorithm to compare visual similarity even if images are resized, re-compressed, or converted to a different file format.

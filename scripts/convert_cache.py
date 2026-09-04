#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core import fs  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Convert dupeGuru cache database between SQLite and Valkey/Redis.")
    parser.add_argument(
        "source",
        help="Source DB path (e.g., path/to/hash_cache.db) or Redis/Valkey URL (e.g., redis://localhost:6379)",
    )
    parser.add_argument(
        "destination",
        help="Destination DB path or Redis/Valkey URL",
    )
    parser.add_argument(
        "--clear-destination",
        action="store_true",
        help="Clear destination database before conversion",
    )
    args = parser.parse_args()

    print(f"Connecting to source database: {args.source}...")
    src_db = fs.FilesDB()
    src_db.connect(args.source)

    print(f"Connecting to destination database: {args.destination}...")
    dst_db = fs.FilesDB()
    dst_db.connect(args.destination)

    if args.clear_destination:
        print("Clearing destination database...")
        dst_db.clear()

    # 1. Copy scanned directories
    print("Converting scanned directories...")
    scanned_dirs = []
    if hasattr(src_db.engine, "conn") and src_db.engine.conn:
        # SQLite
        cursor = src_db.engine.conn.execute("SELECT path FROM scanned_directories")
        scanned_dirs = [row[0] for row in cursor.fetchall()]
    elif hasattr(src_db.engine, "client") and src_db.engine.client:
        # Redis
        scanned_dirs = [d.decode("utf-8") for d in src_db.engine.client.smembers("dg:scanned_dirs")]

    for d in scanned_dirs:
        dst_db.mark_directory_scanned(Path(d))
    print(f"Successfully converted {len(scanned_dirs)} scanned directories.")

    # 2. Copy cached files and metadata
    print("Converting cached files (this may take a moment)...")

    total_files = 0
    if hasattr(src_db.engine, "conn") and src_db.engine.conn:
        cursor = src_db.engine.conn.execute("SELECT COUNT(*) FROM files")
        total_files = cursor.fetchone()[0]
    elif hasattr(src_db.engine, "client") and src_db.engine.client:
        total_files = src_db.engine.client.zcard("dg:files_by_path")

    print(f"Total files to convert: {total_files}")

    def get_source_files():
        if hasattr(src_db.engine, "conn") and src_db.engine.conn:
            # SQLite: use keyset pagination to prevent python-sqlite3 from loading the whole table
            limit = 5000
            last_path = ""
            while True:
                cursor = src_db.engine.conn.execute(
                    """SELECT path, size, mtime_ns, entry_dt, digest, digest_partial, digest_samples
                       FROM files
                       WHERE path > ?
                       ORDER BY path
                       LIMIT ?""",
                    (last_path, limit),
                )
                rows = cursor.fetchall()
                if not rows:
                    break
                for row in rows:
                    yield row
                last_path = rows[-1][0]
        elif hasattr(src_db.engine, "client") and src_db.engine.client:
            # Redis: scan keys lazily to avoid holding millions of items in memory
            for key in src_db.engine.client.scan_iter("dg:file:*"):
                path_str = key.decode("utf-8").replace("dg:file:", "", 1)
                meta = src_db.engine.client.hmget(
                    key, ["size", "mtime_ns", "entry_dt", "digest", "digest_partial", "digest_samples"]
                )
                if meta[0] is not None:
                    yield (
                        path_str,
                        int(meta[0]),
                        int(meta[1]) if meta[1] is not None else 0,
                        meta[2].decode("utf-8") if meta[2] is not None else "",
                        meta[3],  # digest bytes
                        meta[4],  # digest_partial bytes
                        meta[5],  # digest_samples bytes
                    )

    count = 0
    import gc

    for item in get_source_files():
        path_str, size, mtime_ns, entry_dt, digest, digest_partial, digest_samples = item

        dst_db.snapshot_file(Path(path_str), size, mtime_ns / 1e9)

        if digest:
            dst_db.put(Path(path_str), "digest", digest)
        if digest_partial:
            dst_db.put(Path(path_str), "digest_partial", digest_partial)
        if digest_samples:
            dst_db.put(Path(path_str), "digest_samples", digest_samples)

        count += 1
        if count % 2000 == 0:
            dst_db.commit()
            dst_db.scanned_paths.clear()
            dst_db.hit_paths.clear()
            gc.collect()
            print(f"Progress: Converted {count}/{total_files} files...", flush=True)

    dst_db.commit()
    dst_db.scanned_paths.clear()
    dst_db.hit_paths.clear()
    gc.collect()
    print(f"Conversion complete! Converted total of {count} files.")


if __name__ == "__main__":
    main()

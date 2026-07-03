#!/usr/bin/env python3
"""
dupeGuru Reporter Tool
A command-line tool to query dupeGuru's SQLite cache and results XML to generate reports.
"""

import argparse
import os
import sqlite3
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def get_default_db_path():
    """Detects the default hash_cache.db path depending on the operating system."""
    home = Path.home()
    if sys.platform == "darwin":
        return home / "Library/Application Support/dupeGuru/hash_cache.db"
    elif sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "dupeGuru/hash_cache.db"
        return home / "AppData/Roaming/dupeGuru/hash_cache.db"
    else:  # Linux / POSIX
        return home / ".local/share/dupeGuru/hash_cache.db"


def format_size(bytes_val):
    """Formats bytes into human-readable sizes."""
    if bytes_val is None:
        return "N/A"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"


def get_extension(path_str):
    """Extracts lowercase file extension from path string."""
    _, ext = os.path.splitext(path_str)
    return ext.lower() if ext else "no extension"


def analyze_db(db_path, fmt):
    """Analyzes the SQLite hash_cache.db and generates reports."""
    if not db_path.exists():
        print(f"Error: Database file not found at: {db_path}", file=sys.stderr)
        print("Run dupeGuru first to generate a scan cache.", file=sys.stderr)
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # 1. General Database Stats
    cursor.execute("SELECT COUNT(*), SUM(size) FROM files")
    total_files, total_size = cursor.fetchone()
    total_size = total_size or 0

    # 2. Duplicate Analysis (files with identical digests)
    cursor.execute(
        "SELECT digest, size, COUNT(*) as cnt FROM files WHERE digest IS NOT NULL GROUP BY digest HAVING COUNT(*) > 1"
    )
    dup_groups = cursor.fetchall()

    total_groups = len(dup_groups)
    total_dupes = sum(group[2] for group in dup_groups)
    reclaimable_bytes = sum(group[1] * (group[2] - 1) for group in dup_groups)
    total_duplicate_files_bytes = sum(group[1] * group[2] for group in dup_groups)

    # 3. Retrieve files to build top largest groups and extension breakdowns
    cursor.execute("SELECT path, size, digest FROM files WHERE digest IS NOT NULL")
    all_files = cursor.fetchall()
    conn.close()

    # Extension distribution
    ext_stats = {}  # {ext: {'count': 0, 'size': 0, 'dupes': 0, 'reclaimable': 0}}
    digest_to_size = {}
    digest_to_paths = {}

    for path, size, digest in all_files:
        ext = get_extension(path)
        if ext not in ext_stats:
            ext_stats[ext] = {"count": 0, "size": 0, "dupes": 0, "reclaimable": 0}
        ext_stats[ext]["count"] += 1
        ext_stats[ext]["size"] += size

        digest_to_size[digest] = size
        if digest not in digest_to_paths:
            digest_to_paths[digest] = []
        digest_to_paths[digest].append((path, size))

    # Calculate duplicate details per extension
    for digest, size, count in dup_groups:
        paths = digest_to_paths.get(digest, [])
        for path, _ in paths:
            ext = get_extension(path)
            if ext in ext_stats:
                ext_stats[ext]["dupes"] += 1
        # Distribute reclaimable space proportionally
        if paths:
            ext = get_extension(paths[0][0])
            ext_stats[ext]["reclaimable"] += size * (count - 1)

    # Top 10 largest groups
    sorted_groups = sorted(dup_groups, key=lambda x: x[1] * (x[2] - 1), reverse=True)

    # Output generation
    if fmt == "markdown":
        print(f"# dupeGuru Cache Report: `{db_path.name}`\n")
        print("## General Cache Statistics\n")
        print(f"- **Total Cached Files**: {total_files:,}")
        print(f"- **Total Cached Size**: {format_size(total_size)}")
        print(f"- **Database Disk Size**: {format_size(os.path.getsize(db_path))}\n")

        print("## Duplicate Summary\n")
        print(f"- **Duplicate Groups (Unique Sets)**: {total_groups:,}")
        print(
            f"- **Total Duplicate Files**: {total_dupes:,} / {total_files:,} ({total_dupes / total_files * 100:.1f}%)"
        )
        print(f"- **Total Space Occupied by Duplicates**: {format_size(total_duplicate_files_bytes)}")
        print(f"- **Reclaimable Space (Preserving 1 file/group)**: **{format_size(reclaimable_bytes)}**\n")

        print("## File Extension Breakdown\n")
        print("| Extension | Total Files | Total Size | Dupes Count | Reclaimable Space |")
        print("| --- | --- | --- | --- | --- |")
        for ext, stat in sorted(ext_stats.items(), key=lambda x: x[1]["size"], reverse=True)[:15]:
            print(
                f"| `{ext}` | {stat['count']:,} | {format_size(stat['size'])} | {stat['dupes']:,} | {format_size(stat['reclaimable'])} |"
            )
        print("\n*Showing top 15 extensions by size.*\n")

        print("## Top 10 Largest Reclaimable Duplicate Groups\n")
        for idx, (digest, size, count) in enumerate(sorted_groups[:10], 1):
            group_reclaim = size * (count - 1)
            print(
                f"### Group {idx}: {format_size(group_reclaim)} Reclaimable (Size: {format_size(size)}, {count} copies)"
            )
            paths = digest_to_paths.get(digest, [])
            for path, _ in paths:
                print(f"- `{path}`")
            print()
    else:
        print("=" * 60)
        print(f"dupeGuru Cache Report: {db_path.name}")
        print("=" * 60)
        print(f"Total Cached Files:          {total_files:,}")
        print(f"Total Cached Size:           {format_size(total_size)}")
        print(f"Database Disk Size:          {format_size(os.path.getsize(db_path))}")
        print("-" * 60)
        print(f"Duplicate Groups:            {total_groups:,}")
        print(f"Total Duplicate Files:       {total_dupes:,}")
        print(f"Total Reclaimable Space:     {format_size(reclaimable_bytes)}")
        print("=" * 60)
        print("Top 10 Largest Duplicate Groups:")
        for idx, (digest, size, count) in enumerate(sorted_groups[:10], 1):
            group_reclaim = size * (count - 1)
            print(
                f"\n{idx}. Group Reclaimable: {format_size(group_reclaim)} (Size: {format_size(size)}, Copies: {count})"
            )
            paths = digest_to_paths.get(digest, [])
            for path, _ in paths:
                print(f"   - {path}")
        print("-" * 60)


def analyze_xml(xml_path, db_path, fmt):
    """Parses .dupegururesults XML file and matches file sizes from database or disk."""
    if not xml_path.exists():
        print(f"Error: XML file not found at: {xml_path}", file=sys.stderr)
        return

    # Try loading file sizes from the SQLite DB cache
    path_to_size = {}
    if db_path and db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT path, size FROM files")
            for path, size in cursor.fetchall():
                path_to_size[path] = size
            conn.close()
        except Exception:
            pass

    # Parse XML
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing XML file: {e}", file=sys.stderr)
        return

    groups_count = 0
    total_files = 0
    marked_count = 0
    reference_count = 0
    reclaimable_bytes = 0
    unmarked_bytes = 0
    marked_paths = []

    for group in root.findall("group"):
        groups_count += 1
        for file_elem in group.findall("file"):
            total_files += 1
            path = file_elem.get("path")
            is_ref = file_elem.get("is_ref") == "y"
            marked = file_elem.get("marked") == "y"

            # Determine size: cache DB, disk, or fallback 0
            size = path_to_size.get(path)
            if size is None:
                try:
                    size = os.path.getsize(path)
                except OSError:
                    size = 0  # Fallback

            if is_ref:
                reference_count += 1
            if marked:
                marked_count += 1
                reclaimable_bytes += size
                marked_paths.append((path, size))
            elif not is_ref:
                unmarked_bytes += size

    if fmt == "markdown":
        print(f"# dupeGuru Results Report: `{xml_path.name}`\n")
        print("## Scan Results Overview\n")
        print(f"- **Total Duplicate Groups**: {groups_count:,}")
        print(f"- **Total Scanned Duplicate Entries**: {total_files:,}")
        print(f"- **Reference Files**: {reference_count:,}")
        print(f"- **Marked Files (Scheduled for Deletion)**: {marked_count:,}")
        print(f"- **Reclaimable Space from Marked Files**: **{format_size(reclaimable_bytes)}**")
        print(f"- **Space Occupied by Unmarked Duplicates**: {format_size(unmarked_bytes)}\n")

        if marked_paths:
            print("## Files Scheduled for Deletion (Marked)\n")
            print("| Path | Size |")
            print("| --- | --- |")
            for path, size in sorted(marked_paths, key=lambda x: x[1], reverse=True)[:30]:
                print(f"| `{path}` | {format_size(size)} |")
            if len(marked_paths) > 30:
                print(f"\n*And {len(marked_paths) - 30} more files.*")
    else:
        print("=" * 60)
        print(f"dupeGuru XML Results Report: {xml_path.name}")
        print("=" * 60)
        print(f"Total Duplicate Groups:      {groups_count:,}")
        print(f"Total Duplicate Entries:     {total_files:,}")
        print(f"Reference Files:             {reference_count:,}")
        print(f"Marked Files for Deletion:   {marked_count:,}")
        print(f"Reclaimable Space:           {format_size(reclaimable_bytes)}")
        print(f"Unmarked Duplicate Space:    {format_size(unmarked_bytes)}")
        print("=" * 60)
        if marked_paths:
            print("Top 10 Largest Files Scheduled for Deletion:")
            for idx, (path, size) in enumerate(sorted(marked_paths, key=lambda x: x[1], reverse=True)[:10], 1):
                print(f"   {idx}. {format_size(size)} - {path}")
        print("-" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Generate analytics and reports from dupeGuru SQLite cache databases and saved XML results."
    )
    parser.add_argument(
        "--db",
        type=str,
        help="Path to dupeGuru's hash_cache.db (auto-detected by default)",
    )
    parser.add_argument(
        "--xml",
        type=str,
        help="Path to a saved .dupegururesults XML file",
    )
    parser.add_argument(
        "--format",
        choices=["text", "markdown"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    db_path = Path(args.db) if args.db else get_default_db_path()

    if args.xml:
        xml_path = Path(args.xml)
        analyze_xml(xml_path, db_path, args.format)
    else:
        print(f"Analyzing SQLite cache from: {db_path}")
        analyze_db(db_path, args.format)


if __name__ == "__main__":
    main()

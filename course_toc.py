#!/usr/bin/env python3
"""
course_toc.py — Generate a Table of Contents for any video course folder.

Scans a folder for video files, reads their durations via ffprobe,
groups them by subfolder (week/module/section), and writes both a
plain-text summary and a CSV file you can import into Google Sheets.

Requirements:
    ffprobe (included with ffmpeg) — https://ffmpeg.org/download.html

Usage:
    python3 course_toc.py "/path/to/course folder"

Output (saved inside the course folder):
    Course Table of Contents.txt
    Course Table of Contents.csv
"""

import os
import re
import sys
import subprocess
from collections import OrderedDict

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".m4v", ".webm", ".flv", ".wmv"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_duration_secs(filepath):
    """Return video duration in seconds using ffprobe, or 0 on failure."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                filepath,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        val = result.stdout.strip()
        return int(float(val)) if val else 0
    except Exception:
        return 0


def secs_to_readable(secs):
    """Convert seconds to a human-readable string like '1h 23m 45s'."""
    h = secs // 3600
    m = (secs % 3600) // 60
    s = secs % 60
    if h > 0:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s"


def secs_to_mins(secs):
    """Convert seconds to rounded minutes (1 decimal place)."""
    return round(secs / 60, 1)


def clean_title(filename):
    """
    Strip file extension and tidy up common filename patterns.
    e.g. '01. Introduction to Python.mp4' -> 'Introduction to Python'
    """
    name = os.path.splitext(filename)[0]
    name = name.replace("_amp;", "&").replace("_", " ")
    # Remove leading numbering patterns: "01.", "1-", "1)", "01 - ", etc.
    name = re.sub(r"^[\d]+[\.\-\)\s]+\s*", "", name).strip()
    return name or os.path.splitext(filename)[0]


def check_ffprobe():
    """Exit with a clear message if ffprobe is not installed."""
    try:
        subprocess.run(
            ["ffprobe", "-version"],
            capture_output=True,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("\nError: ffprobe not found.")
        print("Install ffmpeg to get ffprobe: https://ffmpeg.org/download.html")
        print("  macOS:   brew install ffmpeg")
        print("  Ubuntu:  sudo apt install ffmpeg")
        print("  Windows: https://ffmpeg.org/download.html\n")
        sys.exit(1)


# ── Core logic ────────────────────────────────────────────────────────────────

def find_videos(root):
    """
    Walk the root folder and collect all video files.
    Returns a list of (group_label, filepath, title) tuples,
    grouped by the immediate first-level subfolder name.
    Duplicate file paths are removed.
    """
    root = os.path.abspath(root)
    root_name = os.path.basename(root)
    seen_paths = set()
    results = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()

        rel = os.path.relpath(dirpath, root)
        group = root_name if rel == "." else rel.split(os.sep)[0]

        for filename in sorted(filenames):
            if os.path.splitext(filename)[1].lower() in VIDEO_EXTENSIONS:
                filepath = os.path.join(dirpath, filename)
                if filepath not in seen_paths:
                    seen_paths.add(filepath)
                    results.append((group, filepath, clean_title(filename)))

    return results


def build_toc(course_folder):
    course_name = os.path.basename(os.path.abspath(course_folder))

    print(f"\ncourse-toc-generator")
    print(f"{'─' * 40}")
    print(f"Course : {course_name}")
    print(f"Folder : {course_folder}")
    print(f"{'─' * 40}")
    print("Scanning for video files...")

    videos = find_videos(course_folder)

    if not videos:
        print("\nNo video files found. Supported formats:", ", ".join(sorted(VIDEO_EXTENSIONS)))
        return

    print(f"Found {len(videos)} video(s). Reading durations...\n")

    # Build grouped structure preserving folder order
    groups = OrderedDict()
    for i, (group, filepath, title) in enumerate(videos, 1):
        print(f"  [{i:>3}/{len(videos)}] {title[:65]}")
        secs = get_duration_secs(filepath)
        groups.setdefault(group, []).append((title, secs))

    grand_total = sum(s for vids in groups.values() for _, s in vids)

    # ── Write TXT ─────────────────────────────────────────────────────────
    txt_lines = []
    txt_lines.append(course_name.upper())
    txt_lines.append("Table of Contents")
    txt_lines.append("=" * 72)
    txt_lines.append("")

    for group_label, vids in groups.items():
        group_total = sum(s for _, s in vids)
        txt_lines.append("─" * 72)
        txt_lines.append(f"  {group_label}")
        txt_lines.append(f"  Duration: {secs_to_readable(group_total)}  |  {len(vids)} video(s)")
        txt_lines.append("─" * 72)
        for idx, (title, secs) in enumerate(vids, 1):
            txt_lines.append(f"  {idx:>2}. {title:<50} {secs_to_readable(secs)}")
        txt_lines.append("")

    txt_lines.append("=" * 72)
    txt_lines.append(f"  TOTAL DURATION: {secs_to_readable(grand_total)}")
    txt_lines.append("=" * 72)

    txt_path = os.path.join(course_folder, "Course Table of Contents.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(txt_lines))

    # ── Write CSV ─────────────────────────────────────────────────────────
    csv_lines = ["Section,Video #,Title,Duration,Duration (mins)"]

    for group_label, vids in groups.items():
        group_total = sum(s for _, s in vids)
        for idx, (title, secs) in enumerate(vids, 1):
            safe_title = title.replace('"', "'").replace(",", ";")
            safe_group = group_label.replace('"', "'")
            csv_lines.append(
                f'"{safe_group}",{idx},"{safe_title}",'
                f'{secs_to_readable(secs)},{secs_to_mins(secs)}'
            )
        csv_lines.append(
            f'"{group_label} – TOTAL","","",'
            f'{secs_to_readable(group_total)},{secs_to_mins(group_total)}'
        )
        csv_lines.append("")

    csv_lines.append(
        f'"GRAND TOTAL","","",'
        f'{secs_to_readable(grand_total)},{secs_to_mins(grand_total)}'
    )

    csv_path = os.path.join(course_folder, "Course Table of Contents.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("\n".join(csv_lines))

    # ── Summary ───────────────────────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print(f"  Output saved to:")
    print(f"    {txt_path}")
    print(f"    {csv_path}")
    print(f"\n  TOTAL DURATION : {secs_to_readable(grand_total)}")
    print(f"  TOTAL VIDEOS   : {len(videos)}")
    print(f"{'=' * 72}")
    print("\n  Section breakdown:")
    for group_label, vids in groups.items():
        t = sum(s for _, s in vids)
        print(f"    {group_label}: {secs_to_readable(t)} ({len(vids)} videos)")
    print()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    folder = sys.argv[1].strip().rstrip("/")

    if not os.path.isdir(folder):
        print(f"\nError: '{folder}' is not a valid folder.\n")
        sys.exit(1)

    check_ffprobe()
    build_toc(folder)

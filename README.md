# course-toc-generator

A simple command-line tool that scans any video course folder and generates a **Table of Contents** — complete with video titles, durations, and section totals — exported as both a plain-text file and a CSV you can import directly into Google Sheets or Excel.

---

## Why?

Downloaded a video course and want to know what's inside before diving in? This tool gives you a high-level overview of every video, how long each one is, and the total watch time — so you can plan your learning without opening a single file.

---

## Output

Two files are saved directly inside your course folder:

- `Course Table of Contents.txt` — clean, readable plain text
- `Course Table of Contents.csv` — importable into Google Sheets / Excel

**Sample CSV output** (Google Sheets):

| Section | Video # | Title | Duration | Duration (mins) |
|---|---|---|---|---|
| Week 1 – Getting Started | 1 | Welcome & Course Overview | 8m 14s | 8.2 |
| Week 1 – Getting Started | 2 | Setting Up Your Environment | 12m 33s | 12.6 |
| Week 1 – Getting Started | 3 | Core Concepts Explained | 24m 07s | 24.1 |
| Week 1 – Getting Started – TOTAL | | | 1h 16m 46s | 76.8 |
| Week 2 – Building Foundations | 1 | Understanding the Fundamentals | 45m 10s | 45.2 |
| ... | | | | |
| GRAND TOTAL | | | 12h 18m 17s | 738.4 |

Full sample files: [`sample_output/`](sample_output/)

---

## Requirements

- **Python 3** — comes pre-installed on macOS/Linux. [Download for Windows](https://www.python.org/downloads/)
- **ffprobe** — included with ffmpeg. Install it once:

| OS | Command |
|---|---|
| macOS | `brew install ffmpeg` |
| Ubuntu/Debian | `sudo apt install ffmpeg` |
| Windows | [Download from ffmpeg.org](https://ffmpeg.org/download.html) |

---

## Installation

Just download the single script file — no packages to install.

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/course-toc-generator.git

# Or download the script directly
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/course-toc-generator/main/course_toc.py
```

---

## Usage

```bash
python3 course_toc.py "/path/to/your/course folder"
```

**Tip — macOS/Linux shortcut:** Type the command, then drag and drop the course folder from Finder/Files directly into your Terminal window to auto-fill the path.

```bash
python3 course_toc.py    # then drag folder in → press Enter
```

---

## How It Works

1. Recursively scans the folder for video files (`.mp4`, `.mkv`, `.mov`, `.avi`, `.m4v`, `.webm`, `.flv`, `.wmv`)
2. Groups videos by their immediate parent subfolder (Week 1, Module 2, etc.)
3. Reads each video's duration using `ffprobe`
4. Writes `Course Table of Contents.txt` and `Course Table of Contents.csv` into the course folder

---

## Supported Video Formats

`.mp4` · `.mkv` · `.mov` · `.avi` · `.m4v` · `.webm` · `.flv` · `.wmv`

---

## Import CSV into Google Sheets

1. Open [Google Sheets](https://sheets.google.com) → **File → Import**
2. Upload `Course Table of Contents.csv`
3. Set separator to **Comma** → Import

---

## License

MIT — free to use, modify, and share.

#!/usr/bin/env python3
"""
compile_book.py
Compiles manuscript Markdown chapters into:
  1. dist/WHAT_WAS_IN_THAT_JOINT_BRO.compiled.md (Master KDP Manuscript)
  2. dist/book_data.json (Structured data for SPA wiki generator)
  3. Optional ePub / PDF via Pandoc if installed
"""

import os
import re
import json
import shutil
import subprocess
from pathlib import Path

CHAPTER_FILES = [
    "00. Title.md",
    "01. Introduction.md",
    "02. Ch 1 Why Test What You Take.md",
    "03. Ch 2 The Kitchen, the Thermos, and the Keychain Light.md",
    "04. Ch 3 Paper, Light, and Lemon - The Chemistry in Plain English.md",
    "05. Ch 4 SPOT - Taking the Sample.md",
    "06. Ch 5 SNAP - The Phone Does the Seeing.md",
    "07. Ch 6 KNOW - Reading Your Results.md",
    "08. Ch 7 When the Result Scares You.md",
    "09. Ch 8 What This Can't Tell You.md",
    "10. One-Page Field SOP.md",
    "11. Ch 9 The Purple Canary Protocol (Full SOP).md",
    "12. Ch 10 Why Your Agency Needs This.md",
    "13. Ch 11 Deploying the Protocol.md",
    "14. Ch 12 Training Your Team.md",
    "15. Ch 13 Restocking and Sustaining.md",
    "16. Ch 14 The Economics of Free Testing.md",
    "17. Ch 15 Open Methods, Open Knowledge.md",
    "18. Closing - The Living Protocol.md",
    "19. Back Matter.md",
    "20. Sequel - The Cannabinoid Cookbook.md",
]

def clean_chapter_content(content: str) -> str:
    # Normalize line endings
    content = content.replace("\r\n", "\n")
    # Clean excessive trailing page breaks for JSON extraction
    return content.strip()

def extract_headings(markdown_text: str):
    """Extract h1, h2, h3 for table-of-contents generation."""
    headings = []
    for line in markdown_text.splitlines():
        match = re.match(r"^(#{1,3})\s+(.+)$", line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            slug = re.sub(r"[^\w\- ]", "", title).lower().replace(" ", "-")
            headings.append({"level": level, "title": title, "slug": slug})
    return headings

def compile_manuscript():
    root = Path(__file__).parent.resolve()
    dist = root / "dist"
    dist.mkdir(exist_ok=True)

    master_md_lines = []
    book_structure = {
        "title": "What Was In That Joint Bro!?",
        "subtitle": "An Introduction To The Purple Canary Protocol",
        "author": "Michael Scott Hoyt",
        "chapters": []
    }

    print(f"[*] Processing {len(CHAPTER_FILES)} chapters...")

    for idx, fname in enumerate(CHAPTER_FILES):
        fpath = root / fname
        if not fpath.exists():
            print(f"[!] Warning: missing {fname}")
            continue

        raw = fpath.read_text(encoding="utf-8")
        cleaned = clean_chapter_content(raw)
        
        # Derive human friendly chapter name
        clean_name = re.sub(r"^\d+\.\s*", "", fname.replace(".md", ""))
        first_h1 = re.search(r"^#\s+(.+)$", cleaned, re.MULTILINE)
        display_title = first_h1.group(1) if first_h1 else clean_name

        slug = f"ch-{idx:02d}-{re.sub(r'[^a-zA-Z0-9]+', '-', clean_name).lower().strip('-')}"

        book_structure["chapters"].append({
            "id": slug,
            "filename": fname,
            "title": display_title,
            "headings": extract_headings(cleaned),
            "markdown": cleaned
        })

        master_md_lines.append(cleaned)
        master_md_lines.append("\n\n<div style=\"page-break-after: always;\"></div>\n\n")

    compiled_md_path = dist / "WHAT_WAS_IN_THAT_JOINT_BRO.compiled.md"
    compiled_md_path.write_text("".join(master_md_lines), encoding="utf-8")
    print(f"[+] Master Markdown written: {compiled_md_path}")

    json_path = dist / "book_data.json"
    json_path.write_text(json.dumps(book_structure, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Wiki JSON dataset written: {json_path}")

    # Optional Pandoc build for ePub / PDF
    if shutil.which("pandoc"):
        print("[*] Pandoc found. Generating EPUB & PDF...")
        try:
            epub_path = dist / "WHAT_WAS_IN_THAT_JOINT_BRO.epub"
            subprocess.run([
                "pandoc", str(compiled_md_path),
                "-o", str(epub_path),
                "--toc", "--toc-depth=2",
                "--metadata", f"title={book_structure['title']}",
                "--metadata", f"author={book_structure['author']}"
            ], check=True)
            print(f"[+] EPUB generated: {epub_path}")
        except Exception as e:
            print(f"[!] EPUB conversion skipped: {e}")
    else:
        print("[i] Pandoc not found. Skipped binary EPUB/PDF compilation.")

if __name__ == "__main__":
    compile_manuscript()

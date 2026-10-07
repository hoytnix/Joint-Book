#!/usr/bin/env python3
"""
Book Compilation Script for "WHAT WAS IN THAT JOINT BRO!?"
Compiles split Markdown chapters/sections into publication-ready formats:
  - PDF (Print interior formatted via WeasyPrint)
  - EPUB / KDP (Kindle Direct Publishing eBook package)
  - HTML (Single-file book preview / Kindle Create import)
  - Markdown (Unified single manuscript)

Usage:
    python3 compile_book.py [OPTIONS]

Options:
    -f, --format {all,pdf,epub,html,markdown}
                            Output format to generate (default: all)
    -i, --input-dir DIR     Directory containing chapter markdown files (default: .)
    -o, --output-dir DIR    Directory where compiled files will be saved (default: ./dist)
    --title TITLE           Book title override
    --author AUTHOR         Author name override
    -h, --help              Show this help message and exit
"""

import os
import sys
import re
import glob
import html
import zipfile
import argparse

try:
    import weasyprint
    HAS_WEASYPRINT = True
except ImportError:
    HAS_WEASYPRINT = False


BOOK_METADATA = {
    "title": "WHAT WAS IN THAT JOINT BRO!?",
    "subtitle": "An Introduction To The Purple Canary Protocol",
    "author": "Michael Scott Hoyt",
    "publisher": "Independently published via Kindle Direct Publishing",
    "copyright": "2026 Michael Scott Hoyt. All rights reserved.",
    "identifier": "urn:uuid:purple-canary-protocol-2026",
    "language": "en",
}


def get_sorted_chapter_files(input_dir):
    """Find and return all numbered chapter files in sorted order."""
    pattern = os.path.join(input_dir, "[0-9][0-9]. *.md")
    files = sorted(glob.glob(pattern))
    if not files:
        # Fallback to all .md files excluding Manuscript.md and compiled outputs
        files = sorted([
            f for f in glob.glob(os.path.join(input_dir, "*.md"))
            if not os.path.basename(f).startswith("Manuscript")
            and not os.path.basename(f).startswith("README")
        ])
    return files


def markdown_to_html(md_text):
    """
    Pure-Python Markdown to HTML converter supporting:
    - Headings (# to ######)
    - Fenced code blocks (``` ... ```)
    - Tables (| ... |)
    - Blockquotes (>)
    - Lists (* and 1.)
    - Emphasis (**bold**, *italic*)
    - Inline code (`...`)
    - Horizontal rules (---)
    - Math notation ($...$, $$...$$)
    """
    lines = md_text.splitlines()
    html_out = []

    in_code_block = False
    code_block_lang = ""
    code_block_lines = []

    in_table = False
    table_lines = []

    in_ul = False
    in_ol = False
    in_blockquote = False
    blockquote_lines = []

    def close_lists():
        nonlocal in_ul, in_ol
        res = []
        if in_ul:
            res.append("</ul>")
            in_ul = False
        if in_ol:
            res.append("</ol>")
            in_ol = False
        return res

    def close_blockquote():
        nonlocal in_blockquote, blockquote_lines
        res = []
        if in_blockquote:
            content = " ".join(blockquote_lines)
            res.append(f"<blockquote><p>{format_inline(content)}</p></blockquote>")
            in_blockquote = False
            blockquote_lines = []
        return res

    def format_inline(text):
        # Preserve <br> and <br/>
        text = text.replace("<br>", "__BR_TOKEN__").replace("<br/>", "__BR_TOKEN__")
        text = html.escape(text)
        text = text.replace("__BR_TOKEN__", "<br/>")

        # Inline code
        text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

        # Bold + Italic
        text = re.sub(r"\*\*\*([^*]+)\*\*\*", r"<strong><em>\1</em></strong>", text)

        # Bold
        text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)

        # Italic
        text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)

        # Math
        text = re.sub(r"\$\$([^$]+)\$\$", r'<span class="math-block">\1</span>', text)
        text = re.sub(r"\$([^$]+)\$", r'<span class="math-inline">\1</span>', text)

        return text

    def process_table(tbl_lines):
        tbl_lines = [l.strip() for l in tbl_lines if l.strip()]
        if not tbl_lines:
            return ""

        rows = []
        for line in tbl_lines:
            if not line.startswith("|") and not line.endswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(re.match(r"^:?-+:?$", c) for c in cells if c):
                continue
            rows.append(cells)

        if not rows:
            return ""

        res = ['<div class="table-container"><table>']
        header_cells = rows[0]
        res.append("<thead><tr>")
        for cell in header_cells:
            res.append(f"<th>{format_inline(cell)}</th>")
        res.append("</tr></thead>")

        if len(rows) > 1:
            res.append("<tbody>")
            for row in rows[1:]:
                res.append("<tr>")
                for cell in row:
                    res.append(f"<td>{format_inline(cell)}</td>")
                res.append("</tr>")
            res.append("</tbody>")

        res.append("</table></div>")
        return "\n".join(res)

    i = 0
    while i < len(lines):
        line = lines[i]
        trimmed = line.strip()

        # Fenced code block
        if trimmed.startswith("```"):
            if in_code_block:
                code_content = html.escape("\n".join(code_block_lines))
                html_out.append(f'<pre><code class="language-{code_block_lang}">{code_content}</code></pre>')
                in_code_block = False
                code_block_lines = []
                code_block_lang = ""
            else:
                html_out.extend(close_lists())
                html_out.extend(close_blockquote())
                in_code_block = True
                code_block_lang = trimmed[3:].strip()
                code_block_lines = []
            i += 1
            continue

        if in_code_block:
            code_block_lines.append(line)
            i += 1
            continue

        # Tables
        if trimmed.startswith("|") and trimmed.endswith("|"):
            html_out.extend(close_lists())
            html_out.extend(close_blockquote())
            table_lines.append(trimmed)
            in_table = True
            i += 1
            continue
        elif in_table:
            html_out.append(process_table(table_lines))
            table_lines = []
            in_table = False

        # Blank line
        if not trimmed:
            html_out.extend(close_lists())
            html_out.extend(close_blockquote())
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^---+$", trimmed) or re.match(r"^\*\*\*+$", trimmed):
            html_out.extend(close_lists())
            html_out.extend(close_blockquote())
            html_out.append("<hr/>")
            i += 1
            continue

        # Headings
        m = re.match(r"^(#{1,6})\s+(.*)$", trimmed)
        if m:
            html_out.extend(close_lists())
            html_out.extend(close_blockquote())
            level = len(m.group(1))
            heading_text = format_inline(m.group(2))
            heading_id = re.sub(r"[^a-zA-Z0-9]+", "-", m.group(2).lower()).strip("-")
            html_out.append(f'<h{level} id="{heading_id}">{heading_text}</h{level}>')
            i += 1
            continue

        # Blockquote
        if trimmed.startswith(">"):
            html_out.extend(close_lists())
            quote_text = trimmed.lstrip(">").strip()
            in_blockquote = True
            blockquote_lines.append(quote_text)
            i += 1
            continue
        elif in_blockquote:
            html_out.extend(close_blockquote())

        # Unordered list
        m_ul = re.match(r"^[\*\-\+]\s+(.*)$", trimmed)
        if m_ul:
            if in_ol:
                html_out.append("</ol>")
                in_ol = False
            if not in_ul:
                html_out.append("<ul>")
                in_ul = True
            html_out.append(f"<li>{format_inline(m_ul.group(1))}</li>")
            i += 1
            continue

        # Ordered list
        m_ol = re.match(r"^\d+\.\s+(.*)$", trimmed)
        if m_ol:
            if in_ul:
                html_out.append("</ul>")
                in_ul = False
            if not in_ol:
                html_out.append("<ol>")
                in_ol = True
            html_out.append(f"<li>{format_inline(m_ol.group(1))}</li>")
            i += 1
            continue

        # Regular paragraph
        html_out.extend(close_lists())
        html_out.extend(close_blockquote())
        html_out.append(f"<p>{format_inline(trimmed)}</p>")
        i += 1

    if in_table:
        html_out.append(process_table(table_lines))
    if in_code_block:
        code_content = html.escape("\n".join(code_block_lines))
        html_out.append(f'<pre><code class="language-{code_block_lang}">{code_content}</code></pre>')
    html_out.extend(close_lists())
    html_out.extend(close_blockquote())

    return "\n".join(html_out)


def compile_markdown(chapter_files, output_path):
    """Concatenate all chapters into a single markdown file."""
    print(f"Compiling Markdown manuscript to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as out_f:
        for i, filepath in enumerate(chapter_files):
            with open(filepath, "r", encoding="utf-8") as in_f:
                content = in_f.read().strip()
            out_f.write(content)
            out_f.write("\n\n")
    print(f"  ✓ Markdown created: {output_path} ({os.path.getsize(output_path):,} bytes)")


def compile_html(chapter_files, output_path, meta):
    """Compile chapters into a single standalone HTML document with book CSS."""
    print(f"Compiling HTML book to {output_path}...")
    chapters_html = []
    for f in chapter_files:
        with open(f, "r", encoding="utf-8") as in_f:
            raw = in_f.read()
        h = markdown_to_html(raw)
        basename = os.path.splitext(os.path.basename(f))[0]
        chapters_html.append(f'<section class="chapter" id="{basename}">\n{h}\n</section>\n')

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(meta['title'])}</title>
<style>
/* Base Book Styling */
@page {{
    size: 6in 9in; /* US Trade standard */
    margin: 0.8in 0.7in 0.8in 0.7in;
    @bottom-center {{
        content: counter(page);
        font-family: 'Baskerville', 'Georgia', serif;
        font-size: 9pt;
    }}
}}
@page :first {{
    @bottom-center {{ content: normal; }}
}}
body {{
    font-family: 'Baskerville', 'Georgia', 'Times New Roman', serif;
    font-size: 10.5pt;
    line-height: 1.55;
    color: #111;
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
    background: #fafafa;
}}
.chapter {{
    page-break-before: always;
    break-before: page;
    margin-bottom: 4rem;
}}
.chapter:first-of-type {{
    page-break-before: avoid;
    break-before: avoid;
}}
h1 {{
    font-size: 22pt;
    font-weight: bold;
    text-align: center;
    margin-top: 2rem;
    margin-bottom: 1.5rem;
    page-break-before: always;
    break-before: page;
    letter-spacing: -0.02em;
}}
h2 {{
    font-size: 15pt;
    font-weight: 600;
    margin-top: 2.2rem;
    margin-bottom: 0.8rem;
    border-bottom: 1px solid #ddd;
    padding-bottom: 0.3rem;
}}
h3 {{
    font-size: 12pt;
    font-weight: 600;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
}}
h4 {{
    font-size: 10.5pt;
    font-weight: 600;
    margin-top: 1.2rem;
    margin-bottom: 0.4rem;
}}
p {{
    text-align: justify;
    text-indent: 1.5em;
    margin: 0 0 0.6em 0;
}}
h1 + p, h2 + p, h3 + p, h4 + p, hr + p, blockquote + p {{
    text-indent: 0;
}}
blockquote {{
    font-style: italic;
    margin: 1.2rem 2rem;
    padding-left: 1rem;
    border-left: 3px solid #888;
    color: #444;
}}
blockquote p {{
    text-indent: 0;
}}
pre {{
    font-family: 'Courier New', Courier, monospace;
    font-size: 8.5pt;
    background: #f0f0f0;
    padding: 10px 12px;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
    white-space: pre-wrap;
    word-break: break-all;
    margin: 1.2rem 0;
    page-break-inside: avoid;
}}
code {{
    font-family: 'Courier New', monospace;
    font-size: 90%;
    background: #f4f4f4;
    padding: 1px 4px;
    border-radius: 3px;
}}
pre code {{
    background: none;
    padding: 0;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
    font-size: 9pt;
    page-break-inside: avoid;
}}
th, td {{
    border: 1px solid #bbb;
    padding: 6px 10px;
    text-align: left;
    vertical-align: top;
}}
th {{
    background: #eee;
    font-weight: bold;
}}
hr {{
    border: 0;
    border-top: 1px solid #ccc;
    margin: 2rem 0;
}}
ul, ol {{
    margin: 0.8rem 0 1rem 1.8rem;
    padding: 0;
}}
li {{
    margin-bottom: 0.35rem;
}}
.math-inline, .math-block {{
    font-family: 'Times New Roman', serif;
    font-style: italic;
}}
.math-block {{
    display: block;
    text-align: center;
    margin: 1rem 0;
}}
</style>
</head>
<body>
{"".join(chapters_html)}
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as out_f:
        out_f.write(full_html)
    print(f"  ✓ HTML created: {output_path} ({os.path.getsize(output_path):,} bytes)")
    return full_html


def compile_pdf(full_html, output_path):
    """Compile HTML into print-ready PDF using WeasyPrint."""
    if not HAS_WEASYPRINT:
        print("  ✗ Error: weasyprint is not installed. Run: pip install weasyprint")
        return False

    print(f"Compiling PDF via WeasyPrint to {output_path}...")
    doc = weasyprint.HTML(string=full_html)
    doc.write_pdf(output_path)
    print(f"  ✓ PDF created: {output_path} ({os.path.getsize(output_path):,} bytes)")
    return True


def compile_epub(chapter_files, output_path, meta):
    """Compile chapters into standard EPUB 3 / KDP-compliant eBook archive."""
    print(f"Compiling EPUB (KDP) to {output_path}...")

    chapter_data = []
    for idx, f in enumerate(chapter_files):
        with open(f, "r", encoding="utf-8") as in_f:
            raw = in_f.read()
        h = markdown_to_html(raw)
        title = os.path.splitext(os.path.basename(f))[0]
        # Clean title for TOC display
        clean_title = re.sub(r"^\d+\.\s*", "", title)
        chapter_data.append((f"chapter_{idx:02d}.xhtml", clean_title, h))

    with zipfile.ZipFile(output_path, "w") as zf:
        # 1. mimetype (must be first and uncompressed)
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)

        # 2. META-INF/container.xml
        container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""
        zf.writestr("META-INF/container.xml", container_xml, compress_type=zipfile.ZIP_DEFLATED)

        # 3. CSS
        css_content = """body {
    font-family: Georgia, 'Times New Roman', serif;
    margin: 5%;
    line-height: 1.5;
    color: #111;
}
h1, h2, h3, h4 {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    text-align: left;
}
h1 {
    font-size: 1.8em;
    margin-top: 1.5em;
    text-align: center;
}
h2 {
    font-size: 1.3em;
    margin-top: 1.2em;
    border-bottom: 1px solid #ccc;
    padding-bottom: 4px;
}
p {
    text-indent: 1.5em;
    margin: 0 0 0.5em 0;
    text-align: justify;
}
h1 + p, h2 + p, h3 + p, hr + p, blockquote + p {
    text-indent: 0;
}
blockquote {
    font-style: italic;
    margin: 1em 1.5em;
    padding-left: 1em;
    border-left: 2px solid #666;
}
pre {
    background: #f4f4f4;
    padding: 8px;
    font-size: 80%;
    overflow-x: auto;
    border: 1px solid #ddd;
    white-space: pre-wrap;
    word-break: break-all;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    font-size: 85%;
}
th, td {
    border: 1px solid #bbb;
    padding: 4px 6px;
    text-align: left;
}
th {
    background: #eee;
}
"""
        zf.writestr("OEBPS/style.css", css_content, compress_type=zipfile.ZIP_DEFLATED)

        # 4. Manifest, Spine, NAV & NCX
        manifest_items = [
            '<item id="css" href="style.css" media-type="text/css"/>',
            '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
            '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
        ]
        spine_items = []
        nav_links = []
        ncx_points = []

        for c_id, (xhtml_filename, title, content) in enumerate(chapter_data):
            item_id = f"chap_{c_id:02d}"
            manifest_items.append(f'<item id="{item_id}" href="{xhtml_filename}" media-type="application/xhtml+xml"/>')
            spine_items.append(f'<itemref idref="{item_id}"/>')
            nav_links.append(f'<li><a href="{xhtml_filename}">{html.escape(title)}</a></li>\n')
            ncx_points.append(f"""  <navPoint id="navPoint-{c_id+1}" playOrder="{c_id+1}">
    <navLabel><text>{html.escape(title)}</text></navLabel>
    <content src="{xhtml_filename}"/>
  </navPoint>""")

            xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en">
<head>
<title>{html.escape(title)}</title>
<link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
{content}
</body>
</html>"""
            zf.writestr(f"OEBPS/{xhtml_filename}", xhtml, compress_type=zipfile.ZIP_DEFLATED)

        # NAV XHTML
        nav_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en">
<head>
<title>Table of Contents</title>
<link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
<nav epub:type="toc" id="toc">
  <h1>Table of Contents</h1>
  <ol>
    {"".join(nav_links)}
  </ol>
</nav>
</body>
</html>"""
        zf.writestr("OEBPS/nav.xhtml", nav_xhtml, compress_type=zipfile.ZIP_DEFLATED)

        # NCX (EPUB 2 / Kindle compatibility)
        toc_ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head>
  <meta name="dtb:uid" content="{meta['identifier']}"/>
  <meta name="dtb:depth" content="1"/>
  <meta name="dtb:totalPageCount" content="0"/>
  <meta name="dtb:maxPageNumber" content="0"/>
</head>
<docTitle><text>{html.escape(meta['title'])}</text></docTitle>
<navMap>
{"".join(ncx_points)}
</navMap>
</ncx>"""
        zf.writestr("OEBPS/toc.ncx", toc_ncx, compress_type=zipfile.ZIP_DEFLATED)

        # content.opf
        content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="3.0">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:identifier id="BookId">{meta['identifier']}</dc:identifier>
  <dc:title>{html.escape(meta['title'])}</dc:title>
  <dc:creator>{html.escape(meta['author'])}</dc:creator>
  <dc:language>{meta['language']}</dc:language>
  <dc:publisher>{html.escape(meta['publisher'])}</dc:publisher>
  <meta property="dcterms:modified">2026-10-07T20:00:00Z</meta>
</metadata>
<manifest>
  {"".join(manifest_items)}
</manifest>
<spine toc="ncx">
  {"".join(spine_items)}
</spine>
</package>"""
        zf.writestr("OEBPS/content.opf", content_opf, compress_type=zipfile.ZIP_DEFLATED)

    print(f"  ✓ EPUB created: {output_path} ({os.path.getsize(output_path):,} bytes)")


def main():
    parser = argparse.ArgumentParser(
        description="Compile split book chapters into PDF, EPUB, HTML, or Markdown.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-f", "--format",
        choices=["all", "pdf", "epub", "html", "markdown"],
        default="all",
        help="Format to compile (default: all)"
    )
    parser.add_argument(
        "-i", "--input-dir",
        default=".",
        help="Directory containing chapter markdown files (default: .)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="./dist",
        help="Directory to save compiled files (default: ./dist)"
    )
    parser.add_argument("--title", default=BOOK_METADATA["title"], help="Book title override")
    parser.add_argument("--author", default=BOOK_METADATA["author"], help="Author override")

    args = parser.parse_args()

    meta = BOOK_METADATA.copy()
    meta["title"] = args.title
    meta["author"] = args.author

    input_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    chapter_files = get_sorted_chapter_files(input_dir)
    if not chapter_files:
        print(f"Error: No chapter markdown files found in {input_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(chapter_files)} chapter/section files in {input_dir}:")
    for cf in chapter_files:
        print(f"  • {os.path.basename(cf)}")
    print(f"\nTarget output directory: {output_dir}\n")

    base_name = "WHAT_WAS_IN_THAT_JOINT_BRO"

    # Always generate HTML if PDF or HTML or ALL is selected
    full_html = None
    if args.format in ["all", "html", "pdf"]:
        html_path = os.path.join(output_dir, f"{base_name}.html")
        full_html = compile_html(chapter_files, html_path, meta)

    if args.format in ["all", "pdf"]:
        pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
        compile_pdf(full_html, pdf_path)

    if args.format in ["all", "epub"]:
        epub_path = os.path.join(output_dir, f"{base_name}.epub")
        compile_epub(chapter_files, epub_path, meta)

    if args.format in ["all", "markdown"]:
        md_path = os.path.join(output_dir, f"{base_name}.compiled.md")
        compile_markdown(chapter_files, md_path)

    print("\n✓ Compilation complete!")


if __name__ == "__main__":
    main()

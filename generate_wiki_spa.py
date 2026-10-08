#!/usr/bin/env python3
"""
generate_wiki_spa.py
Builds a self-contained, offline-first documentation wiki SPA (dist/index.html).
No Node.js or bundlers required.
"""

import json
from pathlib import Path

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>What Was In That Joint Bro!? — The Purple Canary Docs</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <!-- Tailwind CDN for rapid glassmorphic wiki typography -->
  <script src="https://cdn.tailwindcss.com?plugins=typography"></script>
  <!-- Marked.js for fast client-side markdown rendering -->
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
            mono: ['Fira Code', 'monospace'],
          },
          colors: {
            canary: {
              300: '#fde047',
              400: '#facc15',
              500: '#eab308'
            },
            purplecore: {
              400: '#c084fc',
              500: '#a855f7',
              600: '#9333ea',
              900: '#3b0764'
            }
          }
        }
      }
    }
  </script>
  <style>
    /* Custom Scrollbar & Utility styling */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }
    .glass { background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(12px); }
    .prose pre { background-color: #090d16 !important; border: 1px solid #1e293b; }
    .prose code { color: #fde047; font-family: 'Fira Code', monospace; }
    .prose table { border-collapse: collapse; width: 100%; margin: 1.5rem 0; }
    .prose th { background-color: #1e1b4b; color: #f8fafc; padding: 0.65rem 1rem; border: 1px solid #334155; text-align: left; }
    .prose td { padding: 0.65rem 1rem; border: 1px solid #1e293b; }
    .prose tr:nth-child(even) { background-color: rgba(30, 41, 59, 0.25); }
    .prose h1, .prose h2, .prose h3 { scroll-margin-top: 5rem; }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 font-sans antialiased selection:bg-purplecore-500 selection:text-white">

  <!-- Reading Progress Bar -->
  <div id="progress-bar" class="fixed top-0 left-0 h-1 bg-gradient-to-r from-purplecore-500 to-canary-400 z-50 transition-all duration-75" style="width: 0%"></div>

  <!-- Header -->
  <header class="sticky top-0 z-40 w-full border-b border-slate-800 glass">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <button id="mobile-toggle" class="md:hidden p-2 text-slate-400 hover:text-white focus:outline-none">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>
        <div class="flex items-center gap-2.5 cursor-pointer" onclick="navigateTo(0)">
          <span class="text-2xl">🐤</span>
          <div>
            <span class="font-bold text-white tracking-wide">PURPLE CANARY</span>
            <span class="hidden sm:inline-block text-xs px-2 py-0.5 ml-2 rounded font-mono bg-purple-950 text-purple-300 border border-purple-800">PROTOCOL DOCS</span>
          </div>
        </div>
      </div>

      <!-- Quick Search Bar -->
      <div class="flex-1 max-w-md relative">
        <div class="relative">
          <input type="text" id="search-input" placeholder="Search protocol, Rf values, chemical terms... (Cmd+K)" 
            class="w-full bg-slate-900 border border-slate-800 rounded-lg py-1.5 pl-9 pr-4 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purplecore-500 focus:ring-1 focus:ring-purplecore-500 transition">
          <svg class="w-4 h-4 text-slate-500 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
        </div>
        <div id="search-results" class="hidden absolute top-full left-0 right-0 mt-2 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl max-h-80 overflow-y-auto z-50 p-2 space-y-1"></div>
      </div>

      <div class="flex items-center gap-3">
        <a href="https://tehwiz.com" target="_blank" class="hidden sm:inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-purplecore-400 font-mono transition">
          <span>tehwiz.com</span>
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
        </a>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex">
    
    <!-- Sidebar Navigation -->
    <aside id="sidebar" class="fixed md:sticky top-16 z-30 inset-y-0 left-0 w-72 md:w-64 bg-slate-950 md:bg-transparent border-r border-slate-800 p-4 shrink-0 h-[calc(100vh-4rem)] overflow-y-auto transform -translate-x-full md:translate-x-0 transition-transform duration-200 ease-in-out">
      <div class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 px-2 font-mono">Chapters</div>
      <nav id="chapter-list" class="space-y-1 text-sm font-medium"></nav>
    </aside>

    <!-- Content Workspace -->
    <main class="flex-1 min-w-0 py-8 md:px-8 lg:px-12">
      <!-- Chapter Breadcrumbs -->
      <div id="breadcrumbs" class="flex items-center gap-2 text-xs font-mono text-slate-500 mb-4">
        <span>BOOK</span>
        <span>/</span>
        <span id="crumb-active" class="text-purplecore-400">Loading...</span>
      </div>

      <!-- Markdown Article -->
      <article id="markdown-container" class="prose prose-invert prose-purple max-w-none text-slate-300 leading-relaxed"></article>

      <!-- Bottom Chapter Nav -->
      <div class="mt-16 pt-6 border-t border-slate-800 flex items-center justify-between gap-4 font-mono text-xs">
        <button id="btn-prev" onclick="stepChapter(-1)" class="px-4 py-2 rounded border border-slate-800 bg-slate-900/60 hover:bg-slate-800 text-slate-300 transition flex items-center gap-2">
          <span>←</span> <span id="prev-title">Previous</span>
        </button>
        <button id="btn-next" onclick="stepChapter(1)" class="px-4 py-2 rounded border border-slate-800 bg-slate-900/60 hover:bg-slate-800 text-purplecore-300 transition flex items-center gap-2">
          <span id="next-title">Next</span> <span>→</span>
        </button>
      </div>
    </main>

    <!-- In-Page TOC (Desktop Right Sidebar) -->
    <aside class="hidden xl:block w-56 shrink-0 py-8 pl-6 border-l border-slate-900 h-[calc(100vh-4rem)] sticky top-16 overflow-y-auto">
      <div class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 font-mono">On This Page</div>
      <nav id="in-page-toc" class="space-y-1.5 text-xs text-slate-400 font-sans"></nav>
    </aside>

  </div>

  <script>
    // Embedded Book Data
    const BOOK_DATA = {{BOOK_DATA_JSON}};

    let currentChapterIndex = 0;

    function renderNav() {
      const container = document.getElementById('chapter-list');
      container.innerHTML = '';

      BOOK_DATA.chapters.forEach((chap, idx) => {
        const btn = document.createElement('button');
        btn.className = `w-full text-left px-3 py-2 rounded-lg text-xs md:text-sm transition flex items-center justify-between ${
          idx === currentChapterIndex 
            ? 'bg-purple-950/80 text-purple-300 border border-purple-800 font-semibold' 
            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
        }`;
        btn.innerHTML = `<span class="truncate">${chap.title}</span>`;
        btn.onclick = () => {
          navigateTo(idx);
          if (window.innerWidth < 768) toggleSidebar();
        };
        container.appendChild(btn);
      });
    }

    function renderChapter(index) {
      currentChapterIndex = index;
      const chapter = BOOK_DATA.chapters[index];
      
      document.title = `${chapter.title} — What Was In That Joint Bro!?`;
      document.getElementById('crumb-active').innerText = chapter.title;

      // Render Markdown via marked.js
      const container = document.getElementById('markdown-container');
      container.innerHTML = marked.parse(chapter.markdown);

      // Render In-page headings
      renderInPageTOC(chapter.headings);

      // Render bottom navigation buttons
      const prevBtn = document.getElementById('btn-prev');
      const nextBtn = document.getElementById('btn-next');
      
      if (index > 0) {
        prevBtn.classList.remove('invisible');
        document.getElementById('prev-title').innerText = BOOK_DATA.chapters[index - 1].title;
      } else {
        prevBtn.classList.add('invisible');
      }

      if (index < BOOK_DATA.chapters.length - 1) {
        nextBtn.classList.remove('invisible');
        document.getElementById('next-title').innerText = BOOK_DATA.chapters[index + 1].title;
      } else {
        nextBtn.classList.add('invisible');
      }

      renderNav();
      window.scrollTo({ top: 0, behavior: 'smooth' });
      history.replaceState(null, '', `#${chapter.id}`);
    }

    function renderInPageTOC(headings) {
      const toc = document.getElementById('in-page-toc');
      toc.innerHTML = '';
      if (!headings || headings.length === 0) {
        toc.innerHTML = '<span class="text-slate-600">No subheadings</span>';
        return;
      }

      headings.forEach(h => {
        if (h.level > 3) return;
        const a = document.createElement('a');
        a.href = `#${h.slug}`;
        a.className = `block text-slate-400 hover:text-purplecore-400 truncate transition ${h.level === 3 ? 'pl-3 text-slate-500' : ''}`;
        a.innerText = h.title;
        toc.appendChild(a);
      });
    }

    function navigateTo(index) {
      if (index >= 0 && index < BOOK_DATA.chapters.length) {
        renderChapter(index);
      }
    }

    function stepChapter(delta) {
      navigateTo(currentChapterIndex + delta);
    }

    // Client-side instant search
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    searchInput.addEventListener('input', (e) => {
      const q = e.target.value.trim().toLowerCase();
      if (!q) {
        searchResults.classList.add('hidden');
        return;
      }

      const matches = [];
      BOOK_DATA.chapters.forEach((chap, chapIdx) => {
        const text = chap.markdown.toLowerCase();
        const foundPos = text.indexOf(q);
        if (foundPos !== -1 || chap.title.toLowerCase().includes(q)) {
          const start = Math.max(0, foundPos - 40);
          const snippet = chap.markdown.substr(start, 90).replace(/[#*`]/g, '');
          matches.push({ chapIdx, title: chap.title, snippet });
        }
      });

      if (matches.length > 0) {
        searchResults.innerHTML = matches.slice(0, 8).map(m => `
          <div onclick="navigateTo(${m.chapIdx}); searchResults.classList.add('hidden'); searchInput.value='';" 
               class="p-2 rounded hover:bg-slate-800 cursor-pointer text-xs">
            <div class="font-semibold text-purplecore-300">${m.title}</div>
            <div class="text-slate-400 truncate mt-0.5">...${m.snippet}...</div>
          </div>
        `).join('');
        searchResults.classList.remove('hidden');
      } else {
        searchResults.innerHTML = '<div class="p-2 text-xs text-slate-500">No matching text found.</div>';
        searchResults.classList.remove('hidden');
      }
    });

    // Reading progress listener
    window.addEventListener('scroll', () => {
      const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = (winScroll / height) * 100;
      document.getElementById('progress-bar').style.width = scrolled + '%';
    });

    // Mobile sidebar toggle
    const mobileBtn = document.getElementById('mobile-toggle');
    const sidebar = document.getElementById('sidebar');
    function toggleSidebar() {
      sidebar.classList.toggle('-translate-x-full');
    }
    mobileBtn.addEventListener('click', toggleSidebar);

    // Keyboard shortcuts
    window.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        searchInput.focus();
      }
      if (document.activeElement !== searchInput) {
        if (e.key === 'ArrowRight' || e.key.toLowerCase() === 'l') stepChapter(1);
        if (e.key === 'ArrowLeft' || e.key.toLowerCase() === 'h') stepChapter(-1);
      }
    });

    // Hash router boot
    window.addEventListener('DOMContentLoaded', () => {
      const hash = window.location.hash.replace('#', '');
      const initialIdx = BOOK_DATA.chapters.findIndex(c => c.id === hash);
      renderChapter(initialIdx !== -1 ? initialIdx : 0);
    });
  </script>
</body>
</html>
"""

def generate_spa():
    root = Path(__file__).parent.resolve()
    dist = root / "dist"
    json_path = dist / "book_data.json"

    if not json_path.exists():
        print("[!] book_data.json not found in dist/. Running compile_book.py first...")
        from compile_book import compile_manuscript
        compile_manuscript()

    raw_json = json_path.read_text(encoding="utf-8")
    html_output = HTML_TEMPLATE.replace("{{BOOK_DATA_JSON}}", raw_json)

    out_file = dist / "index.html"
    out_file.write_text(html_output, encoding="utf-8")
    print(f"[✓] Standalone Wiki SPA successfully generated at: {out_file}")

if __name__ == "__main__":
    generate_spa()

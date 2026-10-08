#!/usr/bin/env python3
"""
generate_wiki_spa.py
Builds a self-contained, offline-first documentation wiki SPA (dist/index.html).
Features a full-height, left-to-right paginated e-reader with page flipping.
No Node.js or bundlers required.
"""

import json
from pathlib import Path

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" class="dark h-full">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>What Was In That Joint Bro!? — The Purple Canary Protocol</title>
  <link rel="icon" type="image/png" href="https://i.ibb.co/C3Jc6MKH/Gemini-Generated-Image-p4r67dp4r67dp4r6-removebg-preview.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <!-- Tailwind CDN for rapid glassmorphic wiki typography -->
  <script src="https://cdn.tailwindcss.com?plugins=typography"></script>
  <!-- Marked.js for fast client-side markdown rendering -->
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <!-- KaTeX for math equations and Greek symbols ($R_f = 0.00$, $\alpha$, $\beta$, etc.) -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
  <script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
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
    /* Full height fixed viewport application */
    html, body {
      height: 100%;
      overflow: hidden;
      margin: 0;
      padding: 0;
      background-color: #020617;
    }

    /* Custom Scrollbar & Utility styling */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #0b0f19; }
    ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #334155; }
    .glass { background: rgba(11, 15, 25, 0.85); backdrop-filter: blur(16px); }

    /* Dynamic Reader Typography scaling */
    :root {
      --reader-font-size: 16px;
      --reader-line-height: 1.75;
    }

    /* Outer wrapper */
    #book-scroller {
      width: 100%;
      height: 100%;
      position: relative;
      overflow: hidden;
    }

    /* Multi-column paginated e-reader layout on markdown container */
    #markdown-container {
      font-size: var(--reader-font-size) !important;
      line-height: var(--reader-line-height) !important;
      width: 100% !important;
      height: 100% !important;
      overflow-x: auto !important;
      overflow-y: hidden !important;
      column-fill: auto !important;
      column-gap: 0px !important;
      scroll-behavior: smooth;
      -webkit-overflow-scrolling: touch;
      user-select: text;

      /* Clean reader scrollbar styling */
      scrollbar-width: thin;
      scrollbar-color: #334155 #0b0f19;
    }

    #markdown-container::-webkit-scrollbar {
      height: 6px;
    }
    #markdown-container::-webkit-scrollbar-track {
      background: #090d16;
      border-radius: 4px;
    }
    #markdown-container::-webkit-scrollbar-thumb {
      background: #334155;
      border-radius: 4px;
    }
    #markdown-container::-webkit-scrollbar-thumb:hover {
      background: #a855f7;
    }

    #markdown-container p,
    #markdown-container li,
    #markdown-container blockquote,
    #markdown-container table td,
    #markdown-container table th {
      font-size: 1em !important;
      line-height: inherit !important;
    }

    #markdown-container h1 {
      font-size: 2.15em !important;
      line-height: 1.25 !important;
      break-after: avoid;
      break-inside: avoid;
      margin-top: 0.2em;
      margin-bottom: 0.6em;
      color: #f8fafc;
    }

    #markdown-container h2 {
      font-size: 1.55em !important;
      line-height: 1.35 !important;
      break-after: avoid;
      break-inside: avoid;
      margin-top: 0.8em;
      margin-bottom: 0.5em;
      color: #e2e8f0;
    }

    #markdown-container h3 {
      font-size: 1.25em !important;
      line-height: 1.4 !important;
      break-after: avoid;
      break-inside: avoid;
      margin-top: 0.7em;
      margin-bottom: 0.4em;
      color: #cbd5e1;
    }

    #markdown-container h4 {
      font-size: 1.1em !important;
      line-height: 1.5 !important;
      break-after: avoid;
      break-inside: avoid;
    }

    #markdown-container p {
      margin-bottom: 1em;
      color: #cbd5e1;
    }

    #markdown-container ul, 
    #markdown-container ol {
      margin-bottom: 1em;
      padding-left: 1.5em;
      break-inside: avoid;
    }

    #markdown-container li {
      margin-bottom: 0.35em;
    }

    #markdown-container pre {
      background-color: #070a12 !important;
      border: 1px solid #1e293b;
      border-radius: 0.5rem;
      padding: 0.75rem 1rem;
      margin: 0.8rem 0;
      max-height: 55vh;
      overflow: auto;
      break-inside: avoid;
    }

    #markdown-container code {
      color: #fde047;
      font-family: 'Fira Code', monospace;
    }

    #markdown-container pre code {
      font-size: 0.875em !important;
      line-height: 1.5 !important;
    }

    #markdown-container blockquote {
      border-left: 3px solid #a855f7;
      padding-left: 1rem;
      margin: 1rem 0;
      color: #94a3b8;
      font-style: italic;
      break-inside: avoid;
    }

    #markdown-container table {
      border-collapse: collapse;
      width: 100%;
      margin: 1rem 0;
      max-width: 100%;
      display: block;
      overflow-x: auto;
      break-inside: avoid;
    }

    #markdown-container th {
      background-color: #1e1b4b;
      color: #f8fafc;
      padding: 0.5rem 0.75rem;
      border: 1px solid #334155;
      text-align: left;
    }

    #markdown-container td {
      padding: 0.5rem 0.75rem;
      border: 1px solid #1e293b;
    }

    #markdown-container tr:nth-child(even) {
      background-color: rgba(30, 41, 59, 0.25);
    }

    #markdown-container img {
      max-width: 100%;
      max-height: 60vh;
      object-fit: contain;
      border-radius: 0.5rem;
      margin: 0.8rem auto;
      break-inside: avoid;
    }

    /* Flip navigation arrow pulses */
    .flip-btn {
      transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .flip-btn:hover {
      transform: scale(1.08);
    }
    .flip-btn:active {
      transform: scale(0.95);
    }

    /* Glossary Term Linking & Tooltips */
    abbr.glossary-abbr {
      text-decoration-line: underline;
      text-decoration-style: dotted;
      text-decoration-color: #a855f7;
      text-underline-offset: 3px;
      cursor: help;
      transition: color 0.15s ease, text-decoration-color 0.15s ease;
    }

    .glossary-term-link {
      color: inherit;
      text-decoration: none;
      border-radius: 2px;
      transition: background-color 0.15s ease;
    }

    .glossary-term-link:hover {
      text-decoration: none;
      background-color: rgba(168, 85, 247, 0.15);
    }

    .glossary-term-link:hover abbr.glossary-abbr {
      color: #e9d5ff;
      text-decoration-color: #facc15;
    }

    .glossary-anchor {
      color: inherit;
      text-decoration: none;
      border-bottom: 1px dashed #64748b;
      transition: all 0.15s ease;
    }

    .glossary-anchor:hover {
      color: #facc15;
      border-bottom-color: #facc15;
    }

    @keyframes glossaryTargetGlow {
      0% {
        background-color: rgba(168, 85, 247, 0.65);
        box-shadow: 0 0 16px rgba(168, 85, 247, 0.7);
        border-radius: 4px;
      }
      50% {
        background-color: rgba(250, 204, 21, 0.45);
        box-shadow: 0 0 12px rgba(250, 204, 21, 0.55);
        border-radius: 4px;
      }
      100% {
        background-color: transparent;
        box-shadow: none;
      }
    }

    .glossary-target-highlight {
      animation: glossaryTargetGlow 2.8s ease-out;
      display: inline-block;
    }
  </style>
</head>
<body class="h-full bg-slate-950 text-slate-100 font-sans antialiased selection:bg-purplecore-500 selection:text-white flex flex-col">

  <!-- Top Global Reading Progress Bar -->
  <div id="progress-bar" class="fixed top-0 left-0 h-1 bg-gradient-to-r from-purplecore-500 via-fuchsia-500 to-canary-400 z-50 transition-all duration-150 shadow-sm" style="width: 0%"></div>

  <!-- Header Navbar -->
  <header class="h-16 w-full border-b border-slate-800/90 glass shrink-0 z-40">
    <div class="h-full px-4 sm:px-6 flex items-center justify-between gap-3 sm:gap-4">
      
      <!-- Brand & Sidebar Toggle -->
      <div class="flex items-center gap-3">
        <button id="sidebar-toggle" aria-label="Toggle Table of Contents" title="Toggle Table of Contents (T)" class="p-2 text-slate-400 hover:text-white hover:bg-slate-800/70 rounded-lg transition focus:outline-none">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>

        <div class="flex items-center gap-2.5 cursor-pointer select-none group" onclick="navigateTo(0, 0)">
          <img src="https://i.ibb.co/C3Jc6MKH/Gemini-Generated-Image-p4r67dp4r67dp4r6-removebg-preview.png" onerror="this.onerror=null; this.src='logo.png';" alt="Purple Canary Logo" class="h-9 w-9 sm:h-10 sm:w-10 object-contain shrink-0 drop-shadow group-hover:scale-105 transition-transform duration-200">
          <div>
            <span class="font-bold text-white tracking-wide text-sm sm:text-base">PURPLE CANARY</span>
            <span class="hidden sm:inline-block text-xs px-2 py-0.5 ml-2 rounded font-mono bg-purple-950 text-purple-300 border border-purple-800">E-READER</span>
          </div>
        </div>
      </div>

      <!-- Quick Search Bar -->
      <div class="flex-1 max-w-xs md:max-w-md relative">
        <div class="relative">
          <input type="text" id="search-input" placeholder="Search book, Rf values, SOPs... (Cmd+K)" 
            class="w-full bg-slate-900 border border-slate-800 rounded-lg py-1.5 pl-9 pr-4 text-xs sm:text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purplecore-500 focus:ring-1 focus:ring-purplecore-500 transition">
          <svg class="w-4 h-4 text-slate-500 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
        </div>
        <div id="search-results" class="hidden absolute top-full left-0 right-0 mt-2 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl max-h-80 overflow-y-auto z-50 p-2 space-y-1"></div>
      </div>

      <!-- Right Header Actions: Reading Stats & Text Controls -->
      <div class="flex items-center gap-2 sm:gap-3">
        <!-- Live Header Reading Time Stat -->
        <div id="header-reading-stat" class="hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900/90 border border-slate-800 text-xs font-mono text-purple-300">
          <span id="header-stat-text">Loading...</span>
        </div>

        <!-- Text Size Controls (Bigger / Smaller) -->
        <div class="flex items-center bg-slate-900/90 border border-slate-800 rounded-lg p-0.5 text-xs text-slate-300 shadow-sm" role="group" aria-label="Text size controls">
          <button id="font-dec-btn" title="Decrease font size (Alt -)" aria-label="Decrease font size" class="px-2 py-1 hover:text-white hover:bg-slate-800 active:bg-slate-700 rounded transition font-semibold disabled:opacity-30 disabled:cursor-not-allowed">
            <span class="text-xs">A−</span>
          </button>
          <button id="font-reset-btn" title="Reset font size to 100% (Alt 0)" aria-label="Reset font size" class="px-1.5 py-1 text-[11px] font-mono text-slate-400 hover:text-purplecore-300 hover:bg-slate-800 active:bg-slate-700 rounded transition">
            <span id="font-size-label">100%</span>
          </button>
          <button id="font-inc-btn" title="Increase font size (Alt +)" aria-label="Increase font size" class="px-2 py-1 hover:text-white hover:bg-slate-800 active:bg-slate-700 rounded transition font-semibold disabled:opacity-30 disabled:cursor-not-allowed">
            <span class="text-xs">A+</span>
          </button>
        </div>
      </div>
    </div>
  </header>

  <!-- Full-Height App Body -->
  <div class="flex-1 flex min-h-0 relative overflow-hidden">
    
    <!-- Left Sidebar: Chapter List (Collapsible) -->
    <aside id="sidebar" class="w-72 md:w-80 shrink-0 bg-slate-950/95 border-r border-slate-800/90 flex flex-col h-full overflow-hidden transition-all duration-200 z-30 absolute md:static inset-y-0 left-0 transform -translate-x-full md:translate-x-0">
      <div class="p-3 border-b border-slate-800 flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono">
        <span>Table of Contents</span>
        <button id="sidebar-close" class="md:hidden p-1 text-slate-400 hover:text-white">✕</button>
      </div>
      <nav id="chapter-list" class="flex-1 overflow-y-auto p-2 space-y-1 text-xs md:text-sm"></nav>
      <div class="p-3 border-t border-slate-800/80 bg-slate-950/90 shrink-0">
        <a href="https://tehwiz.com" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-purplecore-300 font-mono transition">
          <span>A TehWiz Production.</span>
          <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
        </a>
      </div>
    </aside>

    <!-- Main Reader Workspace -->
    <main class="flex-1 min-w-0 h-full flex flex-col bg-slate-950 relative overflow-hidden">
      
      <!-- Reader Top Bar: Breadcrumbs, Section Dropdown, Page Minutes -->
      <div class="h-13 px-4 sm:px-6 py-2.5 border-b border-slate-800/80 bg-slate-900/40 backdrop-blur-md flex items-center justify-between gap-3 shrink-0">
        
        <!-- Chapter Breadcrumb -->
        <div class="flex items-center gap-2 min-w-0 font-mono text-xs">
          <span class="text-slate-400 shrink-0 inline-flex items-center" title="Book">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
          </span>
          <span id="crumb-active" class="text-purplecore-300 font-medium truncate max-w-[200px] sm:max-w-md md:max-w-lg">Title</span>
        </div>

        <!-- Reading Time -->
        <div class="flex items-center gap-1.5 text-canary-400 font-mono text-xs shrink-0">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          <span id="reading-time-badge">~0m</span>
        </div>
      </div>

      <!-- Paginated Book Viewport Frame -->
      <div id="reader-viewport-frame" class="flex-1 min-h-0 relative flex items-center justify-center p-3 sm:p-5 lg:p-6 overflow-hidden">
        
        <!-- Left Page Flip Floating Arrow -->
        <button id="btn-flip-prev" onclick="flipPage(-1)" aria-label="Previous Page" title="Previous Page (← or Swipe Right)" class="flip-btn absolute left-2 sm:left-4 z-20 p-2.5 sm:p-3 rounded-full bg-slate-900/90 hover:bg-slate-800 text-slate-300 hover:text-purplecore-300 border border-slate-700/80 shadow-2xl backdrop-blur focus:outline-none disabled:opacity-20 disabled:cursor-not-allowed">
          <svg class="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/></svg>
        </button>

        <!-- Centered Paginated Book Page Container -->
        <div class="w-full max-w-4xl h-full rounded-2xl bg-slate-900/40 border border-slate-800/80 px-6 sm:px-12 py-6 sm:py-8 shadow-2xl relative overflow-hidden flex flex-col">
          
          <!-- Inner Multi-Column Scroller -->
          <div id="book-scroller" class="flex-1 min-h-0 w-full">
            <article id="markdown-container" class="prose prose-invert prose-purple max-w-none text-slate-300 leading-relaxed"></article>
          </div>
          
        </div>

        <!-- Right Page Flip Floating Arrow -->
        <button id="btn-flip-next" onclick="flipPage(1)" aria-label="Next Page" title="Next Page (→ or Swipe Left)" class="flip-btn absolute right-2 sm:right-4 z-20 p-2.5 sm:p-3 rounded-full bg-slate-900/90 hover:bg-slate-800 text-slate-300 hover:text-purplecore-300 border border-slate-700/80 shadow-2xl backdrop-blur focus:outline-none disabled:opacity-20 disabled:cursor-not-allowed">
          <svg class="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/></svg>
        </button>

      </div>

      <!-- Bottom Reader Controller Bar -->
      <footer id="reader-footer" class="h-13 px-4 sm:px-6 py-2 border-t border-slate-800/80 bg-slate-900/60 backdrop-blur-md flex items-center justify-between gap-2 shrink-0 font-mono text-xs">
        
        <!-- Prev Chapter Button -->
        <button id="btn-prev-chap" onclick="stepChapter(-1)" class="px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 hover:bg-slate-800 text-slate-300 transition flex items-center gap-1.5 text-xs truncate max-w-[130px] sm:max-w-[200px]">
          <span>←</span>
          <span id="prev-chap-label" class="truncate hidden sm:inline">Prev Chapter</span>
        </button>

        <!-- Center Page Turner & Counter Controls -->
        <div class="flex items-center gap-2 sm:gap-3">
          <button onclick="flipPage(-1)" class="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition" title="Previous Page (←)">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
          </button>

          <span id="page-counter-label" class="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-purplecore-300 font-semibold text-[11px] sm:text-xs">
            Page 1 of 1
          </span>

          <button onclick="flipPage(1)" class="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition" title="Next Page (→ or Space)">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
          </button>
        </div>

        <!-- Next Chapter Button -->
        <button id="btn-next-chap" onclick="stepChapter(1)" class="px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 hover:bg-slate-800 text-purplecore-300 transition flex items-center gap-1.5 text-xs truncate max-w-[130px] sm:max-w-[200px]">
          <span id="next-chap-label" class="truncate hidden sm:inline">Next Chapter</span>
          <span>→</span>
        </button>

      </footer>

    </main>

  </div>

  <script>
    // Embedded Book Data
    const BOOK_DATA = {{BOOK_DATA_JSON}};

    let currentChapterIndex = 0;
    let currentPageIndex = 0;
    let totalPagesInChapter = 1;

    // Font Scaling System (Bigger / Smaller Controls)
    const FONT_SCALES = [
      { label: '80%', px: 13 },
      { label: '90%', px: 14.5 },
      { label: '100%', px: 16 },
      { label: '115%', px: 18.5 },
      { label: '130%', px: 21 },
      { label: '145%', px: 23 },
      { label: '160%', px: 25.5 },
    ];
    let currentFontScaleIndex = 2; // Default 100%

    function applyFontSize(index) {
      const container = document.getElementById('markdown-container');
      const oldFraction = totalPagesInChapter > 1 ? (currentPageIndex / (totalPagesInChapter - 1)) : 0;
      currentFontScaleIndex = Math.max(0, Math.min(FONT_SCALES.length - 1, index));
      const scale = FONT_SCALES[currentFontScaleIndex];
      
      document.documentElement.style.setProperty('--reader-font-size', `${scale.px}px`);
      if (container) {
        container.style.setProperty('--reader-font-size', `${scale.px}px`);
        void container.offsetHeight; // Force immediate layout reflow
      }

      const label = document.getElementById('font-size-label');
      if (label) label.innerText = scale.label;

      const decBtn = document.getElementById('font-dec-btn');
      const incBtn = document.getElementById('font-inc-btn');
      if (decBtn) decBtn.disabled = (currentFontScaleIndex === 0);
      if (incBtn) incBtn.disabled = (currentFontScaleIndex === FONT_SCALES.length - 1);

      try {
        localStorage.setItem('purple_canary_font_scale_idx', currentFontScaleIndex);
      } catch (e) {}

      // Recalculate pagination immediately
      updatePagination(true, oldFraction);

      // And follow up on the next frame to catch any subpixel font metric rasterization
      requestAnimationFrame(() => {
        updatePagination(true, oldFraction);
      });
    }

    // Set of chapter indices whose sections are currently expanded/spoiled
    const expandedChapters = new Set([0]);

    // Set of Part names that are currently expanded/spoiled
    const expandedParts = new Set(['PART ONE: FOR EVERYONE', 'PART TWO: FOR HARM-REDUCTION AGENCIES']);

    function toggleChapterExpand(idx, e) {
      if (e) e.stopPropagation();
      if (expandedChapters.has(idx)) {
        expandedChapters.delete(idx);
      } else {
        expandedChapters.add(idx);
      }
      renderNav();
    }

    function togglePartExpand(partName, e) {
      if (e) e.stopPropagation();
      if (expandedParts.has(partName)) {
        expandedParts.delete(partName);
      } else {
        expandedParts.add(partName);
      }
      renderNav();
    }

    function navigateToSection(chapIdx, slug) {
      const chap = BOOK_DATA.chapters[chapIdx];
      if (chap && chap.part) expandedParts.add(chap.part);
      if (chapIdx === currentChapterIndex) {
        jumpToHeading(slug);
      } else {
        expandedChapters.add(chapIdx);
        navigateTo(chapIdx, slug);
      }
      if (window.innerWidth < 768) closeSidebar();
    }

    function createChapterNavItem(chap, idx) {
      const isCurrent = (idx === currentChapterIndex);
      const isExpanded = expandedChapters.has(idx);

      // Filter sections: all level 2 and level 3 headings
      const sections = (chap.headings || []).filter(h => h.level > 1 || (h.title !== chap.title));

      const itemContainer = document.createElement('div');
      itemContainer.className = 'rounded-lg overflow-hidden transition';

      // Chapter Header Item
      const headerRow = document.createElement('div');
      headerRow.className = `w-full px-2 py-1.5 rounded-lg text-xs md:text-sm transition flex items-center justify-between select-none cursor-pointer group ${
        isCurrent 
          ? 'bg-purple-950/80 text-purple-200 border border-purple-800/90 font-semibold' 
          : 'text-slate-300 hover:text-white hover:bg-slate-900/60'
      }`;

      // Left Container: Chevron button + Chapter Title
      const leftBox = document.createElement('div');
      leftBox.className = 'flex items-center gap-1.5 min-w-0 w-full';

      if (sections.length > 0) {
        const chevronBtn = document.createElement('button');
        chevronBtn.className = 'p-1 rounded hover:bg-slate-800 text-slate-500 hover:text-purplecore-300 transition shrink-0';
        chevronBtn.title = isExpanded ? 'Hide sections' : 'Show sections';
        chevronBtn.innerHTML = `
          <svg class="w-3.5 h-3.5 transition-transform duration-200 ${isExpanded ? 'rotate-90 text-purplecore-400' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        `;
        chevronBtn.onclick = (e) => toggleChapterExpand(idx, e);
        leftBox.appendChild(chevronBtn);
      } else {
        const spacer = document.createElement('span');
        spacer.className = 'w-4 shrink-0';
        leftBox.appendChild(spacer);
      }

      const titleSpan = document.createElement('span');
      titleSpan.className = 'truncate';
      titleSpan.innerText = chap.title;
      leftBox.appendChild(titleSpan);

      headerRow.appendChild(leftBox);

      // Click row navigates to chapter & expands its sections
      headerRow.onclick = (e) => {
        expandedChapters.add(idx);
        if (chap.part) expandedParts.add(chap.part);
        navigateTo(idx, 0);
        if (window.innerWidth < 768) closeSidebar();
      };

      itemContainer.appendChild(headerRow);

      // Spoilable Sections Dropdown List
      if (sections.length > 0 && isExpanded) {
        const secList = document.createElement('div');
        secList.className = 'ml-5 pl-2 my-1 border-l border-slate-800 space-y-0.5';

        sections.forEach(sec => {
          const secBtn = document.createElement('button');
          secBtn.className = `w-full text-left py-1 px-1.5 rounded text-[11px] text-slate-400 hover:text-purplecore-300 hover:bg-slate-900/80 transition truncate block ${
            sec.level === 3 ? 'pl-3 text-slate-500 text-[10.5px]' : ''
          }`;
          secBtn.title = sec.title;
          secBtn.innerText = sec.title;
          secBtn.onclick = (e) => {
            e.stopPropagation();
            navigateToSection(idx, sec.slug);
          };
          secList.appendChild(secBtn);
        });

        itemContainer.appendChild(secList);
      }

      return itemContainer;
    }

    // Sidebar navigation rendering with collapsible Parts and spoilable chapter sections
    function renderNav() {
      const container = document.getElementById('chapter-list');
      container.innerHTML = '';

      let currentPartName = null;
      let currentPartChaptersContainer = null;

      BOOK_DATA.chapters.forEach((chap, idx) => {
        const partName = chap.part || null;

        if (partName !== currentPartName) {
          currentPartName = partName;

          if (partName) {
            // New Part container
            const partGroup = document.createElement('div');
            partGroup.className = 'pt-2 pb-0.5 space-y-1';

            const isPartExpanded = expandedParts.has(partName);

            const partHeader = document.createElement('div');
            partHeader.role = 'button';
            partHeader.tabIndex = 0;
            partHeader.className = 'w-full flex items-center justify-between px-2 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider text-purplecore-400 hover:text-purplecore-300 hover:bg-slate-900/70 transition select-none cursor-pointer group';
            partHeader.innerHTML = `
              <div class="flex items-center gap-1.5 min-w-0">
                <svg class="w-3.5 h-3.5 transition-transform duration-200 shrink-0 ${isPartExpanded ? 'rotate-90 text-purplecore-400' : 'text-slate-500'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
                <span class="truncate">${partName}</span>
              </div>
            `;
            partHeader.onclick = (e) => togglePartExpand(partName, e);
            partHeader.onkeydown = (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                togglePartExpand(partName, e);
              }
            };
            partGroup.appendChild(partHeader);

            currentPartChaptersContainer = document.createElement('div');
            currentPartChaptersContainer.className = `pl-1.5 border-l border-slate-800/80 ml-2 space-y-1 ${isPartExpanded ? '' : 'hidden'}`;
            partGroup.appendChild(currentPartChaptersContainer);

            container.appendChild(partGroup);
          } else {
            currentPartChaptersContainer = null;
          }
        }

        const chapterItem = createChapterNavItem(chap, idx);
        if (currentPartChaptersContainer) {
          currentPartChaptersContainer.appendChild(chapterItem);
        } else {
          container.appendChild(chapterItem);
        }
      });
    }

    // Glossary Terms Data & Auto-Annotation System
    const GLOSSARY_TERMS = [
      // Multi-word compound terms (matched first)
      { pattern: 'Normal-Phase Chromatography', slug: 'term-normal-phase-chromatography', abbr: 'Normal-Phase Chromatography', def: 'Polar stationary phase (paper) paired with non-polar mobile phase (terpene).' },
      { pattern: 'Capillary Action', slug: 'term-capillary-action', abbr: 'Capillary Action', def: 'Liquid creeping upward through porous fibers against gravity due to surface tension.' },
      { pattern: 'Dielectric Constant', slug: 'term-dielectric-constant', abbr: 'Dielectric Constant (ε)', def: 'Measure of solvent polarity; non-polar D-limonene exhibits ε ≈ 2.3.' },
      { pattern: 'Eluotropic Strength', slug: 'term-eluotropic-strength', abbr: 'Eluotropic Strength', def: 'Thermodynamic ability of solvent to desorb solutes and carry them upward.' },
      { pattern: 'False Negatives?', slug: 'term-false-negative', abbr: 'False Negative', def: 'Analytical error where test fails to detect a dangerous compound actually present.' },
      { pattern: 'False Positives?', slug: 'term-false-positive', abbr: 'False Positive', def: 'Analytical error where test flags an adulterant when sample is actually benign.' },
      { pattern: 'Fentanyl Test Strips?', slug: 'term-fts', abbr: 'Fentanyl Test Strip (FTS)', def: 'Rapid lateral flow immunoassay detecting trace nanogram concentrations of fentanyl.' },
      { pattern: 'Fluorescence Quenching', slug: 'term-fluorescence-quenching', abbr: 'Fluorescence Quenching', def: 'Compound absorbs UV without glowing, appearing as dark shadow band.' },
      { pattern: 'Forensic Parity', slug: 'term-forensic-parity', abbr: 'Forensic Parity', def: 'Principle that individuals deserve equal access to chemical truth about what enters their bodies.' },
      { pattern: 'Good Samaritan (?:Laws|Acts?)', slug: 'term-good-samaritan-laws', abbr: 'Good Samaritan Laws', def: 'Statutes providing legal immunity from drug possession arrests for calling 911 in an overdose.' },
      { pattern: 'Indazole-3-Carboxamides', slug: 'term-indazole-3-carboxamides', abbr: 'Indazole-3-Carboxamides', def: 'Potent class of synthetic cannabinoid receptor agonists lacking phenolic hydroxyl groups.' },
      { pattern: 'Keto-Enol Tautomerism', slug: 'term-keto-enol-tautomerism', abbr: 'Keto-Enol Tautomerism', def: 'Equilibrium interconverting between ketone and enol structural isomers in curcumin.' },
      { pattern: 'Matrix Masking', slug: 'term-matrix-masking', abbr: 'Matrix Masking', def: 'Heavy plant waxes, tars, or unrefined oils physically trapping trace adulterants.' },
      { pattern: 'Mobile Phase', slug: 'term-mobile-phase', abbr: 'Mobile Phase', def: 'Moving carrier solvent (95.5% D-Limonene : 0.5% Curcumin) ascending the strip.' },
      { pattern: 'Presumptive Testing', slug: 'term-presumptive-testing', abbr: 'Presumptive Testing', def: 'Rapid screening methods indicating probable presence or absence of compound classes.' },
      { pattern: 'Retention Factors?', slug: 'term-rf', abbr: 'Retention Factor (Rf)', def: 'Decimal fraction describing migration distance relative to solvent front (d_analyte / d_solvent).' },
      { pattern: 'Solvent Front', slug: 'term-solvent-front', abbr: 'Solvent Front', def: 'Highest physical boundary line reached by migrating developer (Rf = 1.00).' },
      { pattern: 'Stationary Phase', slug: 'term-stationary-phase', abbr: 'Stationary Phase', def: 'Porous solid matrix (Whatman Grade 1 cellulose paper) providing resistance during migration.' },
      { pattern: 'Vitamin E Acetate', slug: 'term-vitamin-e-acetate', abbr: 'Vitamin E Acetate', def: 'Thick synthetic ester cutting agent implicated in EVALI lung injuries.' },
      { pattern: 'Whatman Grade 1(?: Cellulose)?', slug: 'term-whatman-grade-1', abbr: 'Whatman Grade 1 Cellulose', def: 'Pure binder-free cotton cellulose filter paper used as standardized stationary phase.' },
      { pattern: 'Medium-Chain Triglycerides', slug: 'term-mct', abbr: 'Medium-Chain Triglycerides (MCT)', def: 'Bulking lipids made of caprylic and capric fatty acids; illicit vape cutting agent.' },
      { pattern: 'Molecular Polar Surface Area', slug: 'term-psa', abbr: 'Molecular Polar Surface Area (PSA)', def: 'Surface area of polar atoms governing hydrogen-bonding capture on cellulose.' },
      { pattern: 'Limit of Detection', slug: 'term-lod', abbr: 'Limit of Detection (LOD)', def: 'Lowest concentration reliably distinguishable from background noise.' },

      // Abbreviations and Acronyms (case-sensitive)
      { pattern: 'FTIR', slug: 'term-ftir', abbr: 'FTIR (Fourier-Transform Infrared Spectroscopy)', def: 'Confirmatory optical technology measuring molecular infrared absorption spectrum.', caseSensitive: true },
      { pattern: 'GC-MS', slug: 'term-gc-ms', abbr: 'GC-MS (Gas Chromatography-Mass Spectrometry)', def: 'Laboratory gold standard for confirmatory drug testing; vaporizes, separates, and fragments molecules.', caseSensitive: true },
      { pattern: 'HPLC', slug: 'term-hplc', abbr: 'HPLC (High-Performance Liquid Chromatography)', def: 'Confirmatory laboratory instrument pumping liquid solvent under high pressure to separate compounds.', caseSensitive: true },
      { pattern: 'CBD', slug: 'term-cbd', abbr: 'CBD (Cannabidiol)', def: 'Non-intoxicating phytocannabinoid; migrates at Rf = 0.42-0.48 in Purple Canary.', caseSensitive: true },
      { pattern: 'CBN', slug: 'term-cbn', abbr: 'CBN (Cannabinol)', def: 'Oxidized degradation product of THC; strongly retarded to Rf = 0.34-0.40.', caseSensitive: true },
      { pattern: '(?:\\bDelta-9|Δ9)[ -]?THC', slug: 'term-thc', abbr: 'Δ9-THC (Delta-9-Tetrahydrocannabinol)', def: 'Primary psychoactive cannabinoid in cannabis; migrates at Rf = 0.52-0.58.', caseSensitive: true, isRawRegex: true },
      { pattern: 'THC', slug: 'term-thc', abbr: 'THC (Tetrahydrocannabinol)', def: 'Primary psychoactive cannabinoid in cannabis; migrates at Rf = 0.52-0.58 in Purple Canary.', caseSensitive: true },
      { pattern: 'SCRAs?', slug: 'term-scra', abbr: 'SCRA (Synthetic Cannabinoid Receptor Agonist)', def: 'Potent lab-synthesized research chemicals engineered to bind aggressively to CB1 receptors.', caseSensitive: true },
      { pattern: 'FTS', slug: 'term-fts', abbr: 'FTS (Fentanyl Test Strip)', def: 'Rapid lateral flow immunoassay detecting trace nanogram concentrations of fentanyl.', caseSensitive: true },
      { pattern: 'LOD', slug: 'term-lod', abbr: 'LOD (Limit of Detection)', def: 'Lowest physical concentration reliably distinguishable from background noise.', caseSensitive: true },
      { pattern: 'PSA', slug: 'term-psa', abbr: 'PSA (Molecular Polar Surface Area)', def: 'Surface area of polar atoms governing hydrogen-bonding capture on cellulose.', caseSensitive: true },
      { pattern: 'MCT(?: Oil)?', slug: 'term-mct', abbr: 'MCT (Medium-Chain Triglycerides)', def: 'Bulking lipids from caprylic and capric fatty acids; illicit vape cutting agent.', caseSensitive: true },
      { pattern: 'EVALI', slug: 'term-evali', abbr: 'EVALI (E-cigarette or Vaping Use-Associated Lung Injury)', def: 'Severe pulmonary injury outbreak linked to toxic pyrolysis of Vitamin E Acetate.', caseSensitive: true },
      { pattern: 'SOP', slug: 'term-sop', abbr: 'SOP (Standard Operating Procedure)', def: 'Standardized field protocol sequential operating instructions.', caseSensitive: true },
      { pattern: 'CLIA', slug: 'term-clia', abbr: 'CLIA (Clinical Laboratory Improvement Amendments)', def: 'Federal regulatory standards for laboratory testing; field harm-reduction testing is CLIA-exempt.', caseSensitive: true },
      { pattern: 'UNODC', slug: 'term-unodc', abbr: 'UNODC (United Nations Office on Drugs and Crime)', def: 'Publisher of international laboratory analytical manuals for forensic drug identification.', caseSensitive: true },

      // Distinct single terms
      { pattern: 'Adulterants?', slug: 'term-adulterant', abbr: 'Adulterant', def: 'Foreign unlisted agent added to mimic potency, cut costs, or stretch supply weight.' },
      { pattern: 'Cannabidiol', slug: 'term-cbd', abbr: 'Cannabidiol (CBD)', def: 'Non-intoxicating phytocannabinoid featuring open resorcinol ring.' },
      { pattern: 'Cannabinol', slug: 'term-cbn', abbr: 'Cannabinol (CBN)', def: 'Oxidized, fully aromatized degradation product of THC.' },
      { pattern: 'Chromatography', slug: 'term-chromatography', abbr: 'Chromatography', def: 'Physical separation of a mixture through stationary phase using mobile solvent.' },
      { pattern: 'Colorimetry', slug: 'term-colorimetry', abbr: 'Colorimetry', def: 'Quantitative profiling of wavelength, shade, and color saturation (RGB vectors).' },
      { pattern: 'Curcumin', slug: 'term-curcumin', abbr: 'Curcumin', def: 'Primary active polyphenolic in turmeric; indicator dye & natural fluorophore.' },
      { pattern: 'Densitometry', slug: 'term-densitometry', abbr: 'Densitometry', def: 'Analytical scanning measuring light absorption and band optical density.' },
      { pattern: 'D-Limonene', slug: 'term-d-limonene', abbr: 'D-Limonene', def: 'Food-grade citrus terpene solvent acting as non-polar mobile carrier.' },
      { pattern: 'Fluorophores?', slug: 'term-fluorophore', abbr: 'Fluorophore', def: 'Molecule absorbing UV light (365 nm) and re-emitting visible luminescence.' },
      { pattern: 'Naloxone', slug: 'term-naloxone', abbr: 'Naloxone (Narcan)', def: 'Opioid antagonist medication rapidly reversing life-threatening respiratory depression.' },
      { pattern: 'Xylazine', slug: 'term-xylazine', abbr: 'Xylazine ("Tranq")', def: 'Non-opioid veterinary sedative co-mingled with street drugs; unresponsive to naloxone.' }
    ];

    function navigateToGlossary(slug) {
      const glossaryIdx = BOOK_DATA.chapters.findIndex(c => c.filename.includes('Back Matter') || c.id.includes('back-matter'));
      if (glossaryIdx === -1) return;

      expandedChapters.add(glossaryIdx);
      if (currentChapterIndex === glossaryIdx) {
        jumpToHeading(slug);
        highlightGlossaryTerm(slug);
      } else {
        navigateTo(glossaryIdx, slug);
        setTimeout(() => highlightGlossaryTerm(slug), 240);
      }
    }

    function highlightGlossaryTerm(slug) {
      const el = document.getElementById(slug);
      if (!el) return;
      el.classList.remove('glossary-target-highlight');
      void el.offsetWidth;
      el.classList.add('glossary-target-highlight');
      setTimeout(() => {
        el.classList.remove('glossary-target-highlight');
      }, 3000);
    }

    function annotateGlossaryTerms(container) {
      const skipTags = new Set(['A', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'PRE', 'CODE', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA', 'SCRIPT', 'STYLE', 'ABBR']);
      const blocks = container.querySelectorAll('p, li, blockquote, td, th');

      blocks.forEach(block => {
        const textNodes = [];
        const walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT, {
          acceptNode(node) {
            let parent = node.parentElement;
            while (parent && parent !== block) {
              if (skipTags.has(parent.tagName)) return NodeFilter.FILTER_REJECT;
              if (parent.classList && (parent.classList.contains('katex') || parent.classList.contains('math-inline'))) return NodeFilter.FILTER_REJECT;
              parent = parent.parentElement;
            }
            if (parent && skipTags.has(parent.tagName)) return NodeFilter.FILTER_REJECT;
            if (parent && parent.classList && (parent.classList.contains('katex') || parent.classList.contains('math-inline'))) return NodeFilter.FILTER_REJECT;
            return NodeFilter.FILTER_ACCEPT;
          }
        });

        let n;
        while (n = walker.nextNode()) {
          textNodes.push(n);
        }

        const annotatedInBlock = new Set();

        textNodes.forEach(textNode => {
          let text = textNode.nodeValue;
          if (!text || text.length < 2) return;

          for (const item of GLOSSARY_TERMS) {
            if (annotatedInBlock.has(item.slug)) continue;

            const regex = item.isRawRegex 
              ? new RegExp(`(${item.pattern})`, (item.caseSensitive ? '' : 'i') + 'u')
              : new RegExp(`\\b(${item.pattern})\\b`, (item.caseSensitive ? '' : 'i') + 'u');
            
            const match = regex.exec(text);
            if (match) {
              const matchIndex = match.index;
              const matchText = match[0];

              const beforeText = text.substring(0, matchIndex);
              const afterText = text.substring(matchIndex + matchText.length);

              const linkEl = document.createElement('a');
              linkEl.href = `#${item.slug}`;
              linkEl.className = 'glossary-term-link';
              linkEl.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                navigateToGlossary(item.slug);
              };

              const abbrEl = document.createElement('abbr');
              abbrEl.className = 'glossary-abbr';
              abbrEl.title = `${item.abbr}: ${item.def}`;
              abbrEl.textContent = matchText;
              linkEl.appendChild(abbrEl);

              const frag = document.createDocumentFragment();
              if (beforeText) frag.appendChild(document.createTextNode(beforeText));
              frag.appendChild(linkEl);

              const afterNode = afterText ? document.createTextNode(afterText) : null;
              if (afterNode) frag.appendChild(afterNode);

              textNode.parentNode.replaceChild(frag, textNode);
              annotatedInBlock.add(item.slug);

              if (afterNode) {
                textNode = afterNode;
                text = afterText;
              } else {
                break;
              }
            }
          }
        });
      });
    }

    // High-fidelity LaTeX math and symbol renderer (KaTeX with offline fallback)
    function renderMathEquations(container) {
      if (!container) return;

      if (window.renderMathInElement) {
        try {
          renderMathInElement(container, {
            delimiters: [
              { left: '$$', right: '$$', display: true },
              { left: '$', right: '$', display: false }
            ],
            throwOnError: false
          });
          return;
        } catch (err) {
          console.warn('KaTeX renderMathInElement failed, using fallback:', err);
        }
      }

      // Offline / standalone fallback for LaTeX math symbols & formulas
      const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT);
      const textNodes = [];
      let n;
      while (n = walker.nextNode()) {
        if (n.nodeValue && n.nodeValue.includes('$')) {
          textNodes.push(n);
        }
      }

      textNodes.forEach(node => {
        const val = node.nodeValue;
        if (!val || !val.includes('$')) return;

        let p = node.parentElement;
        while (p && p !== container) {
          if (p.tagName === 'CODE' || p.tagName === 'PRE') return;
          p = p.parentElement;
        }

        const replaced = val.replace(/\\$([^\\$\\n]+)\\$/g, (match, formula) => {
          let f = formula
            .split('\\\\alpha').join('α')
            .split('\\\\beta').join('β')
            .split('\\\\gamma').join('γ')
            .split('\\\\delta').join('δ')
            .split('\\\\Delta').join('Δ')
            .split('\\\\varepsilon').join('ε')
            .split('\\\\epsilon').join('ε')
            .split('\\\\mu').join('µ')
            .split('\\\\approx').join('≈')
            .split('\\\\le').join('≤')
            .split('\\\\ge').join('≥')
            .split('\\\\times').join('×')
            .split('\\\\pm').join('±')
            .replace(/\\\\text\\{([^}]+)\\}/g, '$1')
            .replace(/_\\{?([a-zA-Z0-9]+)\\}?/g, '<sub>$1</sub>')
            .replace(/\\^\\{?([a-zA-Z0-9]+)\\}?/g, '<sup>$1</sup>');
          return `<span class="math-inline font-mono text-purple-200">${f}</span>`;
        });

        if (replaced !== val) {
          const span = document.createElement('span');
          span.innerHTML = replaced;
          node.parentNode.replaceChild(span, node);
        }
      });
    }

    function renderChapter(index, targetPage = 0) {
      currentChapterIndex = index;
      expandedChapters.add(index);
      const chapter = BOOK_DATA.chapters[index];
      if (chapter && chapter.part) {
        expandedParts.add(chapter.part);
      }
      
      document.title = `${chapter.title} — What Was In That Joint Bro!?`;
      document.getElementById('crumb-active').innerText = chapter.title;

      const words = chapter.wordCount || (chapter.markdown ? chapter.markdown.trim().split(/\\s+/).length : 0);
      const totalMins = chapter.readingMinutes || Math.max(1, Math.round(words / 200));

      document.getElementById('reading-time-badge').innerText = `~${totalMins}m`;

      // Render Markdown via marked.js
      const container = document.getElementById('markdown-container');
      container.innerHTML = marked.parse(chapter.markdown);

      // Render LaTeX equations & Greek symbols ($R_f = 0.00$, $\alpha$, $\beta$, etc.)
      renderMathEquations(container);

      // Ensure headings have predictable IDs for in-chapter jump navigation
      container.querySelectorAll('h1, h2, h3, h4').forEach(h => {
        if (!h.id) {
          h.id = h.innerText.toLowerCase().replace(/[^\\w\\s-]/g, '').trim().replace(/\\s+/g, '-');
        }
      });

      // Annotate glossary terms with <abbr> tags and links to the glossary
      const glossaryIdx = BOOK_DATA.chapters.findIndex(c => c.filename.includes('Back Matter') || c.id.includes('back-matter'));
      if (index !== glossaryIdx) {
        annotateGlossaryTerms(container);
      }

      // Attach click interceptors for glossary anchors
      container.querySelectorAll('a[href^="#term-"]').forEach(a => {
        a.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          const slug = a.getAttribute('href').slice(1);
          navigateToGlossary(slug);
        });
      });

      // Update Prev / Next Chapter footer buttons
      const prevChapBtn = document.getElementById('btn-prev-chap');
      const nextChapBtn = document.getElementById('btn-next-chap');
      const prevChapLabel = document.getElementById('prev-chap-label');
      const nextChapLabel = document.getElementById('next-chap-label');

      if (index > 0) {
        prevChapBtn.classList.remove('invisible');
        if (prevChapLabel) prevChapLabel.innerText = BOOK_DATA.chapters[index - 1].title;
      } else {
        prevChapBtn.classList.add('invisible');
      }

      if (index < BOOK_DATA.chapters.length - 1) {
        nextChapBtn.classList.remove('invisible');
        if (nextChapLabel) nextChapLabel.innerText = BOOK_DATA.chapters[index + 1].title;
      } else {
        nextChapBtn.classList.add('invisible');
      }

      renderNav();
      history.replaceState(null, '', `#${chapter.id}`);

      // Calculate pages and jump to target page
      requestAnimationFrame(() => {
        updatePagination(false);
        if (targetPage === 'last') {
          goToPage(totalPagesInChapter - 1, false);
        } else if (typeof targetPage === 'string') {
          jumpToHeading(targetPage);
        } else {
          goToPage(typeof targetPage === 'number' ? targetPage : 0, false);
        }
      });
    }

    // Recalculates horizontal columns and page count
    function updatePagination(maintainFraction = false, oldFraction = 0) {
      const container = document.getElementById('markdown-container');
      if (!container) return;

      const pageWidth = container.clientWidth;
      if (pageWidth <= 0) return;

      container.style.columnWidth = `${pageWidth}px`;
      container.style.columnGap = '0px';

      // Total pages derived from full horizontal scroll width of markdown-container
      totalPagesInChapter = Math.max(1, Math.round(container.scrollWidth / pageWidth));

      if (maintainFraction) {
        currentPageIndex = Math.min(totalPagesInChapter - 1, Math.round(oldFraction * (totalPagesInChapter - 1)));
      } else {
        currentPageIndex = Math.max(0, Math.min(totalPagesInChapter - 1, currentPageIndex));
      }

      goToPage(currentPageIndex, false);
    }

    // Flips to a specific page index
    function goToPage(pageIdx, smooth = true) {
      const container = document.getElementById('markdown-container');
      if (!container) return;

      const pageWidth = container.clientWidth;
      currentPageIndex = Math.max(0, Math.min(totalPagesInChapter - 1, pageIdx));

      container.scrollTo({
        left: currentPageIndex * pageWidth,
        behavior: smooth ? 'smooth' : 'instant'
      });

      updatePageIndicators();
    }

    // Step pages left (-1) or right (+1)
    function flipPage(delta) {
      const target = currentPageIndex + delta;
      if (target >= 0 && target < totalPagesInChapter) {
        goToPage(target, true);
      } else if (target >= totalPagesInChapter) {
        // Flipping past last page advances to next chapter
        if (currentChapterIndex < BOOK_DATA.chapters.length - 1) {
          navigateTo(currentChapterIndex + 1, 0);
        }
      } else if (target < 0) {
        // Flipping before first page steps to prev chapter's last page
        if (currentChapterIndex > 0) {
          navigateTo(currentChapterIndex - 1, 'last');
        }
      }
    }

    // Update all page count, progress bar, and reading minute badges
    function updatePageIndicators() {
      const chapter = BOOK_DATA.chapters[currentChapterIndex];
      const words = chapter.wordCount || (chapter.markdown ? chapter.markdown.trim().split(/\\s+/).length : 0);
      const totalMins = chapter.readingMinutes || Math.max(1, Math.round(words / 200));

      const pageNum = currentPageIndex + 1;
      const totalPages = totalPagesInChapter;

      // Percentage of current chapter read
      const percent = totalPages > 1 
        ? Math.min(100, Math.round((pageNum / totalPages) * 100))
        : 100;

      // Remaining minutes on this chapter
      const fractionRemaining = Math.max(0, (totalPages - pageNum) / totalPages);
      const minsLeft = Math.max(0, Math.round(totalMins * fractionRemaining));

      // Global top line progress bar
      const topBar = document.getElementById('progress-bar');
      if (topBar) topBar.style.width = `${percent}%`;

      // Reader header progress fill & percent
      const pageFill = document.getElementById('page-progress-fill');
      if (pageFill) pageFill.style.width = `${percent}%`;

      const progressPercentText = document.getElementById('progress-percent-text');
      if (progressPercentText) progressPercentText.innerText = `${percent}%`;

      const timeRemainingText = document.getElementById('time-remaining-text');
      if (timeRemainingText) {
        if (pageNum === totalPages) {
          timeRemainingText.innerHTML = `<span class="text-emerald-400 font-semibold">✓ End of chapter</span>`;
        } else {
          timeRemainingText.innerText = `~${minsLeft}m left (${pageNum}/${totalPages})`;
        }
      }

      // Live header stat
      const headerStat = document.getElementById('header-stat-text');
      if (headerStat) {
        if (pageNum === totalPages) {
          headerStat.innerHTML = `<span class="text-emerald-400">✓ Page ${pageNum}/${totalPages}</span>`;
        } else {
          headerStat.innerText = `⏱️ ~${minsLeft}m left (Page ${pageNum}/${totalPages})`;
        }
      }

      // Footer page counter
      const pageCounterLabel = document.getElementById('page-counter-label');
      if (pageCounterLabel) {
        pageCounterLabel.innerText = `Page ${pageNum} of ${totalPages}`;
      }

      // Floating flip arrows disabled status
      const btnPrev = document.getElementById('btn-flip-prev');
      const btnNext = document.getElementById('btn-flip-next');
      if (btnPrev) {
        btnPrev.disabled = (currentPageIndex === 0 && currentChapterIndex === 0);
        btnPrev.title = (currentPageIndex === 0) ? "Previous Chapter" : "Previous Page (←)";
      }
      if (btnNext) {
        btnNext.disabled = (currentPageIndex === totalPages - 1 && currentChapterIndex === BOOK_DATA.chapters.length - 1);
        btnNext.title = (currentPageIndex === totalPages - 1) ? "Next Chapter (→)" : "Next Page (→)";
      }
    }

    function jumpToHeading(slug) {
      const el = document.getElementById(slug);
      const container = document.getElementById('markdown-container');
      if (!el || !container) return;

      const containerRect = container.getBoundingClientRect();
      const elRect = el.getBoundingClientRect();
      const trueLeft = elRect.left - containerRect.left + container.scrollLeft;
      const targetPage = Math.max(0, Math.min(totalPagesInChapter - 1, Math.floor(trueLeft / container.clientWidth)));
      
      goToPage(targetPage, true);
    }

    function navigateTo(index, targetPage = 0) {
      if (index >= 0 && index < BOOK_DATA.chapters.length) {
        renderChapter(index, targetPage);
      }
    }

    function stepChapter(delta) {
      navigateTo(currentChapterIndex + delta, 0);
    }

    // Instant search with exact page jumping
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
          matches.push({ chapIdx, title: chap.title, snippet, query: q });
        }
      });

      if (matches.length > 0) {
        searchResults.innerHTML = matches.slice(0, 8).map(m => `
          <div onclick="selectSearchResult(${m.chapIdx}, '${m.query.replace(/'/g, "\\'")}')" 
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

    function selectSearchResult(chapIdx, query) {
      searchResults.classList.add('hidden');
      searchInput.value = '';
      navigateTo(chapIdx, 0);

      // Seek text node match and flip to that page
      setTimeout(() => {
        const container = document.getElementById('markdown-container');
        if (!container) return;

        const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT);
        let node;
        while (node = walker.nextNode()) {
          if (node.nodeValue.toLowerCase().includes(query.toLowerCase())) {
            const parent = node.parentElement;
            if (parent) {
              const containerRect = container.getBoundingClientRect();
              const pRect = parent.getBoundingClientRect();
              const trueLeft = pRect.left - containerRect.left + container.scrollLeft;
              const targetPage = Math.max(0, Math.min(totalPagesInChapter - 1, Math.floor(trueLeft / container.clientWidth)));
              goToPage(targetPage, true);
              break;
            }
          }
        }
      }, 150);
    }

    // Sidebar toggling (Desktop & Mobile)
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarClose = document.getElementById('sidebar-close');

    function toggleSidebar() {
      if (window.innerWidth < 768) {
        sidebar.classList.toggle('-translate-x-full');
      } else {
        sidebar.classList.toggle('hidden');
        requestAnimationFrame(() => updatePagination(true));
      }
    }
    function closeSidebar() {
      sidebar.classList.add('-translate-x-full');
    }

    sidebarToggle.addEventListener('click', toggleSidebar);
    if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);

    // Window resize observer to re-paginate smoothly
    window.addEventListener('resize', () => {
      updatePagination(true);
    });

    // Support manual scrollbar dragging: synchronize page counter and progress in real time
    let manualScrollTimeout = null;
    const markdownContainerEl = document.getElementById('markdown-container');
    if (markdownContainerEl) {
      markdownContainerEl.addEventListener('scroll', () => {
        if (manualScrollTimeout) clearTimeout(manualScrollTimeout);
        manualScrollTimeout = setTimeout(() => {
          const pageWidth = markdownContainerEl.clientWidth;
          if (pageWidth > 0 && totalPagesInChapter > 0) {
            const newPage = Math.max(0, Math.min(totalPagesInChapter - 1, Math.round(markdownContainerEl.scrollLeft / pageWidth)));
            if (newPage !== currentPageIndex) {
              currentPageIndex = newPage;
              updatePageIndicators();
            }
          }
        }, 50);
      }, { passive: true });
    }

    // Touch / Swipe Gesture Page Turning
    let touchStartX = 0;
    let touchStartY = 0;
    
    markdownContainerEl.addEventListener('touchstart', (e) => {
      touchStartX = e.touches[0].clientX;
      touchStartY = e.touches[0].clientY;
    }, { passive: true });

    markdownContainerEl.addEventListener('touchend', (e) => {
      const diffX = e.changedTouches[0].clientX - touchStartX;
      const diffY = e.changedTouches[0].clientY - touchStartY;
      if (Math.abs(diffX) > 40 && Math.abs(diffX) > Math.abs(diffY)) {
        if (diffX < 0) flipPage(1);  // Swipe Left -> Next Page
        else flipPage(-1);           // Swipe Right -> Prev Page
      }
    }, { passive: true });

    // Trackpad / Mousewheel page flip with debounce
    let wheelDebounce = null;
    markdownContainerEl.addEventListener('wheel', (e) => {
      e.preventDefault();
      if (wheelDebounce) return;
      const delta = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY;
      if (Math.abs(delta) > 30) {
        if (delta > 0) flipPage(1);
        else flipPage(-1);
        wheelDebounce = setTimeout(() => { wheelDebounce = null; }, 320);
      }
    }, { passive: false });

    // Font size control listeners
    document.getElementById('font-dec-btn').addEventListener('click', () => applyFontSize(currentFontScaleIndex - 1));
    document.getElementById('font-inc-btn').addEventListener('click', () => applyFontSize(currentFontScaleIndex + 1));
    document.getElementById('font-reset-btn').addEventListener('click', () => applyFontSize(2));

    // Keyboard Shortcuts
    window.addEventListener('keydown', (e) => {
      // Focus Search: Cmd/Ctrl + K
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        searchInput.focus();
        return;
      }

      // Font scaling: Alt + '+' / '-' / '0'
      if (e.altKey && (e.key === '=' || e.key === '+')) {
        e.preventDefault();
        applyFontSize(currentFontScaleIndex + 1);
        return;
      }
      if (e.altKey && (e.key === '-' || e.key === '_')) {
        e.preventDefault();
        applyFontSize(currentFontScaleIndex - 1);
        return;
      }
      if (e.altKey && e.key === '0') {
        e.preventDefault();
        applyFontSize(2);
        return;
      }

      // Toggle Table of Contents: T
      if (e.key.toLowerCase() === 't' && document.activeElement !== searchInput) {
        toggleSidebar();
        return;
      }

      // Page Navigation Keyboard Controls
      if (document.activeElement !== searchInput) {
        // Next Page: Right Arrow, PageDown, Space, 'l'
        if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ' || e.key.toLowerCase() === 'l') {
          e.preventDefault();
          flipPage(1);
        }
        // Prev Page: Left Arrow, PageUp, Shift+Space, 'h'
        if (e.key === 'ArrowLeft' || e.key === 'PageUp' || (e.key === ' ' && e.shiftKey) || e.key.toLowerCase() === 'h') {
          e.preventDefault();
          flipPage(-1);
        }
        // Prev / Next Chapter: '[' and ']'
        if (e.key === '[') stepChapter(-1);
        if (e.key === ']') stepChapter(1);
      }
    });

    // Hash router boot & initialize state
    window.addEventListener('DOMContentLoaded', () => {
      try {
        const savedFontIdx = localStorage.getItem('purple_canary_font_scale_idx');
        if (savedFontIdx !== null) {
          applyFontSize(parseInt(savedFontIdx, 10));
        } else {
          applyFontSize(2);
        }
      } catch (e) {
        applyFontSize(2);
      }

      const hash = window.location.hash.replace('#', '');
      const initialIdx = BOOK_DATA.chapters.findIndex(c => c.id === hash);
      renderChapter(initialIdx !== -1 ? initialIdx : 0, 0);
    });
  </script>
</body>
</html>
"""

def generate_spa():
    root = Path(__file__).parent.resolve()
    dist = root / "dist"
    dist.mkdir(exist_ok=True)
    json_path = dist / "book_data.json"

    # Cache local copy of the logo for offline resilience
    logo_file = dist / "logo.png"
    if not logo_file.exists():
        try:
            import urllib.request
            url = "https://i.ibb.co/C3Jc6MKH/Gemini-Generated-Image-p4r67dp4r67dp4r6-removebg-preview.png"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp, open(logo_file, "wb") as f:
                f.write(resp.read())
        except Exception:
            pass

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

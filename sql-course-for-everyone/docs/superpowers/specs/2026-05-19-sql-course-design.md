# SQL for Everyone — Design Spec

**Date:** 2026-05-19
**Status:** Approved

## Overview

A single-file interactive SQL course for non-technical business professionals (marketing, finance, ops, HR) who currently rely on data analysts for basic data extraction. The course teaches SQL from zero to analyst-level using a live in-browser editor, friendly tone, and exercises with hints.

## Audience

- Business function people who understand data conceptually but cannot query it themselves
- Currently submit tickets to data analysts for basic pulls and reports
- Work with Snowflake or BigQuery at their company
- No prior SQL or programming experience assumed

## Goals

After completing the course, learners can:
1. Pull and filter their own data without an analyst
2. Summarise data with aggregations and grouping
3. Combine multiple tables with joins
4. Write subqueries, CASE WHEN, window functions, and CTEs
5. Build basic reports independently

## Format

- **Single HTML file** — self-contained, runs in browser, no server, no setup
- **Interactive SQL editor** — type queries, see results instantly
- **SQL engine:** sql.js (SQLite compiled to WebAssembly) with a compatibility layer that translates Snowflake/BigQuery syntax
- **Theme:** Light mode default, dark mode toggle
- **Responsive:** Works on desktop and tablet

## Architecture

| Component | Choice | Rationale |
|-----------|--------|-----------|
| SQL engine | sql.js (SQLite in WASM) | Runs entirely in browser, real SQL, no server |
| Styling | Inline `<style>` | Keeps it one file |
| JavaScript | Vanilla JS, inline `<script>` | No framework, no build step |
| Layout | Sidebar nav + main content area | Familiar, scales to 12 lessons |
| Editor | `<textarea>` with monospace font + Tab support | Simple, no heavy library |
| Results | HTML table rendered from query output | Clean, scrollable, copy-friendly |

### SQL Syntax Compatibility

The course teaches **Snowflake/BigQuery syntax**. Under the hood, sql.js runs SQLite, so a thin compatibility layer rewrites common functions before execution:

| Taught Syntax (Snowflake/BigQuery) | Rewritten to (SQLite) |
|------------------------------------|-----------------------|
| `DATE_TRUNC('month', date_col)` | `strftime('%Y-%m', date_col)` |
| `DATEADD('day', 30, date_col)` | `date(date_col, '+30 days')` |
| `DATEDIFF('day', start, end)` | `julianday(end) - julianday(start)` |
| `CURRENT_DATE()` | `date('now')` |
| `ILIKE` | `LIKE` (SQLite is case-insensitive by default) |

Where syntax diverges significantly (e.g. QUALIFY), the lesson explains the difference and provides both Snowflake and BigQuery variants.

## Data Model

Four tables with realistic sample data:

### customers (~15 rows)
| Column | Type | Example |
|--------|------|---------|
| id | INTEGER | 1 |
| name | TEXT | "James Wilson" |
| email | TEXT | "james.wilson@gmail.com" |
| city | TEXT | "Sydney" |
| signup_date | TEXT | "2023-03-15" |

### products (~15 rows)
| Column | Type | Example |
|--------|------|---------|
| id | INTEGER | 1 |
| name | TEXT | "Wireless Headphones" |
| price | REAL | 89.99 |
| category | TEXT | "Electronics" |

### orders (~30 rows)
| Column | Type | Example |
|--------|------|---------|
| id | INTEGER | 1 |
| customer_id | INTEGER | 1 (FK → customers.id) |
| product_id | INTEGER | 1 (FK → products.id) |
| quantity | INTEGER | 2 |
| amount | REAL | 179.98 |
| order_date | TEXT | "2024-01-15" |

### employees (~15 rows)
| Column | Type | Example |
|--------|------|---------|
| id | INTEGER | 1 |
| name | TEXT | "Sarah Johnson" |
| department | TEXT | "Engineering" |
| salary | REAL | 125000 |
| hire_date | TEXT | "2020-03-15" |

**Data characteristics:**
- Cities: Sydney, Melbourne, Brisbane, Perth, Adelaide
- Categories: Electronics, Furniture, Stationery, Accessories
- Orders span 2023-2024 (enables monthly trends, YoY)
- Departments: Engineering, Marketing, Sales, HR, Finance

## Curriculum

12 lessons in linear sequence. Each builds on the previous.

| # | Lesson | Core Concept | Exercises |
|---|--------|-------------|-----------|
| 0 | Welcome | What is SQL? Spreadsheet analogy. Try a simple query. | 1 (try it) |
| 1 | SELECT | Pick columns, rename with AS, SELECT * | 1 (easy) |
| 2 | WHERE | Filter rows, =, !=, >, <, >=, <=, AND, OR, IN, BETWEEN, LIKE, IS NULL | 2 (easy) |
| 3 | Sorting | ORDER BY ASC/DESC, LIMIT | 1 (easy) |
| 4 | Aggregation | COUNT, SUM, AVG, MIN, MAX | 1 (medium) |
| 5 | GROUP BY | Grouping, HAVING, aggregate filtering | 2 (medium) |
| 6 | JOINs | INNER JOIN, LEFT JOIN, multi-table joins, join + aggregation | 2 (medium) |
| 7 | Subqueries | Subquery in WHERE, subquery in FROM, correlated subqueries | 2 (hard) |
| 8 | CASE WHEN | Simple CASE, searched CASE, conditional aggregation | 2 (hard) |
| 9 | Window Functions | ROW_NUMBER, RANK, DENSE_RANK, SUM() OVER, LAG/LEAD, PARTITION BY | 2 (hard) |
| 10 | CTEs | WITH clause, multiple CTEs, chaining, readability | 2 (hard) |
| 11 | Cheatsheet | Quick reference — all syntax, common patterns, common mistakes | 0 |

## UI / UX

### Layout

```
┌──────────────┬─────────────────────────────────────┐
│   SIDEBAR    │         MAIN CONTENT                │
│              │                                     │
│  Logo        │  Lesson title (gradient)            │
│  ────────    │  Subtitle                           │
│  ▶ Welcome   │                                     │
│    SELECT    │  Explanation with analogies          │
│    WHERE     │                                     │
│    ...       │  [Static code example]              │
│    Cheatsheet│                                     │
│              │  [Interactive Playground]            │
│   [🌙/☀️]   │    textarea + Run + Reset + Hint    │
│              │    results table                    │
│              │                                     │
│              │  [← Previous]     [Next →]          │
└──────────────┴─────────────────────────────────────┘
```

### Key UX Decisions

| Element | Decision |
|---------|----------|
| Sidebar | Fixed, always visible, highlights current lesson, shows completion checkmarks |
| Progress bar | Top of main area, % complete based on lessons with at least one successful query |
| Theme toggle | Sun/moon icon in sidebar footer, defaults to light |
| Code examples | Static blocks with syntax highlighting before each playground |
| Playgrounds | Textarea + Run (or Cmd/Ctrl+Enter) + Reset + Hint |
| Results | HTML table with row count, friendly error messages |
| Navigation | Previous/Next buttons at bottom + sidebar click |
| Mobile | Sidebar collapses to hamburger menu |
| Schema display | Tables shown at start of relevant lessons as reference |

### Visual Style

- **Light mode default:** White/light grey background, dark text, blue accents
- **Dark mode:** Dark background, light text, same accent colours
- Clean typography (system font stack)
- Monospace for code (system monospace stack)
- Minimal chrome — content is the focus
- Colour-coded concept boxes: analogy (yellow), why (cyan), tip (green), warning (orange)

## Exercise System

Each lesson has 1-3 exercises:

1. **Challenge description** in plain language
2. **Playground** with empty textarea or starter query
3. **Hint button** reveals the answer in the results area (doesn't overwrite their query)
4. **Subtle success feedback** when query returns results

### Difficulty Progression

| Lessons | Difficulty | Style |
|---------|-----------|-------|
| 1-3 | Easy | Modify a working example |
| 4-6 | Medium | Write from scratch, single concept |
| 7-10 | Hard | Combine multiple concepts |

### No Strict Validation

SQL has multiple valid solutions. The course does not validate correctness — hints show one possible answer. This avoids frustration and respects that their approach may differ.

## File Structure

```
sql-course-for-everyone/
├── index.html              # The entire course (single file)
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-05-19-sql-course-design.md  # This file
```

## Success Criteria

1. Single HTML file opens in any modern browser with no setup
2. All 12 lessons render with interactive SQL editor
3. Queries execute and return results correctly
4. Snowflake/BigQuery syntax works via compatibility layer
5. Light/dark theme toggle works
6. Exercises have hints that reveal answers
7. Progress tracking persists during session
8. Mobile responsive (sidebar collapses)
9. Course feels friendly and approachable, not intimidating

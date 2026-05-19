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
4. Build basic reports independently
5. Write subqueries, CASE WHEN, window functions, and CTEs
6. Continue self-directed learning with external resources

## Key Design Principles (from persona research)

1. **Frame as "asking questions", not "learning SQL"** — the word "coding" triggers fear. Position SQL as "search filters for databases."
2. **Every lesson starts with a business question** — not "Filtering with WHERE" but "How many customers are in Sydney?"
3. **Interactive editor is the core differentiator** — 10/10 target personas rated it 8+/10. Lean into hands-on learning.
4. **Smooth the difficulty curve** — add a transitional lesson between GROUP BY and subqueries to bridge the gap.
5. **Friendly but not condescending** — technical personas will disengage if too dumbed down; non-technical ones need reassurance.

## Format

- **Single HTML file** — self-contained, runs in browser, no server, no setup
- **Interactive SQL editor** — type queries, see results instantly
- **SQL engine:** sql.js (SQLite compiled to WebAssembly) with a compatibility layer that translates Snowflake/BigQuery syntax
- **Theme:** Light mode default, dark mode toggle
- **Responsive:** Works on desktop and tablet

## Monetisation (from paid conversion research)

- **Price point:** $89 individual, $59/seat team pack (5+ licences)
- **Expense-friendly:** Clean invoice, completion certificate, clear learning outcome
- **Perceived value upgrades:**
  - Branded PDF export of the course
  - Completion certificate (auto-generated with learner's name and date)
  - Custom domain with simple landing page
- **Retention:** Optional email capture for progress nudges (days 3, 7, 14)
- **Drop-off prevention:** Capstone checkpoint at lesson 7 (Mini Reports) — "Build a monthly revenue report from scratch"

**Research files:**
- `docs/superpowers/specs/2026-05-19-persona-research.md` — target audience review
- `docs/superpowers/specs/2026-05-19-paid-conversion-research.md` — pricing & commitment research

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

14 lessons in linear sequence. Each builds on the previous. Each lesson header includes a **business question** (not a SQL concept) and a **difficulty badge**.

| # | Lesson | Business Question | Core Concept | Difficulty | Exercises |
|---|--------|------------------|-------------|------------|-----------|
| 0 | Welcome | "What is this and why should I care?" | What SQL is, spreadsheet analogy, "What SQL is NOT" myth-busting, try a simple query | — | 1 (try it) |
| 1 | SELECT | "How do I see just the data I need?" | Pick columns, rename with AS, SELECT * | Easy | 1 |
| 2 | WHERE | "How do I find specific records?" | Filter rows, =, !=, >, <, >=, <=, AND, OR, IN, BETWEEN, LIKE, IS NULL | Easy | 2 |
| 3 | Sorting | "What are my top/bottom results?" | ORDER BY ASC/DESC, LIMIT | Easy | 1 |
| 4 | Aggregation | "How many? What's the total? What's the average?" | COUNT, SUM, AVG, MIN, MAX | Medium | 1 |
| 5 | GROUP BY | "How do I summarise by category?" | Grouping, HAVING, aggregate filtering | Medium | 2 |
| 6 | JOINs | "How do I combine data from different tables?" | INNER JOIN, LEFT JOIN, multi-table joins, join + aggregation | Medium | 2 |
| 7 | **Mini Reports** | "Can I build a real report with what I know?" | Combining SELECT + WHERE + JOIN + GROUP BY + ORDER BY into end-to-end reports | Medium | 2 |
| 8 | Subqueries | "How do I use one query's result in another?" | Subquery in WHERE, subquery in FROM, correlated subqueries | Hard | 2 |
| 9 | CASE WHEN | "How do I add labels and buckets to my data?" | Simple CASE, searched CASE, conditional aggregation | Hard | 2 |
| 10 | Window Functions | "How do I rank or compare rows within a group?" | ROW_NUMBER, RANK, DENSE_RANK, SUM() OVER, LAG/LEAD, PARTITION BY | Hard | 2 |
| 11 | CTEs | "How do I write complex queries that I can actually read?" | WITH clause, multiple CTEs, chaining, readability | Hard | 2 |
| 12 | Cheatsheet | "What's the syntax again?" | Quick reference — all syntax, common patterns, common mistakes | — | 0 |
| 13 | What's Next | "Where do I go from here?" | External resources for continued learning (dbt, Looker, Power BI SQL, advanced courses) | — | 0 |

**Lesson 7 (Mini Reports) rationale:** Persona research flagged a difficulty cliff between GROUP BY (lesson 5) and subqueries (lesson 8). This transitional lesson bridges the gap by having learners combine everything they've learned into complete reports — building confidence before introducing new concepts.

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
| PDF export | "Download PDF" button in sidebar — exports full course as branded PDF |
| Completion certificate | Auto-generated on finishing all lessons — fills in name + date |
| Progress nudges | Optional email capture at start; nudges at days 3, 7, 14 if incomplete |

### Visual Style

- **Light mode default:** White/light grey background, dark text, blue accents
- **Dark mode:** Dark background, light text, same accent colours
- Clean typography (system font stack)
- Monospace for code (system monospace stack)
- Minimal chrome — content is the focus
- Colour-coded concept boxes: analogy (yellow), why (cyan), tip (green), warning (orange)

## Lesson Content Guidelines

### Welcome Lesson (Lesson 0)
Must include a "What SQL is NOT" concept box that explicitly addresses the fear of coding:
- SQL is not programming — it's asking questions to a database
- Analogy: "Like using search filters on a spreadsheet, not building an app"
- You don't need to be technical — if you can use Excel filters, you can learn SQL

### All Lessons
- Title in sidebar shows the business question, not the SQL concept
- Each lesson opens with the business question before introducing syntax
- Concept boxes use analogies from spreadsheets, email, and everyday office tools
- Code examples are preceded by a plain-English explanation of what they'll do

### What's Next Lesson (Lesson 13)
Links to external resources for continued learning:
- dbt (data transformation)
- Looker / Power BI SQL (reporting)
- Mode Analytics SQL tutorial (intermediate)
- Snowflake / BigQuery documentation
- Community: dbt Slack, Locally Optimistic

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
2. All 14 lessons render with interactive SQL editor
3. Queries execute and return results correctly
4. Snowflake/BigQuery syntax works via compatibility layer
5. Light/dark theme toggle works
6. Exercises have hints that reveal answers
7. Progress tracking persists during session
8. Mobile responsive (sidebar collapses)
9. Course feels friendly and approachable, not intimidating
10. Welcome lesson explicitly addresses "fear of coding" barrier
11. Each lesson framed as a business question, not a SQL concept
12. Difficulty progression is smooth — no cliff between GROUP BY and subqueries
13. "What's Next" section provides clear path for continued learning
14. PDF export generates a branded, printable version of the course
15. Completion certificate auto-generates with learner's name and date
16. Capstone checkpoint at lesson 7 creates a "shareable win" moment
17. Landing page exists with clear CTA and pricing ($89 individual)

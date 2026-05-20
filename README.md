# SQL for Everyone

An interactive SQL course for non-technical business professionals. Learn to query databases without relying on data analysts.

## Quick Start

1. Open `index.html` in any modern browser
2. No server or installation required
3. Start with the Welcome lesson

## What You'll Learn

- **SELECT** — Pick the data you need
- **WHERE** — Filter and search records
- **Sorting** — ORDER BY and LIMIT
- **Aggregation** — COUNT, SUM, AVG, MIN, MAX
- **GROUP BY** — Summarise by category
- **JOINs** — Combine data from multiple tables
- **Subqueries** — Nested queries
- **CASE WHEN** — Conditional logic
- **Window Functions** — ROW_NUMBER, RANK, running totals
- **CTEs** — Readable complex queries

## Project Structure

```
sql-course-for-everyone/
├── index.html              # The entire course (single file)
├── landing.html            # Marketing landing page
├── js/
│   ├── sql-wasm.js         # SQLite compiled to WebAssembly
│   └── sql-wasm.wasm       # SQLite WASM binary
├── docs/
│   └── superpowers/
│       ├── specs/          # Design specs and research
│       └── plans/          # Implementation plans
└── README.md               # This file
```

## Features

- **Interactive SQL editor** — Type queries, see results instantly
- **Snowflake/BigQuery syntax** — Teaches modern SQL with compatibility layer
- **14 lessons** — From zero to analyst-level
- **Exercises with hints** — Practice what you learn
- **Progress tracking** — Saves progress in localStorage
- **Light/dark theme** — Clean Light theme
- **Responsive** — Works on desktop and tablet
- **Cmd+K** — Command palette to jump between lessons
- **PDF export** — Print the course for offline reference
- **Completion certificate** — Auto-generates on finishing all lessons

## Database

Uses an in-memory SQLite database with sample data:

- **customers** — 15 rows (names, emails, cities)
- **products** — 15 rows (names, prices, categories)
- **orders** — 30 rows (product orders with dates and amounts)
- **employees** — 15 rows (names, departments, salaries)

## Customisation

### Changing Colours

Edit the CSS variables at the top of the `<style>` block:

```css
:root {
  --bg: #ffffff;
  --text: #171717;
  --accent: #171717;
  /* ... */
}
```

### Adding Lessons

1. Add content function to the `lessons` array
2. Add entry to the `renderNav` function
3. Follow the existing pattern for playgrounds and exercises

### Modifying Data

Edit the `INSERT INTO` statements in the database initialization section.

## Browser Support

- Chrome 55+
- Firefox 52+
- Safari 10.1+
- Edge 15+

## Credits

- **SQL.js** — SQLite compiled to WebAssembly
- **Inter** — UI font
- **JetBrains Mono** — Code font

## Licence

MIT

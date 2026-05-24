# SQL for Everyone

An interactive SQL course for non-technical business professionals. Data judgment for the AI age. Learn to read, write, and evaluate SQL queries.

## Quick Start

1. Open `index.html` in any modern browser
2. No server or installation required
3. Start with the Welcome lesson

## What You'll Learn

11 high-impact lessons for business stakeholders:

- **SELECT**, pick the data you need
- **WHERE**, filter, search, pattern match, handle NULLs
- **ORDER BY + LIMIT**, sort and cap results
- **Aggregation**, COUNT, SUM, AVG, ROUND, percentages
- **GROUP BY**, summarise by category
- **JOINs**, combine data from multiple tables
- **CASE WHEN**, conditional logic
- **Date Filtering**, monthly trends, quarter comparisons, date ranges
- **AI + SQL**, prompt AI, explain queries to stakeholders, catch bugs

## Project Structure

```
sql-course-for-everyone/
├── index.html              # The entire course (single file)
└── README.md               # This file
```

## Features

- **Interactive SQL editor**, type queries, see results instantly
- **Snowflake/BigQuery syntax**, teaches modern SQL with compatibility layer
- **11 lessons**, each lesson builds on the previous one
- **Business-focused**, real-world patterns: trends, percentages, date filtering
- **Exercises with hints**, practice what you learn
- **Progress tracking**, saves progress in localStorage
- **Responsive**, works on desktop and tablet
- **Cmd+K**, command palette to jump between lessons
- **PDF export**, print the course for offline reference

## Database

Uses an in-memory SQLite database with sample data:

- **customers**, 15 rows (names, emails, cities)
- **products**, 15 rows (names, prices, categories)
- **orders**, 30 rows (product orders with dates and amounts)
- **employees**, 15 rows (names, departments, salaries)

## Browser Support

- Chrome 55+
- Firefox 52+
- Safari 10.1+
- Edge 15+

## Credits

- **SQL.js**, SQLite compiled to WebAssembly
- **Inter**, UI font
- **JetBrains Mono**, code font

## Licence

MIT

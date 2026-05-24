# SQL for Everyone

Data judgment for the AI age. An interactive SQL course for non-technical business professionals. Learn to read, write, and evaluate SQL queries — including AI-generated ones.

AI can write SQL for you. That makes knowing SQL *more* important, not less. When you can read a query, you can check whether it's right. When you can't, you're trusting a black box with your business decisions. Calculators didn't kill arithmetic. They made numeracy essential. Same thing is happening with SQL and AI.

## Quick Start

1. Go to [wsamuelw.github.io/sql-for-everyone](https://wsamuelw.github.io/sql-for-everyone/)
2. No server, no installation, no accounts
3. Start with the Welcome lesson

## What You'll Learn

11 lessons that build on each other:

| # | Lesson | What It Covers |
|---|--------|----------------|
| 01 | **Welcome** | What a database is, how the course works |
| 02 | **SELECT** | Pick specific columns, rename with AS |
| 03 | **WHERE** | Filter with =, BETWEEN, AND/OR, IN, LIKE, IS NULL |
| 04 | **ORDER BY + LIMIT** | Sort results, get top N rows |
| 05 | **Aggregation** | COUNT, SUM, AVG, MIN, MAX, ROUND, percentages |
| 06 | **GROUP BY** | Summarise by category, filter groups with HAVING |
| 07 | **JOINs** | Combine tables, INNER JOIN vs LEFT JOIN |
| 08 | **CASE WHEN** | Conditional logic, label rows by category |
| 09 | **Date Filtering** | Date ranges, monthly trends, quarter comparisons, month-over-month growth |
| 10 | **AI + SQL** | Prompt AI effectively, read its output, spot bugs, explain queries to stakeholders |
| 11 | **Reference & Next Steps** | Quick reference cheat sheet, external resources |

## What You Can Do After This Course

- Pull and filter your own data
- Summarise with aggregations and grouping
- Combine tables with joins
- Use CASE WHEN for conditional logic
- Filter by date ranges and analyse trends over time
- Read and evaluate AI-generated queries
- Spot common AI failure patterns before they become wrong answers
- Build basic reports independently

## Features

- **Live SQL editor** — type queries, see results instantly in your browser
- **In-memory SQLite** — runs on WebAssembly, no server needed
- **Snowflake/BigQuery syntax** — teaches modern SQL with a compatibility layer
- **Business-focused examples** — real-world patterns: trends, percentages, date filtering
- **Exercises with hints** — practice what you learn, with two-level hint system
- **Progress tracking** — saves your progress in localStorage
- **Command palette** — Cmd+K to jump between lessons
- **PDF export** — print the course for offline reference
- **Responsive** — works on desktop and tablet

## Database Schema

The course uses a fictional company's data across 4 tables:

```
customers          products           orders              employees
-----------        -----------        -----------         -----------
id                 id                 id                  id
name               name               customer_id (FK)    name
email              price              product_id (FK)     department
city               category           quantity            salary
signup_date                           amount              hire_date
                                      order_date
```

**Sample data:** 15 customers, 15 products, 30 orders, 15 employees.

## Quick Reference

```sql
SELECT column1, column2, COUNT(*)
FROM table_name
JOIN other_table ON table.id = other_table.table_id
WHERE condition
GROUP BY column1
HAVING COUNT(*) > 2
ORDER BY column2 DESC
LIMIT 10;
```

**Key patterns:**
- `WHERE x IN ('a', 'b')` — match multiple values
- `WHERE x LIKE '%text%'` — pattern match
- `IS NULL / IS NOT NULL` — empty values
- `COUNT(*)  SUM()  AVG()` — aggregate functions
- `ROUND(value, 2)` — round to 2 decimals
- `COALESCE(a, b)` — use a if not null, else b

**Common mistakes:**
- Use `IS NULL` not `= NULL`
- Use `HAVING` for filtering after GROUP BY, not WHERE
- Every column in SELECT must either be aggregated or in GROUP BY
- Use LEFT JOIN to keep all rows from the left table

## External Resources

- [Google Data Analytics Professional Certificate](https://imp.i384100.net/6bOn5Q) (Coursera)
- [Snowflake Documentation](https://docs.snowflake.com/)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)

## Project Structure

```
sql-for-everyone/
├── index.html                        # The entire course (single file, ~2500 lines)
├── README.md
└── .github/workflows/deploy.yml      # GitHub Pages deployment
```

## Browser Support

Chrome 55+ | Firefox 52+ | Safari 10.1+ | Edge 15+

## Credits

- [SQL.js](https://sql.js.org/) — SQLite compiled to WebAssembly
- [Inter](https://rsms.me/inter/) — UI font
- [JetBrains Mono](https://www.jetbrains.com/lp/mono/) — code font

## License

MIT

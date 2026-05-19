# SQL for Everyone — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-file interactive SQL course that teaches non-technical business professionals to write SQL from zero to analyst-level, with live query execution in the browser.

**Architecture:** Single HTML file containing inline CSS and JavaScript. Uses sql.js (SQLite compiled to WebAssembly) for in-browser SQL execution. A compatibility layer rewrites Snowflake/BigQuery syntax to SQLite before execution. Course content is 14 lessons with interactive playgrounds, exercises with hints, progress tracking, theme toggle, PDF export, and completion certificate.

**Tech Stack:** HTML5, CSS3, Vanilla JavaScript, sql.js 1.10.3 (WebAssembly)

---

## File Structure

```
sql-course-for-everyone/
├── index.html                          # The entire course (single file, all tasks modify this)
├── landing.html                        # Marketing landing page (Task 22)
├── docs/
│   └── superpowers/
│       ├── specs/
│       │   ├── 2026-05-19-sql-course-design.md
│       │   ├── 2026-05-19-persona-research.md
│       │   └── 2026-05-19-paid-conversion-research.md
│       └── plans/
│           └── 2026-05-19-sql-course-for-everyone.md  # This file
```

---

## Task 1: HTML Skeleton + CSS Foundation

**Files:**
- Create: `sql-course-for-everyone/index.html`

Build the complete HTML structure: sidebar navigation, main content area, progress bar, theme toggle. All CSS is inline in a `<style>` block. Light theme is default.

- [ ] **Step 1: Create index.html with full CSS**

Create the file with:
- `<!DOCTYPE html>` and meta tags
- Inline `<style>` with all CSS variables for light and dark themes
- Sidebar layout (280px fixed, scrollable, sticky)
- Main content area (max-width 960px, padded)
- Progress bar (fixed top, gradient fill)
- Responsive breakpoint at 900px (sidebar collapses to hamburger)
- Colour-coded concept boxes (analogy/yellow, why/cyan, tip/green, warning/orange)
- Code block styles (dark background, monospace)
- Playground styles (textarea, buttons, results table)
- Exercise styles (bordered box with accent)
- Navigation buttons (prev/next at bottom)
- Result table styles (alternating, hover, null handling)
- Button styles (run/green, reset/outline, hint/yellow)
- Mobile hamburger menu
- Scrollbar styling
- Theme toggle in sidebar footer

- [ ] **Step 2: Verify CSS renders correctly**

Open `index.html` in a browser. Verify:
- Sidebar is 280px fixed on the left
- Main content area is padded and centered
- Progress bar appears at top
- Resize to <900px — sidebar should collapse, hamburger should appear
- Click hamburger — sidebar should overlay

- [ ] **Step 3: Commit**

```bash
cd /Users/samuel/projects/sql-course-for-everyone
git add index.html
git commit -m "feat: HTML skeleton with CSS foundation, sidebar layout, responsive design"
```

---

## Task 2: Database Initialisation + Sample Data

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Add sql.js loading and database setup. All sample data is inserted on page load.

- [ ] **Step 1: Add sql.js script tag and database init**

Add before closing `</body>`:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.10.3/sql-wasm.js"></script>
<script>
let db = null;

async function initDatabase() {
  const SQL = await initSqlJs({
    locateFile: file => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.10.3/${file}`
  });
  db = new SQL.Database();

  // Create tables and insert data here
  db.run(`
    CREATE TABLE customers (
      id INTEGER PRIMARY KEY,
      name TEXT NOT NULL,
      email TEXT,
      city TEXT,
      signup_date TEXT
    );
    -- ... (all 4 tables + INSERT statements)
  `);
}

initDatabase().then(() => {
  // Ready to render lessons
});
</script>
```

- [ ] **Step 2: Add all sample data**

Insert into the `db.run()` call:
- **customers**: 15 rows — names, emails (gmail/outlook/yahoo), cities (Sydney/Melbourne/Brisbane/Perth/Adelaide), signup dates (2023-2024)
- **products**: 15 rows — names (Wireless Headphones, Standing Desk, USB-C Hub, Ergonomic Chair, Webcam HD, Monitor Stand, Mechanical Keyboard, Desk Lamp, Portable SSD 1TB, Notebook Set, Wireless Mouse, Filing Cabinet, Whiteboard, Cable Management Kit, Laptop Stand), prices, categories (Electronics/Furniture/Stationery/Accessories)
- **orders**: 30 rows — customer_id FK, product_id FK, quantity, amount, order_date (2023-2024 spread)
- **employees**: 15 rows — names, departments (Engineering/Marketing/Sales/HR/Finance), salaries, hire_dates

- [ ] **Step 3: Verify database works**

Add a temporary test in the `.then()` callback:
```javascript
const result = db.exec("SELECT COUNT(*) AS cnt FROM customers");
console.log(result);
```
Open browser console — should show `[{columns: ['cnt'], values: [[15]]}]`

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: database init with sql.js, 4 tables, 75 rows of sample data"
```

---

## Task 3: SQL Compatibility Layer

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Add a function that rewrites Snowflake/BigQuery syntax to SQLite before execution.

- [ ] **Step 1: Add translateSQL function**

```javascript
function translateSQL(sql) {
  let translated = sql;

  // DATE_TRUNC('month', col) → strftime('%Y-%m', col)
  translated = translated.replace(
    /DATE_TRUNC\s*\(\s*'month'\s*,\s*([^)]+)\)/gi,
    "strftime('%Y-%m', $1)"
  );

  // DATE_TRUNC('year', col) → strftime('%Y', col)
  translated = translated.replace(
    /DATE_TRUNC\s*\(\s*'year'\s*,\s*([^)]+)\)/gi,
    "strftime('%Y', $1)"
  );

  // DATE_TRUNC('day', col) → date(col)
  translated = translated.replace(
    /DATE_TRUNC\s*\(\s*'day'\s*,\s*([^)]+)\)/gi,
    "date($1)"
  );

  // DATEADD('day', N, col) → date(col, '+N days')
  translated = translated.replace(
    /DATEADD\s*\(\s*'day'\s*,\s*(\d+)\s*,\s*([^)]+)\)/gi,
    "date($2, '+$1 days')"
  );

  // DATEADD('month', N, col) → date(col, '+N months')
  translated = translated.replace(
    /DATEADD\s*\(\s*'month'\s*,\s*(\d+)\s*,\s*([^)]+)\)/gi,
    "date($2, '+$1 months')"
  );

  // DATEDIFF('day', start, end) → julianday(end) - julianday(start)
  translated = translated.replace(
    /DATEDIFF\s*\(\s*'day'\s*,\s*([^,]+)\s*,\s*([^)]+)\)/gi,
    "julianday($2) - julianday($1)"
  );

  // CURRENT_DATE() → date('now')
  translated = translated.replace(/CURRENT_DATE\s*\(\s*\)/gi, "date('now')");

  // ILIKE → LIKE (SQLite is case-insensitive by default)
  translated = translated.replace(/\bILIKE\b/gi, 'LIKE');

  return translated;
}
```

- [ ] **Step 2: Wire translateSQL into query execution**

Update the run function (will be fully built in Task 4) to call `translateSQL()` before `db.exec()`:
```javascript
function executeQuery(sql) {
  const translated = translateSQL(sql);
  return db.exec(translated);
}
```

- [ ] **Step 3: Verify translations work**

Add temporary test calls in the console:
```javascript
console.log(translateSQL("SELECT DATE_TRUNC('month', order_date) FROM orders"));
// Should show: SELECT strftime('%Y-%m', order_date) FROM orders

console.log(translateSQL("SELECT * FROM orders WHERE ILIKE '%test%'"));
// Should show: SELECT * FROM orders WHERE LIKE '%test%'
```

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: SQL compatibility layer — Snowflake/BigQuery syntax rewrites"
```

---

## Task 4: Playground Component

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Build the reusable interactive playground: textarea, Run/Reset/Hint buttons, results table rendering.

- [ ] **Step 1: Add runPlayground function**

```javascript
function runPlayground(btn) {
  const playground = btn.closest('.playground');
  const textarea = playground.querySelector('textarea');
  const resultArea = playground.querySelector('.result-area');
  const sql = textarea.value.trim();

  if (!sql) {
    resultArea.innerHTML = '<div class="message info">Type a query and click Run.</div>';
    return;
  }

  try {
    const results = executeQuery(sql);

    if (!results || results.length === 0) {
      resultArea.innerHTML = '<div class="message success">Query executed. No results to display.</div>';
      markLessonComplete();
      return;
    }

    const res = results[0];
    let html = '<table class="result-table"><thead><tr>';
    res.columns.forEach(c => { html += `<th>${escapeHtml(c)}</th>`; });
    html += '</tr></thead><tbody>';
    res.values.forEach(row => {
      html += '<tr>';
      row.forEach(v => {
        if (v === null) {
          html += '<td class="null-val">NULL</td>';
        } else {
          html += `<td>${escapeHtml(String(v))}</td>`;
        }
      });
      html += '</tr>';
    });
    html += '</tbody></table>';
    html += `<div class="result-meta">${res.values.length} row${res.values.length !== 1 ? 's' : ''} returned</div>`;
    resultArea.innerHTML = html;
    markLessonComplete();
  } catch (err) {
    resultArea.innerHTML = `<div class="message error">Error: ${escapeHtml(err.message)}</div>`;
  }
}
```

- [ ] **Step 2: Add helper functions**

```javascript
function resetPlayground(btn) {
  const playground = btn.closest('.playground');
  const textarea = playground.querySelector('textarea');
  const resultArea = playground.querySelector('.result-area');
  const original = playground.getAttribute('data-query');
  if (original) textarea.value = original;
  resultArea.innerHTML = '';
}

function showHint(btn, hint) {
  const playground = btn.closest('.playground') || btn.closest('.exercise').querySelector('.playground');
  const resultArea = playground.querySelector('.result-area');
  resultArea.innerHTML = `<div class="message info">💡 Hint: ${escapeHtml(hint)}</div>`;
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
```

- [ ] **Step 3: Add Tab key and Cmd+Enter support**

In `initDatabase().then()`, add:
```javascript
document.querySelectorAll('.playground textarea').forEach(ta => {
  ta.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      ta.value = ta.value.substring(0, start) + '  ' + ta.value.substring(end);
      ta.selectionStart = ta.selectionEnd = start + 2;
    }
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      const btn = ta.closest('.playground').querySelector('.btn-run');
      if (btn) runPlayground(btn);
    }
  });
});
```

- [ ] **Step 4: Verify playground works**

Add a test playground to the HTML body temporarily:
```html
<div class="playground" data-query="SELECT * FROM customers LIMIT 3;">
  <div class="playground-header">
    <span class="label">Test</span>
  </div>
  <textarea spellcheck="false">SELECT * FROM customers LIMIT 3;</textarea>
  <div class="playground-actions">
    <button class="btn btn-run" onclick="runPlayground(this)">▶ Run</button>
    <button class="btn btn-reset" onclick="resetPlayground(this)">↺ Reset</button>
  </div>
  <div class="result-area"></div>
</div>
```
Open in browser, click Run — should show 3 rows. Click Reset — should clear. Press Cmd+Enter — should run.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: playground component — run, reset, hint, results table, keyboard shortcuts"
```

---

## Task 5: Navigation + Progress Tracking

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Add sidebar navigation, progress bar, prev/next buttons, and lesson completion tracking.

- [ ] **Step 1: Add lesson data structure and navigation functions**

```javascript
const lessons = [
  { id: 'welcome', title: 'Welcome', icon: '👋' },
  { id: 'select', title: 'SELECT', icon: '📋' },
  { id: 'where', title: 'WHERE', icon: '🔍' },
  { id: 'sorting', title: 'Sorting', icon: '↕️' },
  { id: 'aggregation', title: 'Aggregation', icon: '📊' },
  { id: 'groupby', title: 'GROUP BY', icon: '📈' },
  { id: 'joins', title: 'JOINs', icon: '🔗' },
  { id: 'mini-reports', title: 'Mini Reports', icon: '📄' },
  { id: 'subqueries', title: 'Subqueries', icon: '🔄' },
  { id: 'case-when', title: 'CASE WHEN', icon: '🏷️' },
  { id: 'window', title: 'Window Functions', icon: '🪟' },
  { id: 'ctes', title: 'CTEs', icon: '🧩' },
  { id: 'cheatsheet', title: 'Cheatsheet', icon: '📖' },
  { id: 'whats-next', title: "What's Next", icon: '🚀' }
];

let currentLesson = 0;
const completedLessons = new Set();

function renderNav() {
  const nav = document.getElementById('lessonNav');
  nav.innerHTML = lessons.map((l, i) => `
    <li class="${i === currentLesson ? 'active' : ''} ${completedLessons.has(i) ? 'completed' : ''}"
        onclick="goToLesson(${i})">
      <span class="num">${l.icon}</span>
      ${l.title}
    </li>
  `).join('');
}

function goToLesson(i) {
  currentLesson = i;
  renderLesson();
  window.scrollTo(0, 0);
  document.querySelector('.sidebar').classList.remove('open');
}

function markLessonComplete() {
  completedLessons.add(currentLesson);
  renderNav();
  updateProgress();
}

function updateProgress() {
  const pct = (completedLessons.size / lessons.length) * 100;
  document.getElementById('progressFill').style.width = pct + '%';
}
```

- [ ] **Step 2: Add renderLesson function skeleton**

```javascript
function renderLesson() {
  const content = document.getElementById('lessonContent');
  content.innerHTML = lessons[currentLesson].content();
  renderNav();
  updateProgress();

  // Re-attach keyboard handlers to new textareas
  content.querySelectorAll('.playground textarea').forEach(ta => {
    ta.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        e.preventDefault();
        const start = ta.selectionStart;
        const end = ta.selectionEnd;
        ta.value = ta.value.substring(0, start) + '  ' + ta.value.substring(end);
        ta.selectionStart = ta.selectionEnd = start + 2;
      }
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        e.preventDefault();
        const btn = ta.closest('.playground').querySelector('.btn-run');
        if (btn) runPlayground(btn);
      }
    });
  });
}
```

- [ ] **Step 3: Add lesson content functions to the lessons array**

Update each lesson object to include a `content` function that returns HTML. Start with a placeholder for each:
```javascript
const lessons = [
  { id: 'welcome', title: 'Welcome', icon: '👋', content: () => `<h2>Welcome</h2><p>Lesson content here.</p>` },
  // ... etc
];
```

- [ ] **Step 4: Wire up initDatabase to render first lesson**

```javascript
initDatabase().then(() => {
  renderLesson();
});
```

- [ ] **Step 5: Add keyboard shortcuts for lesson navigation**

```javascript
document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowRight' && e.altKey) {
    if (currentLesson < lessons.length - 1) goToLesson(currentLesson + 1);
  }
  if (e.key === 'ArrowLeft' && e.altKey) {
    if (currentLesson > 0) goToLesson(currentLesson - 1);
  }
});
```

- [ ] **Step 6: Verify navigation works**

Open in browser. Click sidebar items — should update content area. Progress bar should fill as you complete lessons. Alt+Arrow should navigate.

- [ ] **Step 7: Commit**

```bash
git add index.html
git commit -m "feat: sidebar navigation, progress tracking, lesson switching"
```

---

## Task 6: Lesson 0 — Welcome

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Build the Welcome lesson content. Business question: "What is this and why should I care?"

- [ ] **Step 1: Write Welcome lesson content**

Update the `content` function for lesson 0 to include:
- `<h2>` with lesson title
- `<p class="subtitle">` with business question
- Concept box (why): "SQL is just a way to talk to databases. Think of it as asking questions to a very organised filing cabinet."
- `<h3>What you'll learn` with 5 bullet points (pull data, filter, sort, summarise, combine)
- `<h3>How this works` explaining the live editor
- **Concept box (analogy) — "What SQL is NOT":**
  - SQL is not programming — it's asking questions to a database
  - Like using search filters on a spreadsheet, not building an app
  - If you can use Excel filters, you can learn SQL
- Concept box (tip): "All examples use a fictional company's data"
- Playground with `SELECT 'You''re ready to start! 🎉' AS message;`
- Navigation buttons (no Previous, just Next)

- [ ] **Step 2: Verify Welcome lesson**

Open in browser. Should see:
- Title with gradient text
- Concept boxes with correct colours
- "What SQL is NOT" box with yellow border
- Interactive playground with a working query
- Click Run — should show "You're ready to start! 🎉"
- Click Next — should go to lesson 1

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: Welcome lesson — intro, myth-busting, first query"
```

---

## Task 7: Lesson 1 — SELECT

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Business question: "How do I see just the data I need?"

- [ ] **Step 1: Write SELECT lesson content**

Include:
- Subtitle: "Picking the data you want from a table"
- Concept box (analogy): "A database table is just like a spreadsheet. SELECT is you telling someone: go grab me that spreadsheet and show me these specific columns."
- `<h3>See everything` with playground: `SELECT * FROM customers;`
- `<h3>Pick specific columns` with playground: `SELECT name, email, city FROM customers;`
- `<h3>Rename columns for clarity` with playground: `SELECT name AS Customer, email AS "Email Address", city AS Location FROM customers;`
- Concept box (tip): "SELECT * is great for exploring, but in real work, always pick specific columns"
- Exercise: "Show only the product name and price from the products table"
- Hint: `SELECT name, price FROM products;`
- Prev/Next buttons

- [ ] **Step 2: Verify SELECT lesson**

Open in browser, navigate to lesson 1. Run each playground — should show correct columns. Exercise hint should work.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: SELECT lesson — columns, aliases, exercises"
```

---

## Task 8: Lesson 2 — WHERE

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Business question: "How do I find specific records?"

- [ ] **Step 1: Write WHERE lesson content**

Include:
- Concept box (analogy): "If SELECT is picking columns, WHERE is picking rows. Like using the filter button on a spreadsheet."
- `<h3>Exact match` with playground: `SELECT name, email, city FROM customers WHERE city = 'Sydney';`
- `<h3>Comparisons` with playground: `SELECT name, price FROM products WHERE price > 100;`
- `<h3>Multiple conditions` with playground: `SELECT name, price, category FROM products WHERE category = 'Electronics' AND price < 200;`
- `<h3>Handy operators` with schema display showing: =, !=, >, <, >=, <=, AND, OR, NOT, BETWEEN, IN, LIKE, IS NULL/IS NOT NULL
- Playground combining IN + BETWEEN: `SELECT name, category, price FROM products WHERE category IN ('Electronics', 'Furniture') AND price BETWEEN 50 AND 300;`
- Exercise 1: "Find all customers whose city is Melbourne or Brisbane"
- Exercise 2: "Find all products with price between $50 and $150"

- [ ] **Step 2: Verify WHERE lesson**

Run each playground. Verify filtering works. Test exercises.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: WHERE lesson — comparisons, AND/OR, IN, BETWEEN, LIKE, IS NULL"
```

---

## Task 9: Lesson 3 — Sorting

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Business question: "What are my top/bottom results?"

- [ ] **Step 1: Write Sorting lesson content**

Include:
- Concept box (analogy): "ORDER BY is like clicking a column header in a spreadsheet. ASC = ascending (A→Z), DESC = descending (Z→A)."
- `<h3>Sort by price` with playground: `SELECT name, price FROM products ORDER BY price DESC;`
- `<h3>Sort by multiple columns` with playground: `SELECT name, category, price FROM products ORDER BY category ASC, price DESC;`
- `<h3>Limit results` with playground: `SELECT name, price FROM products ORDER BY price DESC LIMIT 5;`
- Concept box (tip): "LIMIT is great for top N questions. In SQL Server, use SELECT TOP 5 instead."
- Exercise: "Show the 3 cheapest products. Display name and price only."
- Hint: `SELECT name, price FROM products ORDER BY price ASC LIMIT 3;`

- [ ] **Step 2: Verify Sorting lesson**

Run each playground. Verify ordering and LIMIT work.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: Sorting lesson — ORDER BY, LIMIT, exercises"
```

---

## Task 10: Lesson 4 — Aggregation

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Business question: "How many? What's the total? What's the average?"

- [ ] **Step 1: Write Aggregation lesson content**

Include:
- Concept box (analogy): "Instead of reading every row, aggregation lets you ask: How many? What's the total? Like SUM and COUNT in a spreadsheet — but way more flexible."
- `<h3>Count rows` with playground: `SELECT COUNT(*) AS total_customers FROM customers;`
- `<h3>Total and average` with playground: `SELECT COUNT(*) AS total_orders, SUM(amount) AS total_revenue, AVG(amount) AS avg_order_value FROM orders;`
- Schema display: COUNT, SUM, AVG, MIN, MAX
- Exercise: "What's the total revenue across all orders?"
- Hint: `SELECT SUM(amount) AS total_revenue FROM orders;`

- [ ] **Step 2: Verify Aggregation lesson**

Run each playground. Verify counts, sums, averages.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: Aggregation lesson — COUNT, SUM, AVG, MIN, MAX"
```

---

## Task 11: Lesson 5 — GROUP BY

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Business question: "How do I summarise by category?"

- [ ] **Step 1: Write GROUP BY lesson content**

Include:
- Concept box (analogy): "GROUP BY splits your data into buckets, then summarises each one. Like a pivot table in Excel."
- `<h3>Group by category` with playground: `SELECT category, COUNT(*) AS product_count, AVG(price) AS avg_price FROM products GROUP BY category;`
- `<h3>Filter groups with HAVING` with playground: `SELECT city, COUNT(*) AS customer_count FROM customers GROUP BY city HAVING customer_count > 2;`
- Concept box (tip): "WHERE filters rows before grouping. HAVING filters groups after grouping."
- Exercise 1: "How many orders has each customer placed?"
- Exercise 2: "Which cities have more than 2 customers?"

- [ ] **Step 2: Verify GROUP BY lesson**

Run each playground. Verify grouping and HAVING work.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: GROUP BY lesson — grouping, HAVING, aggregate filtering"
```

---

## Task 12: Lesson 6 — JOINs

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Business question: "How do I combine data from different tables?"

- [ ] **Step 1: Write JOINs lesson content**

Include:
- Concept box (analogy): "JOIN is like putting two spreadsheets side-by-side, matching rows by a shared ID. Like a mail merge."
- `<h3>Our data model` with schema display showing all 4 tables and their columns
- `<h3>Orders with customer names` with playground: `SELECT c.name AS customer, o.amount, o.order_date FROM orders o JOIN customers c ON o.customer_id = c.id ORDER BY o.order_date DESC;`
- `<h3>Orders with product details` with playground: `SELECT c.name AS customer, p.name AS product, p.category, o.quantity, o.amount FROM orders o JOIN customers c ON o.customer_id = c.id JOIN products p ON o.product_id = p.id ORDER BY o.amount DESC;`
- `<h3>Join + aggregation` with playground: `SELECT c.name AS customer, COUNT(o.id) AS orders, SUM(o.amount) AS total_spent FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.name ORDER BY total_spent DESC;`
- Concept box (tip): "The ON clause tells the database which columns match up."
- Exercise 1: "Show each product name and how many times it's been ordered"
- Exercise 2: "Show total spend per customer, sorted highest first"

- [ ] **Step 2: Verify JOINs lesson**

Run each playground. Verify joins return correct combined data.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: JOINs lesson — INNER JOIN, multi-table, join + aggregation"
```

---

## Task 13: Lesson 7 — Mini Reports (Capstone Checkpoint)

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Business question: "Can I build a real report with what I know?" This is the capstone checkpoint — a "shareable win" moment.

- [ ] **Step 1: Write Mini Reports lesson content**

Include:
- Concept box (why): "You now know enough to build real reports. Let's combine everything you've learned."
- `<h3>💰 Monthly revenue report` with playground:
```sql
SELECT
  strftime('%Y-%m', order_date) AS month,
  COUNT(*) AS orders,
  SUM(amount) AS revenue
FROM orders
GROUP BY month
ORDER BY month;
```
- `<h3>🏆 Top 5 customers by spend` with playground:
```sql
SELECT
  c.name,
  c.city,
  COUNT(o.id) AS orders,
  SUM(o.amount) AS total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.name
ORDER BY total_spent DESC
LIMIT 5;
```
- `<h3>📦 Best-selling products` with playground:
```sql
SELECT
  p.name,
  p.category,
  SUM(o.quantity) AS units_sold,
  SUM(o.amount) AS revenue
FROM orders o
JOIN products p ON o.product_id = p.id
GROUP BY p.name
ORDER BY revenue DESC;
```
- **Capstone checkpoint** — concept box (tip): "🎉 Congratulations! You've just built real business reports. Take a screenshot and share it with your team — you did this yourself!"
- Exercise 1: "Build a report showing revenue by product category"
- Exercise 2: "Find customers who haven't ordered since June 2024" (uses LEFT JOIN + HAVING)

- [ ] **Step 2: Verify Mini Reports lesson**

Run each playground. Verify reports produce correct data. Capstone message should appear.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: Mini Reports lesson — capstone checkpoint, end-to-end reports"
```

---

## Task 14: Lesson 8 — Subqueries

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Business question: "How do I use one query's result in another?"

- [ ] **Step 1: Write Subqueries lesson content**

Include:
- Concept box (analogy): "A subquery is a question inside a question. Like saying: 'Show me everyone who spent more than the average customer.' First you find the average, then you use it."
- `<h3>Subquery in WHERE` with playground:
```sql
SELECT name, email
FROM customers
WHERE id IN (
  SELECT customer_id
  FROM orders
  GROUP BY customer_id
  HAVING SUM(amount) > 300
);
```
- `<h3>Subquery in FROM` with playground:
```sql
SELECT category, avg_price
FROM (
  SELECT category, AVG(price) AS avg_price
  FROM products
  GROUP BY category
)
WHERE avg_price > 100;
```
- Concept box (tip): "Read subqueries from the inside out. The inner query runs first."
- Exercise 1: "Find products that have never been ordered"
- Exercise 2: "Find customers who spent more than the average order amount"

- [ ] **Step 2: Verify Subqueries lesson**

Run each playground. Verify subqueries return correct results.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: Subqueries lesson — WHERE subqueries, FROM subqueries"
```

---

## Task 15: Lesson 9 — CASE WHEN

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Business question: "How do I add labels and buckets to my data?"

- [ ] **Step 1: Write CASE WHEN lesson content**

Include:
- Concept box (analogy): "CASE WHEN is like IF/THEN in Excel. 'If price > 200, label it Premium, otherwise label it Standard.'"
- `<h3>Simple CASE` with playground:
```sql
SELECT
  name,
  price,
  CASE
    WHEN price > 200 THEN 'Premium'
    WHEN price > 50 THEN 'Standard'
    ELSE 'Budget'
  END AS price_tier
FROM products;
```
- `<h3>Conditional aggregation` with playground:
```sql
SELECT
  city,
  COUNT(*) AS total_customers,
  COUNT(CASE WHEN signup_date < '2024-01-01' THEN 1 END) AS pre_2024,
  COUNT(CASE WHEN signup_date >= '2024-01-01' THEN 1 END) AS from_2024
FROM customers
GROUP BY city;
```
- Exercise 1: "Label orders as Small (<$100), Medium ($100-$300), or Large (>$300)"
- Exercise 2: "Count customers per city, split by email domain (gmail vs others)"

- [ ] **Step 2: Verify CASE WHEN lesson**

Run each playground. Verify conditional logic produces correct labels.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: CASE WHEN lesson — simple CASE, conditional aggregation"
```

---

## Task 16: Lesson 10 — Window Functions

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Business question: "How do I rank or compare rows within a group?"

- [ ] **Step 1: Write Window Functions lesson content**

Include:
- Concept box (analogy): "Window functions are like adding a column that knows about the other rows. 'Rank this product within its category' or 'show me the running total.'"
- `<h3>ROW_NUMBER` with playground:
```sql
SELECT
  name,
  category,
  price,
  ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC) AS rank_in_category
FROM products;
```
- `<h3>RANK and DENSE_RANK` with playground:
```sql
SELECT
  name,
  department,
  salary,
  RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS salary_rank
FROM employees;
```
- `<h3>Running total` with playground:
```sql
SELECT
  order_date,
  amount,
  SUM(amount) OVER (ORDER BY order_date) AS running_total
FROM orders;
```
- `<h3>LAG — compare to previous row` with playground:
```sql
SELECT
  order_date,
  amount,
  LAG(amount) OVER (ORDER BY order_date) AS previous_order,
  amount - LAG(amount) OVER (ORDER BY order_date) AS change
FROM orders;
```
- Snowflake note: "In Snowflake, use QUALIFY to filter window functions. In BigQuery, use a subquery."
- Exercise 1: "Rank employees by salary within their department"
- Exercise 2: "Show each order with a running total of revenue per customer"

- [ ] **Step 2: Verify Window Functions lesson**

Run each playground. Verify window functions produce correct rankings and running totals.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: Window Functions lesson — ROW_NUMBER, RANK, SUM OVER, LAG"
```

---

## Task 17: Lesson 11 — CTEs

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Business question: "How do I write complex queries that I can actually read?"

- [ ] **Step 1: Write CTEs lesson content**

Include:
- Concept box (analogy): "A CTE (WITH clause) is like giving a subquery a name. Instead of nesting queries inside each other, you define them at the top and reference them by name. Like variables in a formula."
- `<h3>Basic CTE` with playground:
```sql
WITH customer_totals AS (
  SELECT
    customer_id,
    SUM(amount) AS total_spent
  FROM orders
  GROUP BY customer_id
)
SELECT
  c.name,
  ct.total_spent
FROM customer_totals ct
JOIN customers c ON ct.customer_id = c.id
ORDER BY ct.total_spent DESC;
```
- `<h3>Multiple CTEs` with playground:
```sql
WITH monthly_revenue AS (
  SELECT
    strftime('%Y-%m', order_date) AS month,
    SUM(amount) AS revenue
  FROM orders
  GROUP BY month
),
avg_monthly AS (
  SELECT AVG(revenue) AS avg_rev FROM monthly_revenue
)
SELECT
  mr.month,
  mr.revenue,
  am.avg_rev,
  CASE WHEN mr.revenue > am.avg_rev THEN 'Above average' ELSE 'Below average' END AS performance
FROM monthly_revenue mr, avg_monthly am
ORDER BY mr.month;
```
- Concept box (tip): "CTEs don't make queries faster — they make them readable. Use them when a subquery is getting hard to follow."
- Exercise 1: "Refactor the subquery from lesson 8 into a CTE"
- Exercise 2: "Build a report: top 3 products by revenue per category using a CTE"

- [ ] **Step 2: Verify CTEs lesson**

Run each playground. Verify CTEs produce correct results.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: CTEs lesson — WITH clause, multiple CTEs, readability"
```

---

## Task 18: Lesson 12 — Cheatsheet

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Business question: "What's the syntax again?" No exercises — dense reference.

- [ ] **Step 1: Write Cheatsheet lesson content**

Include sections:
- **Query skeleton** — the full SELECT → FROM → JOIN → WHERE → GROUP BY → HAVING → ORDER → LIMIT template in a code block
- **Comparison operators** — schema display: =, !=, >, <, BETWEEN, IN, LIKE, IS NULL, AND/OR/NOT
- **Aggregate functions** — schema display: COUNT, SUM, AVG, MIN, MAX
- **Date functions** — schema display with Snowflake + BigQuery columns: DATE_TRUNC, DATEADD, DATEDIFF, CURRENT_DATE
- **String functions** — SUBSTRING, UPPER/LOWER, TRIM, CONCAT, REPLACE
- **CASE WHEN** — simple and searched syntax
- **Window functions** — ROW_NUMBER, RANK, DENSE_RANK, SUM() OVER, LAG/LEAD with PARTITION BY + ORDER BY pattern
- **CTEs** — WITH clause syntax, multiple CTEs, chaining
- **Common patterns** — "Top N per group", "Running total", "Month-over-month", "Deduplicate"
- **Common mistakes** — = NULL vs IS NULL, WHERE vs HAVING, missing GROUP BY, wrong JOIN type

- [ ] **Step 2: Verify Cheatsheet**

Open in browser. Verify all sections render, code blocks are readable, schema displays are formatted.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: Cheatsheet lesson — full SQL reference card"
```

---

## Task 19: Lesson 13 — What's Next

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Business question: "Where do I go from here?" No exercises — resources and encouragement.

- [ ] **Step 1: Write What's Next lesson content**

Include:
- Congratulatory message: "You've completed SQL for Everyone. You can now write queries that would have taken a data analyst days to pull."
- **What you can now do** — recap of skills learned (pull data, filter, aggregate, join, subquery, window functions, CTEs)
- **External resources** with links:
  - dbt (data transformation) — https://www.getdbt.com/
  - Looker (reporting) — https://cloud.google.com/looker
  - Power BI SQL — https://powerbi.microsoft.com/
  - Mode Analytics SQL tutorial — https://mode.com/sql-tutorial/
  - Snowflake documentation — https://docs.snowflake.com/
  - BigQuery documentation — https://cloud.google.com/bigquery/docs
- **Communities:**
  - dbt Slack — https://www.getdbt.com/community
  - Locally Optimistic — https://locallyoptimistic.com/
- **Your next steps:** "Pick a real question from your work. Write the query. Run it. Share the result. That's how you learn."
- Prev button (back to Cheatsheet), no Next button

- [ ] **Step 2: Verify What's Next**

Open in browser. Verify links are clickable, content renders correctly.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: What's Next lesson — external resources, communities, next steps"
```

---

## Task 20: Theme Toggle

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Add light/dark theme toggle. Light is default.

- [ ] **Step 1: Add theme toggle CSS variables**

Add to the `<style>` block:
```css
:root {
  /* Light theme (default) */
  --bg: #ffffff;
  --surface: #f8f9fa;
  --surface2: #e9ecef;
  --border: #dee2e6;
  --text: #212529;
  --text-dim: #6c757d;
  /* ... other light theme vars */
}

[data-theme="dark"] {
  --bg: #0f1117;
  --surface: #1a1d27;
  --surface2: #232736;
  --border: #2d3148;
  --text: #e2e4ef;
  --text-dim: #8b8fa8;
  /* ... other dark theme vars */
}
```

- [ ] **Step 2: Add toggle button and function**

Add to sidebar footer:
```html
<button class="theme-toggle" onclick="toggleTheme()" id="themeBtn">🌙 Dark mode</button>
```

Add JavaScript:
```javascript
function toggleTheme() {
  const body = document.body;
  const btn = document.getElementById('themeBtn');
  if (body.getAttribute('data-theme') === 'dark') {
    body.removeAttribute('data-theme');
    btn.textContent = '🌙 Dark mode';
    localStorage.setItem('theme', 'light');
  } else {
    body.setAttribute('data-theme', 'dark');
    btn.textContent = '☀️ Light mode';
    localStorage.setItem('theme', 'dark');
  }
}

// Load saved theme on init
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
  document.body.setAttribute('data-theme', 'dark');
  document.getElementById('themeBtn').textContent = '☀️ Light mode';
}
```

- [ ] **Step 3: Verify theme toggle**

Open in browser. Click toggle — should switch between light and dark. Refresh — should remember preference.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: light/dark theme toggle with localStorage persistence"
```

---

## Task 21: PDF Export + Completion Certificate

**Files:**
- Modify: `sql-course-for-everyone/index.html`

Add "Download PDF" button and auto-generated completion certificate.

- [ ] **Step 1: Add PDF export using window.print()**

Add a "Download PDF" button in the sidebar:
```html
<button class="btn btn-outline" onclick="exportPDF()" style="margin-top:12px;width:100%;">📄 Download PDF</button>
```

Add print styles and function:
```javascript
function exportPDF() {
  // Show all lessons for printing
  const content = document.getElementById('lessonContent');
  const original = content.innerHTML;

  let allContent = '';
  lessons.forEach((l, i) => {
    allContent += `<div class="print-lesson" style="page-break-after:always;">${l.content()}</div>`;
  });
  content.innerHTML = allContent;

  window.print();

  // Restore current lesson
  content.innerHTML = original;
  renderLesson();
}
```

Add print CSS:
```css
@media print {
  .sidebar { display: none !important; }
  .playground-actions { display: none !important; }
  .result-area { display: none !important; }
  .btn-nav { display: none !important; }
  .progress-bar { display: none !important; }
  .theme-toggle { display: none !important; }
  .print-lesson { page-break-after: always; }
  body { background: white !important; color: black !important; }
}
```

- [ ] **Step 2: Add completion certificate**

Add a certificate generator that triggers when all lessons are completed:
```javascript
function generateCertificate() {
  const name = prompt('Enter your name for the certificate:');
  if (!name) return;

  const today = new Date().toLocaleDateString('en-AU', {
    day: 'numeric', month: 'long', year: 'numeric'
  });

  const cert = `
    <div style="text-align:center; padding:60px; font-family:Georgia,serif;">
      <h1 style="font-size:28px; color:#1a365d;">Certificate of Completion</h1>
      <p style="font-size:16px; color:#4a5568;">This certifies that</p>
      <h2 style="font-size:32px; color:#2d3748; margin:20px 0;">${escapeHtml(name)}</h2>
      <p style="font-size:16px; color:#4a5568;">has completed</p>
      <h3 style="font-size:24px; color:#2b6cb0;">SQL for Everyone</h3>
      <p style="font-size:14px; color:#718096; margin-top:40px;">${today}</p>
    </div>
  `;

  const win = window.open('', '_blank');
  win.document.write(`<html><head><title>Certificate</title></head><body>${cert}</body></html>`);
  win.document.close();
  win.print();
}
```

Update `markLessonComplete` to check for all-complete:
```javascript
function markLessonComplete() {
  completedLessons.add(currentLesson);
  renderNav();
  updateProgress();

  if (completedLessons.size === lessons.length) {
    setTimeout(() => {
      if (confirm('🎉 You completed all lessons! Generate your certificate?')) {
        generateCertificate();
      }
    }, 500);
  }
}
```

- [ ] **Step 3: Verify PDF and certificate**

Open in browser. Complete all lessons. Should prompt for certificate. Print dialog should appear. PDF export should show all lessons.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: PDF export and completion certificate generator"
```

---

## Task 22: Landing Page

**Files:**
- Create: `sql-course-for-everyone/landing.html`

Build a simple marketing landing page with pricing and CTA.

- [ ] **Step 1: Create landing.html**

Build a single-page marketing site:
- Hero section: "SQL for Everyone — Learn to answer your own data questions"
- Subtitle: "No analyst required. No coding experience needed."
- CTA button: "Start Learning — $89" (links to index.html)
- **What you'll learn** — 5 bullet points with icons
- **Who it's for** — marketing, finance, ops, HR, sales professionals
- **How it works** — interactive editor, real SQL, instant results
- **Pricing** — $89 individual, $59/seat team pack (5+)
- **FAQ** — "Do I need coding experience?", "How long does it take?", "Can I expense this?"
- Footer with copyright

- [ ] **Step 2: Style landing page**

Use the same CSS variables and design language as the course. Clean, professional, minimal.

- [ ] **Step 3: Verify landing page**

Open landing.html in browser. CTA should link to index.html. Responsive on mobile.

- [ ] **Step 4: Commit**

```bash
git add landing.html
git commit -m "feat: marketing landing page with pricing and CTA"
```

---

## Task 23: Final Integration Test

**Files:**
- Modify: `sql-course-for-everyone/index.html` (if fixes needed)

Run through the entire course as a learner would.

- [ ] **Step 1: Test full course flow**

Open index.html in browser. Go through every lesson:
1. Welcome — run the intro query ✓
2. SELECT — run each playground, complete exercise ✓
3. WHERE — run each playground, complete exercises ✓
4. Sorting — run each playground, complete exercise ✓
5. Aggregation — run each playground, complete exercise ✓
6. GROUP BY — run each playground, complete exercises ✓
7. JOINs — run each playground, complete exercises ✓
8. Mini Reports — run each playground, verify capstone message ✓
9. Subqueries — run each playground, complete exercises ✓
10. CASE WHEN — run each playground, complete exercises ✓
11. Window Functions — run each playground, complete exercises ✓
12. CTEs — run each playground, complete exercises ✓
13. Cheatsheet — verify all sections render ✓
14. What's Next — verify links work ✓

- [ ] **Step 2: Test edge cases**

- Run an invalid query — should show friendly error
- Run empty query — should show "Type a query" message
- Use Cmd+Enter to run — should work
- Toggle theme — should persist on refresh
- Resize to mobile — sidebar should collapse
- Complete all lessons — certificate prompt should appear

- [ ] **Step 3: Test Snowflake/BigQuery syntax**

Run these queries to verify the compatibility layer:
- `SELECT DATE_TRUNC('month', order_date) FROM orders LIMIT 1;`
- `SELECT DATEADD('day', 30, order_date) FROM orders LIMIT 1;`
- `SELECT DATEDIFF('day', '2024-01-01', '2024-01-31');`
- `SELECT CURRENT_DATE();`

- [ ] **Step 4: Fix any issues found**

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "fix: integration test fixes and final polish"
```

---

## Success Criteria Checklist

| # | Criterion | Verified |
|---|-----------|----------|
| 1 | Single HTML file opens in any modern browser with no setup | [ ] |
| 2 | All 14 lessons render with interactive SQL editor | [ ] |
| 3 | Queries execute and return results correctly | [ ] |
| 4 | Snowflake/BigQuery syntax works via compatibility layer | [ ] |
| 5 | Light/dark theme toggle works | [ ] |
| 6 | Exercises have hints that reveal answers | [ ] |
| 7 | Progress tracking persists during session | [ ] |
| 8 | Mobile responsive (sidebar collapses) | [ ] |
| 9 | Course feels friendly and approachable, not intimidating | [ ] |
| 10 | Welcome lesson explicitly addresses "fear of coding" barrier | [ ] |
| 11 | Each lesson framed as a business question, not a SQL concept | [ ] |
| 12 | Difficulty progression is smooth — no cliff between GROUP BY and subqueries | [ ] |
| 13 | "What's Next" section provides clear path for continued learning | [ ] |
| 14 | PDF export generates a branded, printable version of the course | [ ] |
| 15 | Completion certificate auto-generates with learner's name and date | [ ] |
| 16 | Capstone checkpoint at lesson 7 creates a "shareable win" moment | [ ] |
| 17 | Landing page exists with clear CTA and pricing ($89 individual) | [ ] |

# R Scraper Codebase Review Report

**Date:** 2026-06-02
**Files reviewed:** 5 (`indeed review.R`, `realestate sold.R`, `realestate_com_au.R`, `mongolite.R`, `zomato.R`)
**Findings:** 10 critical, 39 warnings, 12 info

---

## 1. Executive Summary

The codebase has **systemic reliability problems** across all scrapers: no user-agent headers, brittle CSS selectors with no fallback, hardcoded pagination counts, and silent data loss from missing length validation before column binding. Two scripts (`zomato.R`, `mongolite.R`) also contain dead/demo code mixed with production logic. Fixing the 10 critical issues will prevent silent data corruption; the warnings represent hardening that should follow immediately after.

---

## 2. Critical Issues

### C1. Column binding without length validation (3 files)

Silent recycling is the most dangerous bug — it produces plausible-looking but completely wrong data.

**Files:** `indeed review.R:43`, `realestate sold.R:61`, `realestate_com_au.R:49`

**Before** (`indeed review.R`):
```r
df <- tibble(
  job_title = job_title_df$job_title,
  location  = location_df$location,
  date      = date_df$date,
  text      = text_df$text
)
```

**After:**
```r
n <- length(job_titles)
stopifnot(
  length(locations) == n,
  length(dates) == n,
  length(texts) == n
)
df <- tibble(job_title = job_titles, location = locations, date = dates, text = texts)
```

For `realestate sold.R`, the better fix is to parse a card-level node first, then extract sub-fields within each card — this makes mismatched lengths structurally impossible.

---

### C2. Hardcoded pagination counts (3 files)

Scripts assume a fixed number of pages. Site changes silently truncate data or cause 404 loops.

| File | Hardcoded value | Fix |
|---|---|---|
| `indeed review.R:13` | `seq(0, 100, 20)` | Loop until zero reviews returned |
| `realestate sold.R:23` | `4754` total count | Parse pagination element on page 1 |
| `realestate_com_au.R:18` | `129` pages | Loop until empty result, add safety cap |

**After** (`realestate_com_au.R` example):
```r
MAX_PAGES <- 500  # safety cap
page <- 1
repeat {
  results <- scrape_page(page)
  if (length(results) == 0 || page >= MAX_PAGES) break
  house_results[[page]] <- results
  page <- page + 1
}
```

---

### C3. Price parsing produces silent garbage (`realestate sold.R:112`)

Stripping all alpha chars from `"$1.2M-$1.4M"` yields `"1.21.4"` — a meaningless number.

**After:**
```r
sold <- sold %>%
  mutate(
    price_type = case_when(
      str_detect(raw_price, regex("contact|auction|poa", ignore_case = TRUE)) ~ "non_numeric",
      str_detect(raw_price, "\\$.*-.*\\$") ~ "range",
      TRUE ~ "numeric"
    ),
    price_min = case_when(
      price_type == "range" ~ parse_number(str_extract(raw_price, "^\\$[\\d.]+[MmKk]?")),
      price_type == "numeric" ~ parse_number(raw_price),
      TRUE ~ NA_real_
    ),
    price_max = case_when(
      price_type == "range" ~ parse_number(str_extract(raw_price, "(?<=-)\\$[\\d.]+[MmKk]?")),
      price_type == "numeric" ~ price_min,
      TRUE ~ NA_real_
    )
  )
```

---

### C4. Empty search result causes crash (`zomato.R:27`)

**Before:**
```r
mugen <- zomato_search(...)
city_id <- mugen$id[1]  # errors if 0-row result
```

**After:**
```r
mugen <- zomato_search(...)
if (nrow(mugen) == 0) stop("No Zomato results found for search term")
city_id <- mugen$id[1]
```

---

### C5. Missing `na.rm = TRUE` (`zomato.R:69`)

**Before:**
```r
mean(syd$average_cost_for_two)
median(syd$average_cost_for_two)
```

**After:**
```r
n_na <- sum(is.na(syd$average_cost_for_two))
if (n_na > 0) message(n_na, " rows have NA average_cost_for_two")
mean(syd$average_cost_for_two, na.rm = TRUE)
median(syd$average_cost_for_two, na.rm = TRUE)
```

---

### C6. Empty price string produces empty from/to columns (`realestate_com_au.R:100`)

**After** — insert after the `gsub` chain:
```r
price_new[!nzchar(price_new)] <- NA_character_
```

---

## 3. Cross-Cutting Patterns

### Pattern A: No User-Agent header (4 of 5 files)

Every scraper uses default `rvest`/`httr` user-agents. Sites fingerprint and block these trivially.

**Fix — create a shared helper:**
```r
# helpers/scrape_utils.R
fetch_page <- function(url, agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36") {
  resp <- httr::GET(url, httr::user_agent(agent))
  httr::stop_for_status(resp)
  xml2::read_html(resp)
}
```

Affected: `indeed review.R:19`, `realestate sold.R:30`, `realestate_com_au.R:23`.

---

### Pattern B: Silent failure in tryCatch (3 files)

`tryCatch` catches R errors but not HTTP 403/404. The scraper stores empty tibbles and moves on.

**Fix:**
```r
page_data <- tryCatch({
  webpage <- fetch_page(url)
  nodes <- html_nodes(webpage, selector)
  if (length(nodes) == 0) {
    warning("Page ", page, ": selector returned 0 nodes — possible site change")
    return(NULL)
  }
  # ... parse ...
}, error = function(e) {
  warning("Page ", page, " failed: ", conditionMessage(e))
  return(NULL)
})
```

Add a failed-page tracker and report summary after the loop.

---

### Pattern C: Hardcoded config scattered through logic (5 files)

URLs, coordinates, entity IDs, sleep durations, and CSS selectors are magic numbers inline.

**Fix:** Each script should have a config block at the top:
```r
# Config
cfg <- list(
  base_url = "https://www.realestate.com.au/sold/in-melbourne+-+greater+region,+vic/list-",
  per_page = 25,
  sleep_sec = runif(1, 1.5, 3.5),
  user_agent = "Mozilla/5.0 ..."
)
```

---

### Pattern D: Brittle CSS selectors with no validation (4 files)

Every `html_nodes()` call assumes the selector still works. A site class rename breaks the entire run silently.

**Fix:** After every `html_nodes()` call:
```r
nodes <- html_nodes(webpage, ".some-class")
if (length(nodes) == 0) {
  warning("Selector '.some-class' matched 0 nodes on page ", page, " — may have changed")
}
```

---

## 4. Per-File Breakdown

### `indeed review.R`

| Severity | Line | Issue | Effort |
|---|---|---|---|
| CRITICAL | 43 | Column binding without length check | medium |
| CRITICAL | 13 | Hardcoded page range (0–100) | medium |
| WARNING | 51 | tryCatch misses HTTP errors | low |
| WARNING | 19 | No User-Agent | low |
| WARNING | 19 | Hardcoded company name/URL | low |
| WARNING | 13 | Magic numbers for pagination | low |
| WARNING | 25 | Fragile CSS selectors | medium |
| WARNING | 10 | `source(_config.R)` without docs | low |
| INFO | 24 | Intermediate tibble pattern unnecessary | low |
| INFO | 55 | Unconditional sleep on failure | low |

---

### `realestate sold.R`

| Severity | Line | Issue | Effort |
|---|---|---|---|
| CRITICAL | 61 | Column binding without length check | medium |
| CRITICAL | 23 | Hardcoded total count (4754) | medium |
| CRITICAL | 112 | Price parsing produces garbage for ranges/text | medium |
| WARNING | 30 | Silent page failures, no summary | medium |
| WARNING | 30 | No User-Agent | low |
| WARNING | 75 | Fixed delay, no backoff | low |
| WARNING | 30 | No selector validation | low |
| WARNING | 18 | Hardcoded URL structure | low |
| WARNING | 85 | Copy-on-modify dataframe churn | medium |
| WARNING | 113 | Sequential gsub calls | low |
| WARNING | 141 | `has_price` uses 0/1 not logical | low |
| WARNING | 209 | Missing `na.rm = TRUE` | low |
| INFO | 11 | _config.R may contain secrets | low |
| INFO | 1 | Monolithic script, should split | high |
| INFO | 150 | Hardcoded year filters | low |

---

### `realestate_com_au.R`

| Severity | Line | Issue | Effort |
|---|---|---|---|
| CRITICAL | 49 | No row-count validation before binding | low |
| CRITICAL | 100 | Empty price string not set to NA | low |
| CRITICAL | 18 | Hardcoded 129 pages | medium |
| WARNING | 23 | No User-Agent | low |
| WARNING | 25 | All selectors class-based, fragile | medium |
| WARNING | 58 | Silent page failures | medium |
| WARNING | 16 | List not pre-allocated | low |
| WARNING | 83 | 12 sequential gsub calls | medium |
| WARNING | 13 | Magic numbers in logic | low |
| WARNING | 112 | Positional feature parsing — very fragile | high |
| WARNING | 10 | No _config.R existence check | low |
| WARNING | 19 | `print()` instead of `message()` | low |
| INFO | 72 | URL prefix added post-scrape | low |
| INFO | 62 | Fixed delay, no jitter | low |
| INFO | 67 | Debug `View()` calls left in | low |

---

### `mongolite.R`

| Severity | Line | Issue | Effort |
|---|---|---|---|
| WARNING | 17 | Dead diamonds demo code in production | low |
| WARNING | 43 | Overly broad search term `q='data'` | low |
| WARNING | 45 | Magic number timeout and collection name | low |
| WARNING | 53 | No guard against empty tibble | low |
| WARNING | 67 | No row-count verification after insert | low |
| WARNING | 76 | tempfile() never cleaned up | low |
| WARNING | 77 | file() connection never closed | low |
| WARNING | 91 | Unconditional `m$drop()` destroys data | low |
| WARNING | 84 | `m$find()` loads entire collection | low |
| WARNING | 11 | _config.R may contain credentials | low |
| INFO | 66 | No explicit db parameter on `mongo()` | low |

---

### `zomato.R`

| Severity | Line | Issue | Effort |
|---|---|---|---|
| CRITICAL | 27 | Index empty search result without check | low |
| CRITICAL | 69 | `mean()`/`median()` without `na.rm` | low |
| WARNING | 75 | ggplot bypasses dataframe, refs parent env | low |
| WARNING | 78 | Same direct-reference anti-pattern on boxplot | low |
| WARNING | 29 | `message()` on failure swallows error | low |
| WARNING | 26 | Magic number coordinates and entity IDs | low |
| WARNING | 73 | `as.data.frame()` produces bad column name | low |
| INFO | 24 | Demo code mixed with analysis | medium |
| INFO | 52 | No pagination handling on search | medium |
| INFO | 67 | Exploratory calls left in production | low |

---

## 5. Quick Wins

These are **low-effort, high-impact** fixes that can be done in under 30 minutes each:

| # | Fix | Files | Impact |
|---|---|---|---|
| 1 | Add `stopifnot(length(...) == n)` before every `tibble()` column bind | indeed, realestate sold, realestate_com_au | Prevents silent data corruption |
| 2 | Add `na.rm = TRUE` to all `mean()`/`median()`/`min()`/`max()` calls | zomato, realestate sold | Prevents NA propagation |
| 3 | Set `price_new[!nzchar(price_new)] <- NA_character_` after gsub chain | realestate_com_au | Prevents empty string bugs |
| 4 | Guard `mugen$id[1]` with `nrow() == 0` check | zomato | Prevents runtime crash |
| 5 | Replace `print()` with `message()` for progress logging | realestate_com_au | Enables `suppressMessages()` |
| 6 | Add `on.exit(unlink(tmp))` after `tempfile()` | mongolite | Prevents temp file leaks |
| 7 | Wrap `m$drop()` in a flag or remove it | mongolite | Prevents accidental data loss |
| 8 | Set `price_new[!nzchar(price_new)] <- NA_character_` | realestate_com_au | Prevents empty from/to columns |
| 9 | Create shared `fetch_page()` helper with user-agent | all scrapers | Unblocks all sites that block default agents |
| 10 | Add `if (!file.exists(...)) stop()` before `source(_config.R)` | realestate_com_au | Clear error on missing config |

---

## 6. Recommended Refactor

### Extract a shared scraping utility

All four scrapers repeat the same pattern: fetch page, parse nodes, validate lengths, sleep, handle errors. This should be a shared helper.

**Proposed:** `helpers/scrape_utils.R`

```r
#' Fetch a page with a realistic user-agent and error checking
fetch_page <- function(url, agent = getOption("scraper.agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")) {
  resp <- httr::GET(url, httr::user_agent(agent))
  httr::stop_for_status(resp)
  xml2::read_html(resp)
}

#' Parse nodes and validate non-empty
parse_nodes <- function(page, selector, page_num = NULL) {
  nodes <- html_nodes(page, selector)
  if (length(nodes) == 0) {
    msg <- paste0("Selector '", selector, "' returned 0 nodes")
    if (!is.null(page_num)) msg <- paste0(msg, " on page ", page_num)
    warning(msg)
  }
  nodes
}

#' Safe column bind with length validation
safe_bind_cols <- function(...) {
  cols <- list(...)
  lens <- vapply(cols, length, integer(1))
  if (length(unique(lens[lens > 0])) > 1) {
    stop("Column length mismatch: ", paste(names(cols), lens, sep = "=", collapse = ", "))
  }
  tibble::as_tibble(cols)
}

#' Paginate until empty result
paginate <- function(scrape_fn, max_pages = 500, sleep_fn = function() Sys.sleep(runif(1, 1.5, 3.5))) {
  results <- list()
  page <- 1
  repeat {
    batch <- scrape_fn(page)
    if (is.null(batch) || length(batch) == 0 || nrow(batch) == 0) break
    results[[page]] <- batch
    message("Page ", page, ": ", nrow(batch), " rows")
    page <- page + 1
    if (page > max_pages) break
    sleep_fn()
  }
  dplyr::bind_rows(results)
}
```

This eliminates the 4 most common bug patterns across all files.

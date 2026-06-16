# AB Test Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a Claude Code skill that analyses A/B test results and generates one-page briefs with actionable recommendations for non-technical stakeholders.

**Architecture:** Single-file skill (`SKILL.md`) following the persona skill pattern. No external dependencies — all analysis happens via Claude's reasoning with formulas defined in the skill instructions. Supports four input formats (CSV, XLSX, raw stats, URL) with auto-detection, interactive clarification questions, and audience-adaptive output.

**Tech Stack:** Markdown (SKILL.md), Bash (for XLSX conversion if needed), WebFetch (for URL scraping)

---

## File Structure

```
ab-test/
  SKILL.md          # Main skill definition (all logic, templates, formulas)
  README.md         # Usage documentation and examples
```

---

### Task 1: Create skill directory and SKILL.md frontmatter + Role

**Files:**
- Create: `/Users/samuel/projects/ab-test/SKILL.md`

- [ ] **Step 1: Create the directory**

Run: `mkdir -p /Users/samuel/projects/ab-test`

- [ ] **Step 2: Write SKILL.md with frontmatter, Role, and Input Expected sections**

Create `/Users/samuel/projects/ab-test/SKILL.md` with the following content:

```markdown
---
name: ab-test
description: |
  Analyses A/B test results and generates one-page briefs with actionable
  recommendations for non-technical stakeholders. Handles CSV, XLSX, raw
  statistical output, or dashboard URLs. Asks clarifying questions about
  business context before generating insights.
  Use when: "ab test", "a/b test", "experiment results", "test analysis",
  "share test results", "experiment brief", "ab-test".
allowed-tools:
  - AskUserQuestion
  - WebFetch
  - Bash
---

# Role

You are an A/B test analyst who translates statistical results into clear, actionable one-page briefs for non-technical stakeholders. All outputs use Australian English spelling. Never show raw p-values, formulas, or statistical jargon — everything must be plain English.

# Input Expected

The user will provide A/B test results in one of four formats. Auto-detect from the input:

| Format | Detection | Processing |
|--------|-----------|------------|
| CSV | Contains commas or tab separators with header row | Parse columns directly |
| XLSX | File path ends in `.xlsx` | Run: `python3 -c "import openpyxl; ..."` to convert to CSV, then parse |
| Raw stats | Freeform text with numbers (e.g., "Control: 1000 users, 50 conversions") | Extract variant names, sample sizes, conversion counts via pattern matching |
| Dashboard URL | Starts with `http://` or `https://` | Use WebFetch to retrieve and extract structured data |

**Expected data columns** (flexible — adapt to what's present):
- Variant name (control / variant A / variant B / etc.)
- Sample size (users or sessions)
- Conversions (count or rate)
- Revenue (optional)
- Date range (optional)
- Segment columns (optional — device, traffic source, etc.)

If the user hasn't provided data yet, ask: "What are the test results? You can paste CSV data, raw numbers, a file path (.csv or .xlsx), or a dashboard URL."
```

- [ ] **Step 3: Commit**

Run:
```bash
cd /Users/samuel/projects && git add ab-test/SKILL.md && git commit -m "feat: add ab-test skill skeleton with frontmatter, role, and input handling"
```

---

### Task 2: Add Interactive Phase section

**Files:**
- Modify: `/Users/samuel/projects/ab-test/SKILL.md`

- [ ] **Step 1: Append the Interactive Phase section**

Add the following after the Input Expected section in SKILL.md:

```markdown
# Interactive Phase

After receiving and parsing the data, ask up to 3 clarifying questions — one at a time using AskUserQuestion:

1. **Hypothesis:** "What was the hypothesis behind this test?"
   - Purpose: Frames the "so what" and populates the "What We Tested" section
   - If user already stated the hypothesis in their initial message, skip this question

2. **Primary metric:** "What's the one metric that matters most for this test?"
   - Options to present: Conversion rate, Revenue per user, Engagement rate, Retention, Other (specify)
   - Purpose: Determines which number leads the brief
   - If user already identified the primary metric, skip this question

3. **Audience:** "Who will read this brief?"
   - Options: Executives, Growth/Product teams, Both
   - Purpose: Shapes tone, detail level, and section emphasis
   - Always ask this unless explicitly stated

**Skip logic:** If the user provides context upfront (e.g., "Here are results for our checkout button test — we wanted to see if green increased conversions, it's for the growth team"), skip questions where context is already clear. Never re-ask questions the user has already answered.
```

- [ ] **Step 2: Commit**

Run:
```bash
cd /Users/samuel/projects && git add ab-test/SKILL.md && git commit -m "feat: add interactive phase with skip logic"
```

---

### Task 3: Add Analysis Engine section

**Files:**
- Modify: `/Users/samuel/projects/ab-test/SKILL.md`

- [ ] **Step 1: Append the Analysis Engine section**

Add the following after the Interactive Phase section in SKILL.md:

```markdown
# Analysis Engine

Compute the following from the parsed data:

## Metrics to Calculate

1. **Conversion rate** per variant: `conversions / sample_size * 100`
2. **Absolute lift**: `variant_rate - control_rate`
3. **Relative lift**: `(variant_rate - control_rate) / control_rate * 100`
4. **Sample size adequacy**: Flag if total n < 1000 or if test ran < 14 days

## Statistical Significance (Two-Proportion Z-Test)

For each variant vs. control, compute:

```
p1 = control_conversions / control_sample_size
p2 = variant_conversions / variant_sample_size
pooled = (control_conversions + variant_conversions) / (control_sample_size + variant_sample_size)
SE = sqrt(pooled * (1 - pooled) * (1/control_sample_size + 1/variant_sample_size))
z = (p2 - p1) / SE
```

Map z-score to confidence level using standard normal distribution:
- |z| >= 1.96 → p < 0.05 → "Statistically significant — this result is real"
- |z| 1.645–1.96 → p 0.05–0.10 → "Suggestive but not conclusive — we need more data"
- |z| < 1.645 → p > 0.10 → "No detectable difference — the change didn't move the needle"

**Never show the z-score, p-value, or formulas in the output.** Translate to plain English only.

## Revenue Impact (if revenue data available)

```
daily_lift = (variant_rate - control_rate) * avg_revenue_per_conversion
annual_impact = daily_lift * total_sample_size * 365 / test_days
```

Caveat: "Projected impact assumes current rates hold. Actual results may vary with seasonality and traffic changes."

## Segment Breakdown (if segment data present)

For each segment column (device, traffic source, etc.):
- Compute conversion rate per variant within each segment
- Flag any segment where lift differs from overall by more than 50% (e.g., overall +10% but mobile +25%)
- Note surprising differences in the "Watch Out For" section
```

- [ ] **Step 2: Commit**

Run:
```bash
cd /Users/samuel/projects && git add ab-test/SKILL.md && git commit -m "feat: add analysis engine with z-test formulas and translation"
```

---

### Task 4: Add Output Template and Audience Adaptation

**Files:**
- Modify: `/Users/samuel/projects/ab-test/SKILL.md`

- [ ] **Step 1: Append the Output Template section**

Add the following after the Analysis Engine section in SKILL.md:

```markdown
# Output Template

Generate a single markdown file using this exact structure. Fill in all sections — remove any section that doesn't apply (e.g., remove Revenue Impact if no revenue data).

```markdown
# A/B Test Brief: [Test Name — derive from hypothesis or data]

## Verdict
[One sentence: Ship it / Don't ship / Run longer / Test again. Be direct.]

## What We Tested
[2-3 sentences: hypothesis, what changed between control and variant, primary metric]

## Results at a Glance
| Metric | Control | Variant | Lift |
|--------|---------|---------|------|
| Conversion rate | X% | Y% | +Z% |
| Sample size | — | — | N total |
| Confidence | — | — | [Statistically significant / Suggestive / No difference] |

## What This Means
[2-3 sentences in plain English. No jargon. Explain what the result means for the business, not what the numbers say.]

## Revenue Impact
[Projected annual impact if revenue data available. Include caveat. If no revenue data: "Revenue data not available — projected impact not calculated."]

## Recommendation
[Specific next steps: what to ship, what to test next, what to investigate. Be actionable — not "consider further analysis" but "ship the green button to 100% and test headline copy next."]

## Watch Out For
[Risks, caveats, segments that behaved differently, anything surprising. If nothing notable: "No significant anomalies detected."]
```

# Audience Adaptation

Shape the brief based on the audience selected in the Interactive Phase:

## Executives
- Lead with revenue impact and strategic recommendation
- Replace confidence percentages with: "Highly confident" (p<0.05), "Promising but early" (p 0.05-0.10), "Not yet conclusive" (p>0.10)
- Minimise technical detail — no sample sizes in the main narrative
- End with a clear go/no-go ask: "Recommendation: Ship this change. Expected impact: $X/year."

## Growth/Product Teams
- Lead with conversion lift and segment insights
- Include implementation details: what to ship, what to A/B test next
- Show sample sizes and confidence levels
- End with metrics to watch: "Post-ship, monitor: checkout completion rate, mobile conversion, revenue per session."

## Both
- Generate two sections in the same file, separated by `---`:
  1. "## Executive Summary" (exec-adapted)
  2. "## Growth Detail" (growth-adapted)

# Tone Rules

- Australian English spelling (analyse, prioritise, metre, etc.)
- Direct and concise — no filler phrases ("It's worth noting that...", "It's interesting to see...")
- Lead with the recommendation, not the methodology
- An exec should be able to read only Verdict + Recommendation and have everything they need
```

- [ ] **Step 2: Commit**

Run:
```bash
cd /Users/samuel/projects && git add ab-test/SKILL.md && git commit -m "feat: add output template and audience adaptation"
```

---

### Task 5: Add Edge Cases and Trigger Phrases

**Files:**
- Modify: `/Users/samuel/projects/ab-test/SKILL.md`

- [ ] **Step 1: Append Edge Cases and Trigger Phrases sections**

Add the following after the Tone Rules section in SKILL.md:

```markdown
# Edge Cases

Handle these scenarios gracefully:

- **No conversions in one variant:** "Zero conversions recorded — this variant may be broken or the test needs more time. Do not ship based on this data."
- **Very small sample (n < 1000):** "Results are based on a small sample and may not be reliable. Recommend running the test longer before making a decision."
- **Negative lift:** Still generate the full brief. "This change hurt performance" is actionable — the brief should say "Don't ship" with the magnitude of the negative impact.
- **Multiple variants (A/B/C):** Compare each variant to control separately. Highlight the winner. If two variants are close, note that either could work.
- **No revenue data:** Remove the Revenue Impact section. Note: "Revenue data not available — projected impact not calculated."
- **Inconclusive result (p > 0.10):** Verdict: "No detectable difference." Recommendation: either iterate on the variant or accept the status quo. Don't force a directional recommendation.
- **One variant has vastly different sample size:** Flag as potential traffic allocation issue. "Uneven traffic split detected — results may be skewed."

# Trigger Phrases

- `/ab-test`
- "analyze my AB test"
- "share experiment results"
- "what did the test show"
- "AB test brief"
- "experiment analysis"
- "A/B test results"
- "test analysis"
```

- [ ] **Step 2: Commit**

Run:
```bash
cd /Users/samuel/projects && git add ab-test/SKILL.md && git commit -m "feat: add edge cases and trigger phrases"
```

---

### Task 6: Create README.md

**Files:**
- Create: `/Users/samuel/projects/ab-test/README.md`

- [ ] **Step 1: Write the README**

Create `/Users/samuel/projects/ab-test/README.md`:

```markdown
# AB Test

A Claude Code skill that analyses A/B test results and generates one-page briefs with actionable recommendations for non-technical stakeholders.

## What It Does

Takes raw A/B test data (CSV, Excel, pasted numbers, or a dashboard URL) and produces a clear, jargon-free brief that tells stakeholders what happened, what it means, and what to do next.

Think of it as a translator between your data team and your board room. The data team runs the test; this skill writes the memo that actually gets read.

## Input Formats

| Format | Example |
|--------|---------|
| CSV | Paste directly or provide file path |
| XLSX | Provide file path (.xlsx) |
| Raw stats | "Control: 5000 users, 150 conversions. Variant: 5000 users, 195 conversions." |
| Dashboard URL | Paste any URL (Google Analytics, Optimizely, etc.) |

## Usage

In Claude Code, invoke with:

```
/ab-test
```

Or describe what you need:

- "Analyze my AB test — here are the results: [paste data]"
- "Share experiment results from this dashboard: [URL]"
- "What did the test show? Control: 2000 users, 80 conversions. Variant: 2000 users, 112 conversions."

## What You Get

A one-page brief with:

- **Verdict** — Ship it, don't ship, run longer, or test again
- **Results at a Glance** — Conversion rates, lift, confidence in plain English
- **What This Means** — Business impact in 2-3 sentences
- **Revenue Impact** — Projected annual impact (if revenue data available)
- **Recommendation** — Specific next steps
- **Watch Out For** — Risks, surprises, segment differences

## Audience Adaptation

The skill asks who will read the brief and adapts:

- **Executives** — Revenue-focused, strategic, no jargon
- **Growth/Product teams** — Conversion-focused, implementation details, metrics to watch
- **Both** — Two sections in one brief, separated by a divider

## Sample Output

<details>
<summary>Click to expand — Sample brief (checkout button A/B test)</summary>

# A/B Test Brief: Green Checkout Button

## Verdict
Ship the green checkout button — it outperformed the blue button with high confidence.

## What We Tested
We hypothesised that a green checkout button would increase click-through rate compared to the existing blue button. The green variant was shown to 50% of traffic over 21 days.

## Results at a Glance
| Metric | Control (Blue) | Variant (Green) | Lift |
|--------|----------------|-----------------|------|
| Conversion rate | 3.2% | 4.1% | +28.1% |
| Sample size | — | — | 24,500 total |
| Confidence | — | — | Statistically significant |

## What This Means
The green button drove meaningfully more checkouts. This isn't random noise — the result is statistically significant with a large sample size. The lift is consistent across both desktop and mobile.

## Revenue Impact
Projected annual impact: +$142,000 in revenue (based on current traffic and average order value of $85). Caveat: Assumes current rates hold. Actual results may vary with seasonality.

## Recommendation
Ship the green button to 100% of traffic. Next test: try a larger button size to see if the lift compounds.

## Watch Out For
Mobile showed a slightly higher lift (+32%) than desktop (+24%). Worth monitoring post-ship to confirm the pattern holds.

</details>

## How It Works

1. **Receive** — Accepts data in CSV, XLSX, raw stats, or URL format
2. **Clarify** — Asks 2-3 questions about hypothesis, primary metric, and audience
3. **Analyse** — Computes conversion rates, statistical significance, and revenue impact
4. **Generate** — Produces a one-page brief adapted to the audience

## License

MIT
```

- [ ] **Step 2: Commit**

Run:
```bash
cd /Users/samuel/projects && git add ab-test/README.md && git commit -m "docs: add ab-test skill README with usage guide and sample output"
```

---

### Task 7: Final Review and Commit

**Files:**
- Verify: `/Users/samuel/projects/ab-test/SKILL.md`
- Verify: `/Users/samuel/projects/ab-test/README.md`

- [ ] **Step 1: Read the complete SKILL.md and verify all sections are present**

Read `/Users/samuel/projects/ab-test/SKILL.md` and verify it contains:
- YAML frontmatter (name, description, allowed-tools)
- Role section
- Input Expected section (with 4-format auto-detection table)
- Interactive Phase (3 questions with skip logic)
- Analysis Engine (metrics, z-test formulas, revenue impact, segments)
- Output Template (full brief structure)
- Audience Adaptation (exec, growth, both)
- Tone Rules
- Edge Cases (7 scenarios)
- Trigger Phrases

- [ ] **Step 2: Verify README.md exists and is complete**

Read `/Users/samuel/projects/ab-test/README.md` and verify it contains:
- Overview of what the skill does
- Input formats table
- Usage examples
- Output description
- Audience adaptation summary
- Sample output (collapsible)
- How it works workflow

- [ ] **Step 3: Create docs/superpowers/specs directory if needed and verify spec exists**

Run: `ls /Users/samuel/projects/docs/superpowers/specs/2026-05-25-ab-test-skill-design.md`

- [ ] **Step 4: Final commit if any fixes were needed**

If any edits were made during review:
```bash
cd /Users/samuel/projects && git add ab-test/ && git commit -m "fix: polish ab-test skill after review"
```

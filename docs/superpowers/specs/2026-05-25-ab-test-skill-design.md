# AB Test Skill — Design Spec

## Overview

A Claude Code skill that analyses A/B test results and generates one-page briefs with actionable recommendations for non-technical stakeholders. Handles multiple input formats, asks clarifying questions about business context, and produces a plain-English brief tailored to the audience.

## Metadata

- **Name:** `ab-test`
- **Location:** `/Users/samuel/projects/ab-test/SKILL.md`
- **Pattern:** Single-file skill (follows `persona/` structure)
- **Allowed tools:** `AskUserQuestion`, `WebFetch`, `Bash`

## Trigger Phrases

- `/ab-test`
- `analyze my AB test`
- `share experiment results`
- `what did the test show`
- `AB test brief`
- `experiment analysis`

## Input Handling

The skill accepts A/B test data in four formats, auto-detected from user input:

| Format | Detection | Processing |
|--------|-----------|------------|
| CSV | Contains commas/tab separators | Direct parse of columns |
| XLSX | File path ends in `.xlsx` | Convert via Python (`openpyxl`) or command-line tool, then parse |
| Raw stats | Freeform text with numbers | Extract variant names, sample sizes, conversion counts |
| Dashboard URL | Starts with `http` | Fetch via WebFetch, extract structured data |

**Expected data columns** (flexible — skill adapts to what's present):
- Variant name (control / variant A / variant B)
- Sample size (users / sessions)
- Conversions (or conversion rate)
- Revenue (optional)
- Date range (optional)
- Segment columns (optional — device, traffic source, etc.)

## Interactive Phase

After receiving data, the skill asks up to 3 clarifying questions — one at a time:

1. **Hypothesis:** "What was the hypothesis behind this test?"
   - Why: Frames the "so what" and helps write the "What We Tested" section
2. **Primary metric:** "What's the one metric that matters most for this test?"
   - Why: Determines which number leads the brief (conversion? revenue? engagement?)
3. **Audience:** "Who will read this brief — executives, growth/product teams, or both?"
   - Why: Shapes tone, detail level, and section emphasis

**Skip logic:** If the user provides context upfront (e.g. "Here are results for our checkout button test — we wanted to see if green increased conversions, it's for the growth team"), the skill skips questions where context is already clear.

## Analysis Engine

The skill computes these metrics from the data:

- **Conversion rate** per variant (absolute and relative lift)
- **Confidence level** (95% threshold, explained in plain English)
- **Sample size adequacy** (flags if total n < 1000 or test ran < 2 weeks)
- **Revenue impact** (if revenue data available — projected annual impact)
- **Segment breakdown** (if data includes device, traffic source, etc.)

### Statistical Translation

No raw p-values or formulas in the output. Plain English only:

| Statistical result | Plain English |
|--------------------|---------------|
| p < 0.05 | "Statistically significant — this result is real" |
| p 0.05–0.10 | "Suggestive but not conclusive — we need more data" |
| p > 0.10 | "No detectable difference — the change didn't move the needle" |

### Calculation Notes

For two-proportion z-test:
- Standard error: `SE = sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)`
- Z-score: `z = (p2 - p1) / SE`
- Confidence from standard normal distribution

For revenue impact: `(variant_rate - control_rate) * total_users * avg_revenue_per_conversion * 365 / test_days`

## Output Template

Single markdown file, one-page brief format:

```
# A/B Test Brief: [Test Name]

## Verdict
[1-sentence recommendation: Ship it / Don't ship / Run longer / Test again]

## What We Tested
[2-3 sentences: hypothesis, variant vs control, primary metric]

## Results at a Glance
| Metric | Control | Variant | Lift |
|--------|---------|---------|------|
| Conversion rate | X% | Y% | +Z% |
| Sample size | — | — | N total |
| Confidence | — | — | XX% |

## What This Means
[2-3 plain-English sentences explaining the result in business terms]

## Revenue Impact
[Projected impact — annualised if possible, with caveat about extrapolation]

## Recommendation
[Specific next steps: ship, iterate, investigate further, kill the test]

## Watch Out For
[Risks, caveats, segments that behaved differently, anything surprising]
```

### Tone

- Direct, no jargon, leads with the recommendation
- An exec should be able to read only Verdict + Recommendation and have everything they need
- Australian English spelling (honour, analyse, etc.)

## Audience Adaptation

The audience question shapes the output:

**Executives:**
- Lead with revenue impact and strategic recommendation
- Minimise technical detail — confidence becomes "highly confident" / "not yet confident"
- End with a clear go/no-go ask

**Growth/product teams:**
- Lead with conversion lift and segment insights
- Include implementation details — what to ship, what to A/B test next
- End with metrics to watch post-ship

**Both:**
- Generate two sections in the same file: "Executive Summary" and "Growth Detail", separated by a divider

## Workflow Summary

```
User invokes /ab-test
  → Skill asks: "What are the test results?"
  → User provides data (CSV/XLSX/raw stats/URL)
  → Skill auto-detects format, parses data
  → Skill asks up to 3 questions (hypothesis, metric, audience)
  → Skill computes metrics and statistical significance
  → Skill generates one-page brief
  → Skill presents brief to user
  → User can request revisions or save to file
```

## File Structure

```
ab-test/
  SKILL.md          # The skill definition
```

Single file, no dependencies beyond Claude Code's built-in tools.

## Edge Cases

- **No conversions in one variant:** Flag as "zero conversions — test may need more time or the variant may be broken"
- **Very small sample:** Warn that results are unreliable, recommend running longer
- **Negative lift:** Still generate brief — "this change hurt performance" is actionable
- **Multiple variants (A/B/C):** Compare each variant to control, highlight winner
- **No revenue data:** Skip Revenue Impact section, note "revenue data not available"
- **Inconclusive result:** Brief says "no detectable difference" with recommendation to either iterate or accept the status quo

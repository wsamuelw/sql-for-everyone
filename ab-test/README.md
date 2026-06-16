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
- **Kill or Iterate** — Fork for negative results: what to abandon vs what to retry
- **Technical Appendix** — Raw stats for analysts (z-scores, CIs, sample sizes)

## Key Capabilities

- **Multi-sheet XLSX** — Joins fact and dimension tables automatically (e.g., offer-level events + campaign-level assignment)
- **Multi-experiment detection** — Spots multiple experiment IDs in one file, surfaces them, and analyses one at a time
- **User-specified analysis level** — Respects "run at campaign level" / "run at user level" without second-guessing
- **Segment analysis** — Automatically computes device, traffic source, and other binary segment breakdowns
- **Uneven splits** — Handles intentional 90/10 or 80/20 traffic allocations without false SRM alarms

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

1. **Receive** — Accepts data in CSV, XLSX, raw stats, or URL format. Multi-sheet workbooks are joined automatically.
2. **Filter** — Detects multiple experiments in one file and asks which to analyse. Surfaces experiment IDs, group splits, and sample sizes.
3. **Validate** — Shows parsed data summary for human review. Validates arithmetic, flags short tests, and detects business rule violations.
4. **Clarify** — Asks contextual questions as needed: analysis date range, SUTVA assumptions, strategic context, audience. Skips what's already known.
5. **Analyse** — Computes conversion rates, statistical significance, effect sizes, MDE, and segment-level breakdowns.
6. **Generate** — Produces a one-page brief adapted to the audience, with a Technical Appendix for analysts.

## License

MIT

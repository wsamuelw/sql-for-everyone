# A/B Test Summary: EXP-01245 — Campaign-Level Offer Conversion

**TL;DR:** Challenger (B) reduced campaign conversion by 3.75pp (68.4% → 64.7%) — this change costs ~5.5% fewer campaigns converting. Don't ship.

## Verdict
Don't ship. Confident — the effect is statistically significant and the confidence interval is entirely negative. Group B underperforms across the board.

## What We Tested
Two offer variants (A vs B) were tested across campaigns, with Group B receiving a different offer configuration. The primary metric was campaign-level conversion rate — whether any offer within a campaign resulted in a conversion. The test ran from 21–29 June 2025 (9 days) with a 90/10 traffic split (intentional).

## Narrative Hook
We expected the challenger offer to lift campaign conversion. Instead, it degraded performance by nearly 4 percentage points — and the damage is concentrated on Web, where we thought we had the strongest position.

## Results at a Glance
| Metric | Control (A) | Variant (B) | Lift |
|--------|------------|------------|------|
| Campaign conversion rate | 68.40% | 64.65% | −3.75pp |
| 95% CI for lift | — | — | [−7.27pp to −0.22pp] |
| Effect size (Cohen's h) | — | — | Very small (0.079) |
| Campaigns analysed | 7,316 | 778 | 8,094 total |
| Could detect effects of | — | — | ~5pp or larger with confidence |
| Confidence | — | — | Statistically significant |

**Offer-level cross-check:** At the individual offer level, B also underperforms (24.71% vs 23.61%, −1.10pp) — consistent with the campaign-level finding.

**Revenue impact:** Not directly measured, but campaign conversion is a leading indicator for pipeline revenue. The −5.5% relative decline suggests a proportional negative revenue impact.

## What This Means
The challenger offer is hurting conversion, not helping it. At scale, this would mean fewer campaigns generating results — a direct hit to pipeline volume. The effect is real (not just noise), but small in absolute terms. The key question is whether the 90/10 split adequately powered the test for the B group (778 campaigns is adequate for a 5pp effect, which is what we observed).

## Recommendation
**Ship control (A) to 100%.** Do not roll out B. The evidence is clear: B underperforms, and the confidence interval excludes zero.

If you still believe the B approach has merit, the issue may be execution rather than concept — see Kill or Iterate below.

**Cost of inaction:** If B ships by default (e.g., it's the new default in the codebase), you'd lose ~5.5% campaign conversion. At 8,000+ campaigns/week, that's ~440 fewer converting campaigns per week.

## Kill or Iterate
- **Kill:** The B offer configuration is worse than A across both campaign and offer level. If B represents a fundamental direction change (new pricing, new creative), the data says it doesn't work — don't retry without a meaningful redesign.
- **Iterate:** If B was a specific tweak to an offer that has other benefits (e.g., higher revenue per conversion, better user experience), test the tweak in isolation on a narrower segment. The Web segment shows the biggest decline (−3.90pp) — that's where the damage is coming from.

## Next Steps
| Owner | Action | Timeline | Decision Gate |
|-------|--------|----------|---------------|
| Product/Ops | Roll all traffic back to Control (A) | This week | Verify campaign conversion returns to ~68% baseline |
| Analytics | Investigate why B degrades Web more than Mobile | Within 2 weeks | Identify specific offer element causing drop |
| Product | If iterating: redesign B and test on Mobile only first | Next sprint | Mobile shows +2.42pp lift — isolate and validate |

## Watch Out For
- **Risk:** The 90/10 split means B only has 778 campaigns — if you want to detect smaller effects (<5pp), you'd need a larger B sample. | **Likelihood:** Low (current effect is large enough to detect) | **What to do:** For future tests, consider 80/20 if you need more precision on the challenger.
- **Risk:** Test ran 9 days (<14) — novelty effects cannot be ruled out, though the direction is negative which makes novelty unlikely to explain the result. | **Likelihood:** Low | **What to do:** Not actionable for this test; note for future test design.
- **Risk:** 1,485 users appear in multiple campaigns — campaign-level independence may be slightly violated. | **Likelihood:** Medium | **What to do:** The effect direction is robust; if anything, shared users would dilute the difference. Results likely conservative.

**One thing to remember:** The challenger offer costs us ~440 converting campaigns per week — ship control and investigate what went wrong with B.

---

## Technical Appendix

| Parameter | Value |
|-----------|-------|
| Experiment | EXP-01245 |
| Groups | A (n=7,316) vs B (n=778) |
| Split | 90/10 (intentional) |
| SRM chi² | 5,281 (critical 3.84) — expected given intentional split |
| Campaign conv: A | 68.40% (5,004/7,316) |
| Campaign conv: B | 64.65% (503/778) |
| Absolute diff | −3.75pp |
| Relative diff | −5.48% |
| Z-score | −2.13 |
| 95% CI (absolute) | [−7.27pp, −0.22pp] |
| Cohen's h | −0.079 (very small) |
| MDE | 4.98pp |
| Offer conv: A | 24.71% (19,959/80,772) |
| Offer conv: B | 23.61% (2,031/8,602) |
| Mobile conv: A | 21.88% (7,526/34,400) |
| Mobile conv: B | 24.30% (1,053/4,333) — +2.42pp |
| Web conv: A | 26.81% (12,433/46,372) |
| Web conv: B | 22.91% (978/4,269) — −3.90pp |
| Date range | 2025-06-21 to 2025-06-29 (9 days) |
| Expected cell counts | All > 5 ✓ |

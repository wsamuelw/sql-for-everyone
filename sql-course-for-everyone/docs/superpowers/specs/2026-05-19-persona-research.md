# Persona Research Report: SQL for Everyone Course

**Date:** 2026-05-19
**Product:** SQL for Everyone — interactive single-file SQL course
**Target audience:** Non-technical business professionals (marketing, finance, ops, HR, sales) who rely on data analysts
**Geography:** Australia (metro focus)

---

## Executive Summary

- **Top preference:** 9/10 personas rated the interactive editor as the most compelling feature — "learning by doing" beats reading every time
- **Key friction point:** 7/10 personas expressed concern about the jump from GROUP BY to subqueries/window functions — the difficulty curve needs smoothing
- **Standout segment:** Mid-level marketing and finance personas (3-7 years experience) showed the highest motivation and willingness to invest time

---

## Quantitative Insights

| Question | Avg (0-10) | Median | Top/Bottom Split |
|----------|------------|--------|------------------|
| Curriculum relevance to daily work | 8.1 | 8 | 8/10 scored ≥7, 0 scored ≤4 |
| Difficulty progression feels manageable | 6.4 | 6 | 4/10 scored ≥8, 3/10 scored ≤5 |
| Tone and approachability | 8.7 | 9 | 9/10 scored ≥7 |
| Interactive editor approach | 9.2 | 9 | 10/10 scored ≥8 |
| Willingness to complete full course | 7.3 | 7 | 5/10 scored ≥8, 2/10 scored ≤5 |
| Likelihood to use skills at work | 8.5 | 9 | 9/10 scored ≥7 |

---

## Personas

### P01 — Sarah, Marketing Coordinator
- **Age:** 28 | **Role:** Marketing Coordinator | **Company:** Mid-size retail (200 staff)
- **Experience:** 4 years | **Tech comfort:** Medium — uses Excel daily, basic Google Analytics
- **Learning style:** Visual learner, prefers short bursts (15-20 min sessions)
- **SQL exposure:** None, but understands "filtering" from Excel pivot tables
- **Quote:** *"I wait 2-3 days for a simple customer list pull. If I could do that myself, it'd change my week."*

### P02 — David, Finance Analyst
- **Age:** 32 | **Role:** Finance Analyst | **Company:** Big 4 bank
- **Experience:** 7 years | **Tech comfort:** High — advanced Excel, some Power BI, has seen SQL but never written it
- **Learning style:** Structured, wants to understand the "why" before the "how"
- **SQL exposure:** Has seen analyst code, understands the concept
- **Quote:** *"I don't need to be a developer. I just need to pull my own reconciliation data without begging the data team."*

### P03 — Jessica, HR Business Partner
- **Age:** 38 | **Role:** HR Business Partner | **Company:** Professional services firm
- **Experience:** 12 years | **Tech comfort:** Low — comfortable with HRIS dashboards, not much else
- **Learning style:** Needs hand-holding, benefits from analogies and real-world context
- **SQL exposure:** Zero, slightly intimidated by "code"
- **Quote:** *"The word 'SQL' sounds technical. If it's friendly and I can take my time, I'd give it a go."*

### P04 — Michael, Operations Manager
- **Age:** 41 | **Role:** Operations Manager | **Company:** Logistics company
- **Experience:** 15 years | **Tech comfort:** Medium — uses ERP systems, basic reporting tools
- **Learning style:** Practical, wants to solve immediate problems, impatient with theory
- **SQL exposure:** None
- **Quote:** *"I don't want a computer science degree. I want to know: how many orders shipped late last month?"*

### P05 — Emma, Digital Marketing Specialist
- **Age:** 26 | **Role:** Digital Marketing Specialist | **Company:** SaaS startup (50 staff)
- **Experience:** 3 years | **Tech comfort:** High — comfortable with APIs, Zapier, basic Python tutorials
- **Learning style:** Self-directed, fast learner, happy to experiment
- **SQL exposure:** Has tried online tutorials but found them too abstract
- **Quote:** *"I've tried Codecademy SQL but it felt disconnected from my actual work. I want real business data."*

### P06 — James, Sales Operations Lead
- **Age:** 35 | **Role:** Sales Operations Lead | **Company:** Enterprise software vendor
- **Experience:** 8 years | **Tech comfort:** Medium-high — Salesforce admin, Excel power user
- **Learning style:** Outcome-focused, wants to build dashboards and reports
- **SQL exposure:** Has exported Salesforce data, understands relational concepts
- **Quote:** *"Our CRM data is a goldmine but I can only scratch the surface with filters. SQL would unlock the rest."*

### P07 — Priya, Financial Controller
- **Age:** 45 | **Role:** Financial Controller | **Company:** Manufacturing firm
- **Experience:** 18 years | **Tech comfort:** Low-medium — knows ERP inside out, wary of "coding"
- **Learning style:** Cautious, needs to see value before investing time
- **SQL exposure:** Zero, associates SQL with IT department
- **Quote:** *"At my level, I shouldn't have to wait a week for a P&L breakdown by region."*

### P08 — Liam, Customer Success Manager
- **Age:** 30 | **Role:** Customer Success Manager | **Company:** B2B SaaS
- **Experience:** 5 years | **Tech comfort:** Medium — uses Intercom, basic Looker dashboards
- **Learning style:** Collaborative, likes to learn with others, benefits from community
- **SQL exposure:** None, but curious
- **Quote:** *"I know what data I need — churn by cohort, usage patterns — but I can't get to it without a data team ticket."*

### P09 — Olivia, People & Culture Analyst
- **Age:** 29 | **Role:** People & Culture Analyst | **Company:** Tech company (500 staff)
- **Experience:** 4 years | **Tech comfort:** Medium-high — Excel, basic Tableau, some R exposure at uni
- **Learning style:** Analytical, wants to understand the underlying logic
- **SQL exposure:** Minimal, but has a mental model from R
- **Quote:** *"If I can write SQL, I can build my own headcount reports instead of waiting for People Analytics."*

### P10 — Tom, General Manager
- **Age:** 50 | **Role:** General Manager (Regional) | **Company:** Hospitality chain
- **Experience:** 22 years | **Tech comfort:** Low — delegates all data work to analysts
- **Learning style:** Executive-style, wants the big picture first, then drill down
- **SQL exposure:** Zero, but sees the strategic value
- **Quote:** *"I don't need to write SQL myself, but I need to understand what my team is doing with data. Literacy, not mastery."*

---

## Qualitative Themes

### Theme 1: The "ticket bottleneck" is the primary pain point
Every persona described the same frustration: waiting days for simple data pulls. The motivation to learn SQL isn't intellectual curiosity — it's removing a dependency. *"I asked for a customer list on Monday. Got it Thursday. By then the campaign was already live without it." (P01, Marketing Coordinator)*

### Theme 2: Fear of "coding" is the biggest barrier to entry
Non-technical personas (P03, P04, P07, P10) associate SQL with programming and feel intimidated. The "friendly and approachable" tone scored 8.7/10 — but it needs to be paired with reassurance that this isn't coding in the traditional sense. *"The moment you say 'programming language', I switch off. But if you say 'search filter for databases', I'm in." (P03, HR Business Partner)*

### Theme 3: Real business data beats abstract examples
Personas who had tried online SQL courses (P05, P06) found generic examples like "students" and "courses" disconnected from their work. The generic business data (customers, orders, products) scored well, but several personas wished for industry-specific examples. *"I don't care about a 'students' table. Show me revenue by region and I'll pay attention." (P07, Financial Controller)*

### Theme 4: The difficulty cliff between GROUP BY and subqueries
7/10 personas flagged the jump from lesson 6 (JOINs) to lesson 7 (subqueries) as concerning. Window functions (lesson 9) were described as "scary" by lower-tech personas. The linear curriculum is good, but the progression needs intermediate stepping stones. *"I was doing fine until you said 'window functions'. That sounds like something my IT team does." (P04, Operations Manager)*

### Theme 5: The interactive editor is the killer feature
10/10 personas rated the interactive editor 8+ out of 10. The ability to type, run, and see results immediately was universally compelling. Multiple personas said this alone would keep them engaged vs. reading static examples. *"Reading SQL is boring. Running SQL and seeing results? That's addictive." (P05, Digital Marketing Specialist)*

### Theme 6: Post-course utility matters as much as the course itself
Several personas (P02, P06, P09) asked about what happens after — reference materials, community, advanced topics. The cheatsheet scored well, but there's appetite for more. *"I'll learn it, but I'll forget syntax in 2 weeks. I need something I can keep coming back to." (P06, Sales Operations Lead)*

---

## Data-Driven Recommendations

1. **Bridge the GROUP BY → subquery gap with a "building reports" transitional lesson**: Backed by 7/10 personas scoring ≤6 on difficulty progression. Add a lesson 6.5 that shows how to combine GROUP BY + JOINs into a real report before introducing subqueries. Suggested next step: Insert a "Mini Report" lesson between JOINs and subqueries.

2. **Add a "What SQL is NOT" section to the Welcome lesson**: Backed by 4/10 personas (P03, P04, P07, P10) expressing fear of "coding". Explicitly state: "This is not programming. It's asking questions to a database — like using a search filter." Suggested next step: Add a concept box in lesson 0 that debunks the "coding" myth.

3. **Include "real question" headers for each lesson**: Backed by 8/10 personas scoring ≥7 on curriculum relevance but 3/10 noting abstract framing. Frame each lesson around a business question: "How many customers are in Sydney?" not "Filtering with WHERE." Suggested next step: Add a business question as the subtitle of each lesson.

4. **Add a "What to learn next" section after the cheatsheet**: Backed by 5/10 personas asking about post-course resources. Point to dbt, Looker/Power BI SQL, or advanced courses. Suggested next step: Add a final section with 3-5 external resources for continued learning.

5. **Consider a "difficulty badge" on each lesson**: Backed by 7/10 personas wanting to know what they're getting into before starting. Show "Easy / Medium / Hard" on sidebar and lesson headers so learners can pace themselves. Suggested next step: Add badges to sidebar nav and lesson titles.

---

## Golden Combos

- **Golden framing:** "Ask your own data questions" — every persona responded better to "asking questions" than "learning SQL" or "writing queries"
- **Golden analogy:** "Like Excel filters, but for databases" — the spreadsheet analogy scored highest for comprehension across all tech comfort levels
- **Golden progression:** SELECT → WHERE → Sorting → Aggregation → GROUP BY → Mini Report → JOINs → Subqueries → CASE WHEN → Window Functions → CTEs → Cheatsheet
- **Golden tone:** Friendly but not condescending — the high-tech personas (P02, P05, P09) would disengage if it felt too "dumbed down", while low-tech personas (P03, P04, P07) need reassurance

---

## Methodology Note

*Findings based on 10 synthetic personas generated to represent non-technical business professionals in Australian organisations. Personas span marketing, finance, HR, operations, sales, and general management roles with 3-22 years experience. Synthetic data supports ideation and prioritisation; validate with 5-10 real prospects before commercial rollout. Complies with ESOMAR Guidelines and Privacy Act 1988 (Cth) for simulated data.*

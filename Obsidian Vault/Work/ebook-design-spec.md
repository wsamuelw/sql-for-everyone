# Ebook Design Spec: Resume Red Flags

## Overview

**Title:** Resume Red Flags: Common Mistakes in Early-Career Data Analytics Resumes (And How to Fix Them)

**Tagline:** A practical guide for university students and fresh graduates to spot and fix the resume mistakes that keep them from landing interviews.

**Audience:** University students and fresh graduates targeting data analyst / data science / BI roles.

**Format:** Markdown (stored in Obsidian Vault), exportable to PDF/HTML later.

**Tone:** Empathetic + direct mix. Acknowledges the struggle, then gives honest, actionable fixes.

**Authority framing:** Position as collective insights from mentoring 20+ early-career data analytics candidates. The same mistakes surface again and again — not because people aren't capable, but because nobody told them what hiring managers actually see.

**Growth model:** Modular. New mistake entries can be appended as more resumes are reviewed. The AI self-audit prompt at the end grows alongside the catalogue.

---

## Structure

### 1. Introduction (~1 page)

- Why this ebook exists — the gap between what uni teaches and what hiring managers actually look for
- Who it's for — uni students and fresh grads targeting data analytics roles
- How to use it — each section is a standalone mistake entry. Jump to whichever resonates, or read front to back
- Authority framing — "After reviewing 20+ resumes from early-career data analytics candidates..."

### 2. The Error Catalogue (core content, grows over time)

Each mistake entry follows a standardised template:

```
## Mistake #N: [Short, punchy title]

### The Problem
[1-2 sentences explaining what the mistake looks like]

### Why It Matters
[The recruiter/hiring manager perspective — what they think when they see this]

### Real Example (Anonymised)
[Pull from one of the 3 source resumes — the actual problematic text, with names/companies anonymised]

### The Fix
[Specific, actionable advice — what to do instead]

### Before → After
[The original text vs the rewritten version, side by side]
```

**Initial 10 mistake categories** (derived from the 3 source resumes):

1. **Missing Professional Summary** — No hook at the top of the resume
2. **Task-Focused Bullets** — "Responsible for X" instead of impact-driven statements
3. **No Quantified Achievements** — Missing numbers, metrics, scale
4. **Vague Technical Skills** — Dumping a flat list instead of categorising by proficiency or relevance
5. **Irrelevant/Outdated Content** — High school awards, expired volunteering, outdated roles
6. **Inconsistent Formatting** — Date styles, section headers, spacing inconsistencies
7. **Too Much Education, Too Little Experience** — When education section dominates the page
8. **Generic Soft Skills** — "Communication, teamwork" listed without evidence or context
9. **No Narrative Arc** — Resume reads like a list, not a story of progression and growth
10. **Missing Contact/LinkedIn/GitHub** — Basic professional hygiene

### 3. AI Self-Audit Prompt (~1 page)

A copy-paste prompt readers can drop into ChatGPT, Claude, or any LLM:

```
You are a senior data analytics hiring manager. Review my resume against
these common mistakes and provide specific, actionable feedback:

[List of all mistakes covered in the ebook — grows as catalogue grows]

For each mistake you find in my resume:
1. Quote the problematic text
2. Explain why it's a problem
3. Suggest a specific rewrite

My resume:
[paste resume here]
```

### 4. Closing (~0.5 page)

Brief encouragement:
- "Your resume is a living document. Review it against this checklist every time you apply."
- "The difference between 'I never hear back' and 'let's schedule an interview' is usually 3-4 fixes."
- Invite readers to share their resumes for future editions of this guide.

---

## Source Material

Three anonymised resumes used as case studies:

| Resume | Profile | Key Strengths | Key Weaknesses |
|--------|---------|---------------|----------------|
| Resume 1 | BSc Data Science, UniMelb (2022-2025). Deloitte vacationer, hotel receptionist, tutor. | Strong education, top school (Mac.Rob, ATAR 97.95), bilingual (Mandarin/English) | No professional summary, task-focused bullets, no quantified achievements, high school awards still listed, weak technical skills section |
| Resume 2 | MPhil Computer Science, RMIT. BSc Automation from Beijing Institute of Technology. Research-focused. | Publication under review, strong technical depth (GNN, deep RL, PyTorch), real-world impact framing ($13.5B potential savings) | Wall-of-text profile, project descriptions overly verbose, skills section could be clearer, no professional summary as a hook |
| Resume 3 | Master of Analytics, RMIT. Business Analyst at PIKMO, Marketing/Product Analyst at Fantuan/EASI/HungryPanda. | Most industry experience, actual commercial data roles, quantified achievements (81.9% accuracy, 19.6% improvement), good skill categorisation | Summary is generic, inconsistent formatting, projects section could be tighter, some bullet points still task-focused |

---

## Design Principles

1. **Modular** — Each mistake entry is self-contained. New entries append without disrupting existing content.
2. **Evidence-based** — Every mistake is drawn from real resume data, not hypotheticals.
3. **Actionable** — Every entry ends with a concrete "Before → After" rewrite, not vague advice.
4. **Scannable** — Headers, bold text, and consistent structure let readers jump to relevant issues.
5. **Growing** — The catalogue is designed to expand as more resumes are reviewed. The AI prompt at the end auto-expands with each new entry.

---

## File Location

- Source resumes: `/Users/samuel/projects/Obsidian Vault/Work/` (resume_1.md, resume_2.md, resume_3.md)
- Ebook output: `/Users/samuel/projects/Obsidian Vault/Work/` (ebook.md — the actual ebook content)

# AI Resume Reviewer — Step-by-Step Build Guide

> Build a master AI prompt that reviews and rewrites resumes, trained on 20+ real mentee resumes. Sell it on Gumroad for $19.

---

## Step 1: Extract the Anti-Patterns (30 min)

Open Claude or ChatGPT. Paste this prompt:

```
I'm going to share 5 resumes that I've reviewed as a mentor.
For each one, list every mistake you find. Group them by category:

- Summary / objective statement
- Work experience / bullet points
- Skills section
- Formatting / structure
- ATS compatibility
- Tone / language

Be specific. Don't say "weak bullet point" — say "bullet point lists
duty instead of achievement and has no numbers."

[Paste 3-5 anonymised resumes, one at a time]
```

Do this in batches of 3-5 resumes. You'll get a massive list of mistakes.

---

## Step 2: Deduplicate and Prioritise (20 min)

Take all the mistakes from Step 1. Paste them into AI with:

```
Here are resume mistakes I've collected from reviewing 20+ resumes.
Deduplicate them. Merge similar ones. Then rank them by frequency —
which mistakes appear most often across all the resumes?

Output as a numbered list, grouped by category.

[Paste the full list]
```

You'll end up with **15-25 unique anti-patterns**, ranked by how common they are. This becomes your checklist.

---

## Step 3: Write the Master Prompt (20 min)

Take your ranked checklist and drop it into this template:

```
You are an expert resume reviewer with 10 years of experience in
[industry/field]. You've reviewed 200+ resumes and identified the
most common mistakes that get resumes rejected.

I will paste a resume below. Your job:

1. Review it against the ANTI-PATTERN CHECKLIST
2. For each issue found, output:
   - ❌ PROBLEM: quote the exact text
   - 💡 WHY: explain why it hurts their chances (1-2 sentences)
   - ✅ FIX: rewrite it better
3. After listing all issues, provide a REWRITTEN VERSION of the
   full resume with all fixes applied
4. Give an overall score out of 10 with a one-line summary

---

ANTI-PATTERN CHECKLIST:

SUMMARY:
1. Uses clichés (hardworking, team player, passionate, results-driven,
   detail-oriented)
2. Too vague — no specific skills, years of experience, or achievements
3. Reads like an objective statement ("seeking a challenging role...")
   instead of a value proposition
4. Longer than 4 lines

EXPERIENCE / BULLET POINTS:
5. Lists duties instead of achievements ("responsible for managing...")
6. No quantified results (numbers, percentages, dollar amounts)
7. Uses passive voice ("was responsible for" instead of "led")
8. Starts with "Assisted" or "Helped" — weak verbs
9. Every bullet point starts with the same word
10. Bullet points are longer than 2 lines
11. Missing context (team size, budget, scope, timeline)

SKILLS SECTION:
12. Lists basic/obvious tools (Microsoft Word, email, PowerPoint)
13. Lists soft skills as standalone items (communication, leadership)
14. Outdated or irrelevant technologies
15. Skills not backed up by experience section
16. No grouping or categorisation (wall of random skills)

FORMATTING:
17. Wall of text — no white space
18. Inconsistent formatting (dates, bullet styles, spacing)
19. Too long (2+ pages for <10 years experience)
20. Missing section headers or poor hierarchy

ATS / KEYWORDS:
21. No keywords matching the target job description
22. Uses tables, columns, or graphics that ATS can't read
23. Missing standard section names (Experience, Education, Skills)

TONE / LANGUAGE:
24. First person ("I managed a team of...")
25. Buzzword overload without substance ("synergised cross-functional
     stakeholder alignment")
26. Typos or grammatical errors

---

TARGET ROLE: [Leave blank for general, or specify: "Software Engineer",
"Marketing Manager", etc.]

Now review this resume:

[PASTE RESUME HERE]
```

---

## Step 4: Test It (30 min)

### Test 1: Run it on your mentees' resumes

Take 5 of your 20 resumes. Run the prompt on each one.

Check:
- Does it catch the mistakes you'd catch manually?
- Does it miss anything obvious?
- Are the rewrites actually better, or generic?

### Test 2: Run it on a GOOD resume

Find a strong resume (or write one). The prompt should give it a high score and find few issues. If it flags things that aren't actually problems, your checklist is too aggressive — tone it down.

### Test 3: Stress-test the edge cases

| Edge case | What to check |
|-----------|---------------|
| Career changer resume | Does it understand non-traditional paths? |
| Fresh graduate | Does it adapt for people with no experience? |
| Senior exec (2 pages) | Does it know when length is acceptable? |
| Creative role | Does it know when formatting rules don't apply? |

---

## Step 5: Refine the Checklist (15 min)

Based on your tests, edit the anti-pattern list:

- **Remove** anything the AI flags incorrectly
- **Add** anything it misses that you consistently catch
- **Clarify** any rules that produce ambiguous results
- **Add industry-specific notes** if needed

```
Here's my resume reviewer prompt. I tested it and found these issues:
- It missed [X]
- It incorrectly flagged [Y]
- The rewrites for [Z] were too generic

Suggest updates to the anti-pattern checklist to fix these issues.

[Paste the prompt]
```

---

## Step 6: Create Niche Versions (optional, 1 hr)

Take your master prompt and create 3-5 variations:

```
Here's my master resume reviewer prompt. Create 5 niche versions
for these roles, adjusting the anti-pattern checklist and rewrite
style for each:

1. Software Engineer / Tech
2. Finance / Banking
3. Marketing / Creative
4. Career changer (no direct experience)
5. Fresh graduate / entry-level

[Paste master prompt]
```

Each niche version gets its own specific anti-patterns (e.g., tech resumes shouldn't list every JS framework; finance resumes need deal sizes and AUM).

---

## Step 7: Package It for Gumroad (1 hr)

### Product structure

```
📦 AI Resume Reviewer

File 1: AI Resume Reviewer — Master Prompt.pdf
  - The prompt (formatted nicely)
  - How to use it (3 steps)
  - Example input/output (before & after)

File 2: Quick Start Guide.pdf
  - Screenshot walkthrough
  - Tips for best results

File 3: Niche Prompts (bonus)
  - Tech / Finance / Marketing / Career Changer / New Grad

File 4: Before & After Swipe File.pdf
  - 3-5 real anonymised transformations
```

### Gumroad listing

- **Title:** "AI Resume Reviewer — Trained on 200+ Real Resumes"
- **Price:** $19
- **Description:** Lead with the outcome — "Paste your resume. Get it reviewed and rewritten in 2 minutes."
- **Mockup:** Use Canva, make it look premium

---

## Timeline Summary

| Step | Time | What |
|------|------|------|
| 1 | 30 min | Extract anti-patterns from 20 resumes |
| 2 | 20 min | Deduplicate and rank |
| 3 | 20 min | Write the master prompt |
| 4 | 30 min | Test on 5+ resumes |
| 5 | 15 min | Refine based on results |
| 6 | 1 hr | Niche versions (optional) |
| 7 | 1 hr | Package for Gumroad |
| **Total** | **~4 hrs** | **Product ready to sell** |

---

## Bonus: 5 Starter Prompts (Use While Building)

### 1. The Achievement Rewrite

```
You are a resume expert. Rewrite the following bullet point to focus on
achievements instead of responsibilities. Use this formula:
[Action verb] + [what you did] + [measurable result].
Keep it under 2 lines. Here's the bullet point:

[paste their bullet point]
```

### 2. The Summary Fixer

```
Rewrite this resume summary to be specific and results-focused.
Remove all clichés (hardworking, team player, passionate).
Include the person's years of experience, top 2-3 skills, and
one quantified achievement. Keep it under 4 lines.

[paste their summary]
```

### 3. The ATS Optimiser

```
Analyse this resume against the following job description.
Identify the top 10 missing keywords and suggest where to
naturally incorporate them. Don't keyword-stuff — make it read naturally.

Resume: [paste]
Job description: [paste]
```

### 4. The Skills Section Slim-Down

```
Here's my skills section. Remove anything outdated, redundant,
or too basic (e.g. Microsoft Word). Group the remaining skills
into 3-4 categories. Prioritise skills mentioned in this job posting.

Skills: [paste]
Job posting: [paste]
```

### 5. The Cover Letter Hook

```
Write an opening paragraph for a cover letter for this job: [paste job URL/description]

Rules:
- Start with a specific achievement, not "I am writing to apply..."
- Mention the company by name and why this role specifically
- Under 4 lines
- Tone: confident but not arrogant

My background: [paste 2-3 sentences about them]
```

---

## What to Build Next

Once this sells, your next products write themselves:

| Product | Price |
|---------|-------|
| AI Cover Letter Writer (same approach) | $19 |
| AI LinkedIn Profile Optimiser | $19 |
| Career Toolkit Bundle (all three) | $39-49 |

Same methodology, different document. Build the system once, repeat it three times.

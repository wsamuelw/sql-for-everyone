# Affiliate Tweets

A Claude Code skill for generating tweet copy for affiliate links.

## What it does

Takes an affiliate URL, fetches the product details, and generates 10 tweet options with varied formatting — all copy-paste ready with the link included.

## How to use

### Option 1: Copy to Claude Code skills

```bash
cp affiliate-tweets-skill.md ~/.claude/skills/affiliate-tweets.md
```

Then invoke with:
```
/affiliate-tweets https://your-affiliate-link.com
```

### Option 2: Use as a prompt template

Just paste the contents of `affiliate-tweets-skill.md` into any Claude conversation along with your affiliate URL.

## Customisation

Edit `affiliate-tweets-skill.md` to:
- Change the number of tweets (default: 10)
- Add/remove formatting styles
- Adjust tone or target audience
- Add product-specific rules (e.g., "always mention the price")

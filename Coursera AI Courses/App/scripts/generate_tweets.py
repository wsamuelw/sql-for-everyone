#!/usr/bin/env python3
"""
generate_tweets.py — Generate ready-to-post tweets from course data.

Usage:
    python generate_tweets.py                    # Generate 30 tweet variations
    python generate_tweets.py --count 10         # Generate 10 tweets
    python generate_tweets.py --focus slug       # Focus on one course
    python generate_tweets.py --style urgency    # Use only one template style
    python generate_tweets.py --list             # List available styles
    python generate_tweets.py --output my.txt    # Custom output file

Available styles:
    social_proof   — "I've reviewed X courses..." with stats
    comparison     — Side-by-side course comparison
    urgency        — "In 12 months it'll be a job requirement"
    salary         — Salary hook + course recommendation
    free_entry     — Free-to-start courses
    hot_take       — Bold claim + course recommendation
    review         — Honest review format
    listicle       — Numbered list format
    learning_path  — Multi-course progression

What it does:
    1. Reads top_30.csv for course data (enrollment, ratings)
    2. Reads config.json for affiliate links and course data
    3. Generates tweet variations using rotating templates
    4. Injects affiliate links
    5. Outputs ready-to-paste tweets to tweets.txt
"""

import csv
import json
import random
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent.parent / "data"
CSV_PATH = DATA_DIR / "top_30.csv"
CONFIG_PATH = DATA_DIR / "config.json"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_courses():
    """Load courses from config.json (includes affiliate links)."""
    config = load_config()
    courses = []
    for slug, c in config.get("courses", {}).items():
        courses.append({
            "title": c.get("title", ""),
            "url": c.get("url", ""),
            "provider": c.get("provider", ""),
            "rating": str(c.get("rating", "")),
            "enrolled": str(c.get("enrolled", c.get("num_ratings", ""))),
            "level": c.get("level", ""),
            "slug": slug,
            "affiliate_link": c.get("affiliate_link", ""),
        })
    return courses


def parse_enrolled(enrolled_str):
    if not enrolled_str:
        return "0"
    return enrolled_str


def get_affiliate_link(config, slug):
    """Get affiliate link for a course, falling back to raw URL."""
    course = config["courses"].get(slug, {})
    link = course.get("affiliate_link", "")
    if link:
        return link
    # Fall back to config URL, then try CSV
    url = course.get("url", "")
    if not url:
        # Try to find from CSV
        courses = load_courses()
        for c in courses:
            if c.get("slug") == slug:
                url = c.get("url", "")
                break
    return url


def get_course_config(config, slug):
    """Get course config by slug."""
    return config["courses"].get(slug, {})


def format_enrolled_short(enrolled_str):
    """Convert '2,502,578' to '2.5M' for shorter tweets."""
    if not enrolled_str:
        return "0"
    num = int(enrolled_str.replace(",", ""))
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.0f}K"
    return str(num)


def generate_social_proof(course, config):
    link = get_affiliate_link(config, course.get("slug", ""))
    enrolled = parse_enrolled(course['enrolled'])
    provider = course['provider']
    title = course['title']
    rating = course['rating']

    hooks = [
        f"{enrolled} people already enrolled. There's a reason.",
        f"With {enrolled} enrolled, this is the most popular course on the topic.",
        f"⭐ {rating} from {enrolled} students. The numbers speak for themselves.",
        f"{enrolled} learners chose this course. You should too.",
        f"Ranked {rating}/5 by {enrolled} students on Coursera.",
    ]
    openers = [
        f"I just finished {title} by {provider}.",
        f"This course has {enrolled} enrolled students for a reason.",
        f"If you're looking for a sign to start learning — this is it.",
        f"The most enrolled course on {title.split()[0].lower()} I've seen.",
        f"Everyone keeps asking me which course to take. This one.",
    ]

    return (
        f"{random.choice(openers)}\n\n"
        f"{title} by {provider}\n"
        f"⭐ {rating} | {enrolled} enrolled\n\n"
        f"{random.choice(hooks)}\n\n"
        f"{link}"
    )


def generate_urgency(course, config):
    link = get_affiliate_link(config, course.get("slug", ""))
    enrolled = format_enrolled_short(course['enrolled'])
    provider = course['provider']
    title = course['title']

    hooks = [
        f"{enrolled} people are already ahead of you.",
        f"The window to get into {title.split()[0].lower()} is closing.",
        f"Every month you wait, {enrolled} more people get certified.",
        f"By the time you 'get around to it', this skill will be table stakes.",
        f"The demand for this skill just hit an all-time high.",
    ]
    closers = [
        "Don't be the person who says 'I should have started earlier.'",
        "The best time to start was last month. Second best is now.",
        "Your future self will thank you for starting today.",
        "Stop planning. Start learning.",
        "The gap between you and the people getting hired? This course.",
    ]

    return (
        f"{random.choice(hooks)}\n\n"
        f"{title} by {provider}\n"
        f"{enrolled} enrolled\n\n"
        f"{random.choice(closers)}\n\n"
        f"{link}"
    )


def generate_salary(course, config):
    link = get_affiliate_link(config, course.get("slug", ""))
    enrolled = parse_enrolled(course['enrolled'])
    provider = course['provider']
    title = course['title']

    roles = [
        ("$165K", "ML Engineer"),
        ("$145K", "Data Scientist"),
        ("$130K", "AI Product Manager"),
        ("$175K", "AI Engineer"),
        ("$155K", "ML Platform Engineer"),
    ]
    salary, role = random.choice(roles)

    openers = [
        f"Average {role} salary in 2026: {salary}",
        f"The median {role} salary just hit {salary}",
        f"{salary}/year for {role.lower()}s. The market is paying.",
        f"Want to earn {salary}? Start here.",
    ]
    hooks = [
        f"You don't need a CS degree. You need this course.",
        f"The barrier to entry is this course. The reward is {salary}.",
        f"{enrolled} people are already on this path.",
        f"This is the cheapest {salary} investment you'll make.",
        f"ROI: {salary}/year for a few hours of learning.",
    ]

    return (
        f"{random.choice(openers)}\n\n"
        f"{title} by {provider}\n"
        f"⭐ {course['rating']} | {enrolled} enrolled\n\n"
        f"{random.choice(hooks)}\n\n"
        f"{link}"
    )


def generate_free_entry(course, config):
    link = get_affiliate_link(config, course.get("slug", ""))
    enrolled = parse_enrolled(course['enrolled'])
    provider = course['provider']
    title = course['title']

    openers = [
        f"You can learn this for $0. No, seriously.",
        f"This course is free. Your excuse just expired.",
        f"Free to audit. {enrolled} people already started.",
        f"No credit card. No commitment. Just click.",
        f"$0 entry price. Unlimited upside.",
    ]
    closers = [
        f"{title} by {provider} — free to start.",
        f"Start today. It costs nothing.",
        f"The only thing between you and this skill is a click.",
        f"You have nothing to lose. Start →",
    ]

    return (
        f"{random.choice(openers)}\n\n"
        f"{title} by {provider}\n"
        f"⭐ {course['rating']} | {enrolled} enrolled\n\n"
        f"{random.choice(closers)}\n\n"
        f"{link}"
    )


def generate_hot_take(course, config):
    link = get_affiliate_link(config, course.get("slug", ""))
    enrolled = parse_enrolled(course['enrolled'])
    provider = course['provider']
    title = course['title']

    claims = [
        f"If you're not learning {title.split()[0].lower()}, you're falling behind.",
        f"This is the most underrated course on Coursera right now.",
        f"The people taking this course will be running AI teams in 2 years.",
        f"Unpopular opinion: this course is worth more than a bootcamp.",
        f"Everyone's talking about AI. This course actually teaches you to build with it.",
        f"Skip the YouTube tutorials. Take this course instead.",
        f"This is where the AI industry is heading. Get there first.",
        f"The ROI on this course is insane. {enrolled} students can't be wrong.",
    ]

    return (
        f"{random.choice(claims)}\n\n"
        f"{title} by {provider}\n"
        f"⭐ {course['rating']} | {enrolled} enrolled\n\n"
        f"{link}"
    )


def generate_listicle(courses, config):
    """Generate a listicle-style tweet for multiple courses."""
    lines = ["I've reviewed 30+ AI courses on Coursera.\n"]
    lines.append("Here are the ones actually worth your time 👇\n")

    for i, course in enumerate(courses[:10], 1):
        lines.append(f"{i}. {course['title']} ({course['provider']})")
        lines.append(f"   ⭐ {course['rating']} | {parse_enrolled(course['enrolled'])} enrolled")
        lines.append("")

    lines.append("Links in bio 👆")
    return "\n".join(lines)


def generate_learning_path(courses, config):
    """Generate a learning path tweet using multiple courses."""
    # Pick courses in learning order
    beginner = [c for c in courses if "beginner" in get_course_config(config, c.get("slug", "")).get("tags", [])]
    intermediate = [c for c in courses if "intermediate" in get_course_config(config, c.get("slug", "")).get("tags", [])]

    if len(beginner) < 3 or len(intermediate) < 2:
        return None

    random.shuffle(beginner)
    random.shuffle(intermediate)

    link = get_affiliate_link(config, beginner[0].get("slug", ""))

    return (
        f"The AI learning path from zero to employed:\n\n"
        f"1️⃣ {beginner[0]['title']} — foundation\n"
        f"2️⃣ {beginner[1]['title']} — understand the landscape\n"
        f"3️⃣ {beginner[2]['title']} — practical skills\n"
        f"4️⃣ {intermediate[0]['title']} — go deeper\n"
        f"5️⃣ {intermediate[1]['title']} — build real things\n\n"
        f"All on Coursera. All worth it.\n\n"
        f"Links in bio 👆"
    )


def generate_comparison(courses, config):
    """Generate a comparison tweet between two similar courses."""
    # Find two courses with similar tags
    tag_groups = {}
    for course in courses:
        course_cfg = get_course_config(config, course.get("slug", ""))
        for tag in course_cfg.get("tags", []):
            if tag not in tag_groups:
                tag_groups[tag] = []
            tag_groups[tag].append(course)

    # Find a tag with exactly 2 courses
    for tag, group in tag_groups.items():
        if len(group) == 2:
            a, b = group
            link_a = get_affiliate_link(config, a.get("slug", ""))
            link_b = get_affiliate_link(config, b.get("slug", ""))
            enrolled_a = parse_enrolled(a["enrolled"])
            enrolled_b = parse_enrolled(b["enrolled"])

            return (
                f"Trying to learn {tag.replace('-', ' ')}?\n\n"
                f"Option A: {a['title']} ({a['provider']})\n"
                f"⭐ {a['rating']} | {enrolled_a} enrolled\n\n"
                f"Option B: {b['title']} ({b['provider']})\n"
                f"⭐ {b['rating']} | {enrolled_b} enrolled\n\n"
                f"Both are solid. Pick based on your style.\n\n"
                f"A: {link_a}\nB: {link_b}"
            )

    return None


STYLE_GENERATORS = {
    "social_proof": lambda c, cfg: generate_social_proof(c, cfg),
    "urgency": lambda c, cfg: generate_urgency(c, cfg),
    "salary": lambda c, cfg: generate_salary(c, cfg),
    "free_entry": lambda c, cfg: generate_free_entry(c, cfg),
    "hot_take": lambda c, cfg: generate_hot_take(c, cfg),
}


def generate_tweets(count=30, focus_slug=None, style=None, output_file=None):
    """Generate tweet variations."""
    config = load_config()
    courses = load_courses()

    if focus_slug:
        courses = [c for c in courses if c.get("slug") == focus_slug]
        if not courses:
            print(f"Error: No course found with slug '{focus_slug}'")
            print("Run with --list to see available courses.")
            return

    if style and style not in STYLE_GENERATORS and style not in ("listicle", "learning_path", "comparison"):
        print(f"Error: Unknown style '{style}'")
        print("Available styles: " + ", ".join(list(STYLE_GENERATORS.keys()) + ["listicle", "learning_path", "comparison"]))
        return

    tweets = []
    styles_used = {}

    # Determine which styles to use
    if style:
        available_styles = [style]
    else:
        available_styles = list(STYLE_GENERATORS.keys())

    # Generate tweets
    attempts = 0
    max_attempts = count * 3  # Avoid infinite loop

    while len(tweets) < count and attempts < max_attempts:
        attempts += 1

        if style in ("listicle", "learning_path", "comparison"):
            # These styles use multiple courses
            if style == "listicle":
                shuffled = courses.copy()
                random.shuffle(shuffled)
                tweet = generate_listicle(shuffled, config)
            elif style == "learning_path":
                tweet = generate_learning_path(courses, config)
            else:
                tweet = generate_comparison(courses, config)

            if tweet and tweet not in tweets:
                tweets.append(tweet)
                styles_used[style] = styles_used.get(style, 0) + 1
                print(f"PROGRESS:{len(tweets)}/{count}", flush=True)
        else:
            # Single-course styles
            chosen_style = random.choice(available_styles)
            course = random.choice(courses)
            generator = STYLE_GENERATORS[chosen_style]
            tweet = generator(course, config)

            if tweet and tweet not in tweets:
                tweets.append(tweet)
                styles_used[chosen_style] = styles_used.get(chosen_style, 0) + 1
                print(f"PROGRESS:{len(tweets)}/{count}", flush=True)

    # Output tweets as JSON to stdout
    import json as _json
    result = {
        "tweets": tweets,
        "count": len(tweets),
        "styles": dict(styles_used),
    }
    print(_json.dumps(result))


def list_styles():
    """Print available styles and courses."""
    config = load_config()
    courses = load_courses()

    print("AVAILABLE STYLES:")
    print("  social_proof   — 'I've reviewed X courses...' with stats")
    print("  comparison     — Side-by-side course comparison")
    print("  urgency        — 'In 12 months it'll be a job requirement'")
    print("  salary         — Salary hook + course recommendation")
    print("  free_entry     — Free-to-start courses")
    print("  hot_take       — Bold claim + course recommendation")
    print("  listicle       — Numbered list of courses")
    print("  learning_path  — Multi-course progression")
    print()
    print("TRACKED COURSES (slugs for --focus):")
    for course in courses:
        slug = course.get("slug", course["url"].rstrip("/").split("/")[-1])
        print(f"  {slug:<40} {course['title']}")


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return

    if "--list" in sys.argv:
        list_styles()
        return

    count = 30
    if "--count" in sys.argv:
        idx = sys.argv.index("--count")
        if idx + 1 < len(sys.argv):
            count = int(sys.argv[idx + 1])

    focus_slug = None
    if "--focus" in sys.argv:
        idx = sys.argv.index("--focus")
        if idx + 1 < len(sys.argv):
            focus_slug = sys.argv[idx + 1]

    style = None
    if "--style" in sys.argv:
        idx = sys.argv.index("--style")
        if idx + 1 < len(sys.argv):
            style = sys.argv[idx + 1]

    output_file = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]

    generate_tweets(count=count, focus_slug=focus_slug, style=style, output_file=output_file)


if __name__ == "__main__":
    main()

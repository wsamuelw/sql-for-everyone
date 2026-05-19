# Coursera AI Affiliate Toolkit — Web App

Local web UI for generating tweets and managing affiliate links.

## Prerequisites

- Python 3.8+
- Flask

## Quick Start (Double-Click)

1. Double-click **`Start.command`** in the `Coursera AI Courses` folder
2. Browser opens automatically to http://localhost:5050

> Port 5000 is used by AirPlay on macOS. The app uses 5050 instead.

## Manual Start (Terminal)

```bash
cd "/Users/samuel/projects/Coursera AI Courses/App"
pip install flask    # install once
python3 app.py       # browser opens automatically
```

## First-Time Setup

### 1. Generate Affiliate Links

- Go to the **Affiliate Links** step
- Expand **Auto-Generate from Impact**
- Enter your Impact Account SID, Auth Token, and Program ID
- Click **Generate All Links**
- Credentials are saved automatically for next time

### 2. Generate Tweets

- Go to the **Generate** step
- Pick a style (Social Proof, Urgency, Salary Hook, etc.)
- Pick a count (5, 10, 20, or 30)
- Click **Generate Tweets** — watch the progress counter
- Each tweet shows which course it promotes (blue badge)
- Character count accounts for Twitter's 23-char link shortening
- Use **Copy** to copy, **X** to open X compose, **Bluesky** to open Bluesky compose

### 3. Refresh Course Data

- Go to the **Refresh Log** step and click **Run Refresh**
- Re-scrapes Coursera for updated enrollment numbers and ratings
- Fresh numbers = new tweet hooks

## Features

| Feature | What it does |
|---------|-------------|
| Generate | Create tweets with real-time progress, character count, course tags |
| Affiliate Links | Auto-generate via Impact API or paste manually |
| Courses | View all 30 tracked courses with ratings and enrollment |
| Refresh Log | Update enrollment/rating data from Coursera |
| X / Bluesky | One-click share to X or Bluesky with tweet pre-filled |
| Stop Server | Power button in header shuts down the app |

## Workflow

### Weekly

1. Open the app (double-click `Start.command`)
2. Generate a batch of tweets
3. Copy or download them
4. Paste into your scheduler (Buffer, Typefully, etc.)

### Monthly

1. Go to Refresh Log → Run Refresh
2. Generate fresh tweets with updated stats

## Generating Tweets via CLI

```bash
cd "/Users/samuel/projects/Coursera AI Courses/App/scripts"

# Generate 10 tweets with all styles
python3 generate_tweets.py --count 10

# Generate only urgency-style tweets
python3 generate_tweets.py --style urgency --count 5

# Focus on one course
python3 generate_tweets.py --focus ai-for-everyone --count 5

# List available styles and course slugs
python3 generate_tweets.py --list
```

## Refreshing Course Data via CLI

```bash
cd "/Users/samuel/projects/Coursera AI Courses/App/scripts"

# Refresh all courses
python3 refresh.py

# Preview changes without saving
python3 refresh.py --dry-run

# Add a new course
python3 refresh.py --add https://www.coursera.org/learn/COURSE-NAME
```

## Files

```
Coursera AI Courses/
├── Start.command              # Double-click to launch
├── data/
│   ├── config.json            # Affiliate links, Impact credentials, templates
│   ├── top_30.csv             # Course data (enrollment, ratings)
│   └── tweets.txt             # Generated tweets output
└── App/
    ├── app.py                 # Flask server
    ├── README.md              # This file
    ├── scripts/
    │   ├── refresh.py         # Re-scrape Coursera
    │   └── generate_tweets.py # Tweet generator
    └── templates/
        └── index.html         # Web UI
```

## Stopping the App

- Click the **power icon** in the top-right of the app header, or
- Press `Ctrl+C` in the Terminal window, or
- Run `pkill -f "python3 app.py"`

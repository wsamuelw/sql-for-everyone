#!/usr/bin/env python3
"""
Local web app for Coursera AI Affiliate Toolkit.
Run: python3 app.py
Open: http://localhost:5000
"""

import json
import os
import sys
import subprocess
import threading
import base64
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

from flask import Flask, render_template, jsonify, request, send_file

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
SCRIPTS_DIR = Path(__file__).parent / "scripts"
CONFIG_PATH = DATA_DIR / "config.json"
GENERATE_SCRIPT = SCRIPTS_DIR / "generate_tweets.py"

app = Flask(__name__)


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def load_courses_from_config():
    """Load courses from config.json."""
    config = load_config()
    courses = []
    for slug, c in config.get("courses", {}).items():
        courses.append({
            "slug": slug,
            "title": c.get("title", ""),
            "url": c.get("url", ""),
            "provider": c.get("provider", ""),
            "rating": c.get("rating", ""),
            "enrolled": c.get("enrolled", ""),
            "level": c.get("level", ""),
            "affiliate_link": c.get("affiliate_link", ""),
            "hook": c.get("hook", ""),
            "audience": c.get("audience", ""),
        })
    return courses


@app.route("/")
def index():
    config = load_config()
    course_list = load_courses_from_config()

    # Impact credentials
    impact_creds = config.get("impact_credentials", {})

    return render_template("index.html", courses=course_list, impact_creds=impact_creds)




@app.route("/api/generate", methods=["POST"])
def generate():
    """Run generate_tweets.py and return tweets as JSON."""
    data = request.json or {}
    count = data.get("count", 30)
    style = data.get("style", "")
    focus = data.get("focus", "")

    cmd = [sys.executable, str(GENERATE_SCRIPT), "--count", str(count)]
    if style:
        cmd.extend(["--style", style])
    if focus:
        cmd.extend(["--focus", focus])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(BASE_DIR),
        )

        # Parse tweets from stdout (JSON)
        tweets = []
        try:
            output = json.loads(result.stdout.strip().split("\n")[-1])
            tweets = output.get("tweets", [])
        except Exception:
            pass

        return jsonify({
            "success": result.returncode == 0,
            "tweets": tweets,
            "errors": result.stderr,
        })
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "tweets": "", "errors": "Generation timed out"})
    except Exception as e:
        return jsonify({"success": False, "tweets": "", "errors": str(e)})


@app.route("/api/links", methods=["GET"])
def get_links():
    """Get all affiliate links with course info."""
    config = load_config()
    links = {}
    courses = {}
    for slug, course in config["courses"].items():
        links[slug] = course.get("affiliate_link", "")
        courses[slug] = {
            "title": course.get("title", ""),
            "provider": course.get("provider", ""),
            "enrolled": course.get("enrolled", ""),
        }
    return jsonify({"links": links, "courses": courses})


@app.route("/api/links", methods=["POST"])
def save_links():
    """Save affiliate links."""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "No data provided"})

    config = load_config()
    for slug, link in data.items():
        if slug in config["courses"]:
            config["courses"][slug]["affiliate_link"] = link

    save_config(config)
    return jsonify({"success": True, "saved": len(data)})


@app.route("/api/tweets")
def get_tweets():
    """Get current tweets file content."""
    if TWEETS_PATH.exists():
        return jsonify({"tweets": TWEETS_PATH.read_text(encoding="utf-8")})
    return jsonify({"tweets": ""})


@app.route("/api/download")
def download_tweets():
    """Generate and download tweets as a .txt file."""
    from io import BytesIO
    data = request.args
    count = int(data.get("count", 30))
    style = data.get("style", "")

    cmd = [sys.executable, str(GENERATE_SCRIPT), "--count", str(count)]
    if style:
        cmd.extend(["--style", style])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=str(BASE_DIR))

    try:
        output = json.loads(result.stdout.strip().split("\n")[-1])
        tweets = output.get("tweets", [])
    except Exception:
        tweets = []

    if not tweets:
        return jsonify({"error": "No tweets generated"}), 404

    txt = "\n\n---\n\n".join(tweets)
    buf = BytesIO(txt.encode("utf-8"))
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name=f"tweets_{__import__('datetime').datetime.now().strftime('%Y%m%d')}.txt",
        mimetype="text/plain",
    )


@app.route("/api/styles")
def get_styles():
    """Get available tweet styles."""
    return jsonify({
        "styles": [
            {"id": "social_proof", "name": "Social Proof", "desc": "\"I've reviewed X courses...\" with stats"},
            {"id": "urgency", "name": "Urgency", "desc": "\"In 12 months it'll be a job requirement\""},
            {"id": "salary", "name": "Salary Hook", "desc": "Salary hook + course recommendation"},
            {"id": "free_entry", "name": "Free Entry", "desc": "Free-to-start courses"},
            {"id": "niche_down", "name": "Niche Down", "desc": "Targeted at specific audiences"},
            {"id": "hot_take", "name": "Hot Take", "desc": "Bold claim + recommendation"},
            {"id": "listicle", "name": "Listicle", "desc": "Numbered list of 10 courses"},
            {"id": "learning_path", "name": "Learning Path", "desc": "Multi-course progression"},
            {"id": "comparison", "name": "Comparison", "desc": "Side-by-side course comparison"},
        ]
    })


def generate_impact_link(account_sid, auth_token, program_id, course_url, sub_id1=""):
    """Call Impact API, follow redirect, build course-specific affiliate link."""
    import urllib.parse

    api_url = f"https://api.impact.com/Mediapartners/{account_sid}/Programs/{program_id}/TrackingLinks"
    body = {"SubId1": sub_id1} if sub_id1 else {}
    data = json.dumps(body).encode("utf-8")
    credentials = base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode()

    req = urllib.request.Request(api_url, data=data, method="POST")
    req.add_header("Authorization", f"Basic {credentials}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"error": str(e)}

    tracking_url = result.get("TrackingURL", "")
    if not tracking_url:
        return {"error": "No TrackingURL in response", "response": result}

    # Follow redirect to get tracking params
    try:
        redirect_url = tracking_url
        for _ in range(5):
            r = urllib.request.Request(redirect_url)
            r.add_header("User-Agent", "Mozilla/5.0")

            class NoRedirect(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, req, fp, code, msg, headers, newurl):
                    return None

            opener = urllib.request.build_opener(NoRedirect)
            try:
                opener.open(r, timeout=10)
                break
            except urllib.error.HTTPError as e:
                location = e.headers.get("Location", "")
                if location:
                    redirect_url = location
                else:
                    break
    except Exception:
        pass

    # Parse tracking params from final URL
    parsed = urllib.parse.urlparse(redirect_url)
    params = urllib.parse.parse_qs(parsed.query)

    # Build course-specific link
    course_path = urllib.parse.urlparse(course_url).path
    tracking_params = {
        "irclickid": params.get("irclickid", [""])[0],
        "irgwc": params.get("irgwc", ["1"])[0],
        "afsrc": params.get("afsrc", ["1"])[0],
        "utm_medium": params.get("utm_medium", ["partners"])[0],
        "utm_source": params.get("utm_source", ["impact"])[0],
        "utm_campaign": params.get("utm_campaign", [""])[0],
        "utm_content": params.get("utm_content", ["b2c"])[0],
        "utm_campaignid": params.get("utm_campaignid", [""])[0],
        "utm_term": params.get("utm_term", [""])[0],
    }

    query_string = urllib.parse.urlencode(tracking_params)
    final_link = f"https://www.coursera.org{course_path}?{query_string}"

    return {"TrackingURL": final_link}

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        return {"error": f"HTTP {e.code}: {error_body}"}
    except Exception as e:
        return {"error": str(e)}


@app.route("/api/impact-credentials", methods=["GET", "POST"])
def impact_credentials():
    """Load or save Impact API credentials."""
    config = load_config()
    if request.method == "GET":
        return jsonify(config.get("impact_credentials", {}))
    data = request.json or {}
    config["impact_credentials"] = {
        "account_sid": data.get("account_sid", ""),
        "auth_token": data.get("auth_token", ""),
        "program_id": data.get("program_id", ""),
    }
    save_config(config)
    return jsonify({"success": True})


@app.route("/api/generate-links", methods=["POST"])
def generate_links():
    """Generate tracking links via Impact API for all courses."""
    data = request.json or {}
    account_sid = data.get("account_sid", "")
    auth_token = data.get("auth_token", "")
    program_id = data.get("program_id", "")

    if not all([account_sid, auth_token, program_id]):
        return jsonify({"success": False, "error": "Missing credentials. Fill in Account SID, Auth Token, and Program ID."})

    config = load_config()
    courses = config["courses"]

    results = []
    updated = 0
    errors = 0

    for slug, course in courses.items():
        dest_url = course["url"]
        result = generate_impact_link(account_sid, auth_token, program_id, dest_url, sub_id1=slug)

        if "error" in result:
            results.append({"slug": slug, "status": "error", "message": result["error"]})
            errors += 1
            continue

        # Extract tracking link from response
        tracking_link = (
            result.get("TrackingURL")
            or result.get("TrackingLink")
            or result.get("trackingLink")
            or result.get("tracking_link")
            or result.get("Link")
            or result.get("link")
            or ""
        )

        if tracking_link:
            config["courses"][slug]["affiliate_link"] = tracking_link
            results.append({"slug": slug, "status": "ok", "link": tracking_link})
            updated += 1
        else:
            results.append({"slug": slug, "status": "no_link", "response": result})
            errors += 1

    if updated > 0:
        save_config(config)

    return jsonify({
        "success": updated > 0,
        "updated": updated,
        "errors": errors,
        "results": results,
    })


@app.route("/api/search-courses", methods=["POST"])
def search_courses():
    """Search Coursera for courses via GraphQL API, scrape enrollment for top 15."""
    import re as _re
    import concurrent.futures

    data = request.json or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"success": False, "error": "Enter a search keyword"})

    gql_url = "https://www.coursera.org/graphql-gateway?opname=Search"
    payload = {
        "operationName": "Search",
        "variables": {
            "requests": [{
                "query": query,
                "entityType": "PRODUCTS",
                "limit": 50,
            }]
        },
        "query": """query Search($requests: [Search_Request!]!) {
            SearchResult {
                search(requests: $requests) {
                    elements {
                        ... on Search_ProductHit {
                            name
                            avgProductRating
                            numProductRatings
                            productDifficultyLevel
                            productDuration
                            partners
                            url
                            productType
                        }
                    }
                    pagination { totalElements }
                }
            }
        }"""
    }

    data_bytes = json.dumps(payload).encode()
    req = urllib.request.Request(gql_url, data_bytes, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    req.add_header("Accept", "application/json")
    req.add_header("Referer", f"https://www.coursera.org/search?query={urllib.parse.quote(query)}")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    elements = result.get("data", {}).get("SearchResult", {}).get("search", [{}])[0].get("elements", [])

    courses = []
    for el in elements:
        partners = el.get("partners", [])
        provider = ", ".join(partners) if isinstance(partners, list) else str(partners)
        rating = el.get("avgProductRating")
        rating_str = f"{rating:.1f}" if isinstance(rating, (int, float)) else ""
        level = (el.get("productDifficultyLevel") or "").title()
        course_url = "https://www.coursera.org" + el.get("url", "") if el.get("url", "").startswith("/") else el.get("url", "")
        slug = course_url.rstrip("/").split("/")[-1]

        courses.append({
            "title": el.get("name", ""),
            "url": course_url,
            "slug": slug,
            "provider": provider,
            "rating": rating_str,
            "enrolled": "",
            "level": level,
        })

    # Scrape enrollment for top 15 only (fast)
    def fetch_enrollment(course):
        try:
            r = urllib.request.Request(course["url"], headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "text/html",
            })
            with urllib.request.urlopen(r, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
            m = _re.search(r'"total(?:Historical)?[Ee]nrollment(?:Count)?"\s*:\s*(\d+)', html)
            if m:
                course["enrolled"] = f"{int(m.group(1)):,}"
            else:
                m = _re.search(r'([\d,]+)\s+already\s+enrolled', html)
                if m:
                    course["enrolled"] = m.group(1)
        except Exception:
            pass
        return course

    top_courses = courses[:15]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(fetch_enrollment, top_courses)

    # Sort by enrollment descending
    def parse_num(c):
        try:
            return int(c["enrolled"].replace(",", ""))
        except:
            return 0
    courses.sort(key=parse_num, reverse=True)

    return jsonify({"success": True, "courses": courses, "query": query})


@app.route("/api/add-course", methods=["POST"])
def add_course():
    """Add a course to tracking list."""
    import re as _re
    data = request.json or {}
    url = data.get("url", "").strip()
    title = data.get("title", "").strip()
    provider = data.get("provider", "").strip()

    if not url:
        return jsonify({"success": False, "error": "URL required"})

    slug = url.rstrip("/").split("/")[-1]

    # Check if already exists
    config = load_config()
    if slug in config["courses"]:
        return jsonify({"success": False, "error": "Course already tracked"})

    # Scrape enrollment and rating from the course page
    enrolled = ""
    rating = ""
    level = ""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        # Enrollment
        m = _re.search(r'"total(?:Historical)?[Ee]nrollment(?:Count)?"\s*:\s*(\d+)', html)
        if m:
            enrolled = f"{int(m.group(1)):,}"
        if not enrolled:
            m = _re.search(r'([\d,]+)\s+already\s+enrolled', html)
            if m:
                enrolled = m.group(1)

        # Rating
        m = _re.search(r'"averageRating"\s*:\s*"?([\d.]+)"?', html)
        if not m:
            m = _re.search(r'"ratingValue"\s*:\s*"?([\d.]+)"?', html)
        if m:
            rating = str(round(float(m.group(1)), 1))

        # Level
        m = _re.search(r'"educationalLevel"\s*:\s*"(\w+)"', html)
        if not m:
            m = _re.search(r'(Beginner|Intermediate|Advanced)\s*level', html)
        if m:
            level = m.group(1).title()
    except Exception:
        pass

    if not title:
        title = slug.replace("-", " ").title()

    # Add to config
    config["courses"][slug] = {
        "url": url,
        "title": title,
        "provider": provider,
        "rating": rating,
        "enrolled": enrolled,
        "level": level,
        "affiliate_link": "",
        "tags": [],
        "audience": "",
        "hook": "",
        "priority": len(config["courses"]) + 1,
    }
    save_config(config)

    return jsonify({
        "success": True,
        "course": {
            "slug": slug,
            "title": title,
            "provider": provider,
            "url": url,
            "enrolled": enrolled,
            "rating": rating,
            "level": level,
        }
    })


@app.route("/api/remove-course", methods=["POST"])
def remove_course():
    """Remove a course from tracking list."""
    data = request.json or {}
    slug = data.get("slug", "")
    if not slug:
        return jsonify({"success": False, "error": "Slug required"})

    config = load_config()
    if slug in config["courses"]:
        del config["courses"][slug]
        save_config(config)

    return jsonify({"success": True})


@app.route("/api/stop", methods=["POST"])
def stop_server():
    """Shut down the Flask dev server."""
    def shutdown():
        os._exit(0)
    threading.Thread(target=shutdown, daemon=True).start()
    return jsonify({"success": True, "message": "Server shutting down"})


if __name__ == "__main__":
    print("=" * 50)
    print("  Coursera AI Affiliate Toolkit")
    print("  Open: http://localhost:5050")
    print("=" * 50)
    app.run(debug=True, port=5050)

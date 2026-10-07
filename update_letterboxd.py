import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

LETTERBOXD_USERNAME = "kayarecepomer"
START_TAG = "<!-- LETTERBOXD_START -->"
END_TAG = "<!-- LETTERBOXD_END -->"
STATE_PATTERN = r"<!-- LETTERBOXD_STATE year=(?P<year>\d+) count=(?P<count>\d+) last=(?P<last>\d+) -->"
LETTERBOXD_NS = {"letterboxd": "https://letterboxd.com"}

def fetch(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")

def get_total_films(username):
    # The profile page sits behind a Cloudflare challenge, the films page does not.
    html = fetch(f"https://letterboxd.com/{username}/films/")
    match = re.search(r'title="([\d,]+)(?:&nbsp;|\s)films?"', html)
    if not match:
        raise RuntimeError("Could not find the total film count on the films page.")
    return match.group(1)

def get_year_count(username, year, state):
    # The RSS feed only holds the latest ~50 entries, so the yearly total is
    # kept in a hidden README comment and bumped for every newer diary entry.
    if state.get("year") != year:
        state = {"year": year, "count": 0, "last": 0}

    newest = state["last"]
    root = ET.fromstring(fetch(f"https://letterboxd.com/{username}/rss/"))
    for item in root.iter("item"):
        watched = item.findtext("letterboxd:watchedDate", namespaces=LETTERBOXD_NS)
        guid = re.fullmatch(r"letterboxd-watch-(\d+)", item.findtext("guid") or "")
        if not watched or not guid or not watched.startswith(f"{year}-"):
            continue
        entry_id = int(guid.group(1))
        if entry_id > state["last"]:
            state["count"] += 1
            newest = max(newest, entry_id)

    state["last"] = newest
    return state

def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    if START_TAG not in content or END_TAG not in content:
        raise RuntimeError("Tracking comments are completely missing from the target file.")

    match = re.search(STATE_PATTERN, content)
    state = {k: int(v) for k, v in match.groupdict().items()} if match else {}
    return content, state

def update_readme(content, films, state):
    # Split and rebuild without matching variants
    parts_before = content.split(START_TAG)
    parts_after = parts_before[1].split(END_TAG)
    
    clean_prefix = parts_before[0] + START_TAG
    clean_suffix = END_TAG + parts_after[1]
    
    new_metrics = f"\n🍿 **Total Films Watched:** {films} | 📅 **Films Watched in {state['year']}:** {state['count']} | 🎬 **Profile:** [Letterboxd](https://letterboxd.com/{LETTERBOXD_USERNAME}) *(Updates Daily!)*\n"
    new_state = f"<!-- LETTERBOXD_STATE year={state['year']} count={state['count']} last={state['last']} -->\n"
    
    final_output = clean_prefix + new_metrics + new_state + clean_suffix

    with open("README.md", "w", encoding="utf-8", newline="") as f:
        f.write(final_output)

if __name__ == "__main__":
    try:
        current_year = datetime.now(timezone.utc).year
        readme, saved_state = read_readme()
        f_count = get_total_films(LETTERBOXD_USERNAME)
        new_state = get_year_count(LETTERBOXD_USERNAME, current_year, saved_state)
        print(f"Scraper verified -> Total Watched: {f_count}, {current_year} Diary: {new_state['count']}")
        update_readme(readme, f_count, new_state)
    except Exception as e:
        # Fail the job so a blocked scrape shows up red instead of passing silently.
        print(f"Workflow execution error: {e}")
        sys.exit(1)

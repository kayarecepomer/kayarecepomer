import re
import urllib.request
from bs4 import BeautifulSoup

LETTERBOXD_USERNAME = "kayarecepomer"

def get_letterboxd_stats(username):
    url = f"https://letterboxd.com/{username}/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req) as response:
        html = response.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    html_str = str(soup)
    
    films_count = "0"
    nav_films = soup.find('a', href=f"/{username}/films/")
    if nav_films:
        val_span = nav_films.find('span', class_='value')
        if val_span:
            films_count = val_span.text.strip()
        else:
            text_content = nav_films.get_text(separator=" ").strip()
            match = re.search(r'([\d,]+)\s*Films', text_content, re.IGNORECASE)
            if match:
                films_count = match.group(1)

    year_count = "0"
    current_year = "2026"
    year_link = soup.find('a', href=f"/{username}/diary/for/{current_year}/")
    if year_link:
        val_span = year_link.find('span', class_='value')
        if val_span:
            year_count = val_span.text.strip()

    return films_count, year_count

def update_readme(films, year):
    start_tag = "<!-- LETTERBOXD_START -->"
    end_tag = "<!-- LETTERBOXD_END -->"
    
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    if start_tag not in content or end_tag not in content:
        print("Error: Tracking comments are completely missing from the target file.")
        return

    # Split and rebuild without matching variants
    parts_before = content.split(start_tag)
    parts_after = parts_before[1].split(end_tag)
    
    clean_prefix = parts_before[0] + start_tag
    clean_suffix = end_tag + parts_after[1]
    
    new_metrics = f"\n🍿 **Total Films Watched:** {films} | 📅 **Films Watched in 2026:** {year} | 🎬 **Profile:** [Letterboxd](https://letterboxd.com/{LETTERBOXD_USERNAME}) *(Updates Daily!)*\n"
    
    final_output = clean_prefix + new_metrics + clean_suffix

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(final_output)

if __name__ == "__main__":
    try:
        f_count, y_count = get_letterboxd_stats(LETTERBOXD_USERNAME)
        print(f"Scraper verified -> Total Watched: {f_count}, 2026 Diary: {y_count}")
        update_readme(f_count, y_count)
    except Exception as e:
        print(f"Workflow execution error: {e}")

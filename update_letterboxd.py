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
    year_match = re.search(r'href="/' + username + r'/films/diary/for/2026/".*?>([\d,]+)</a>', html_str, re.IGNORECASE)
    if not year_match:
        year_match = re.search(r'for/2026/.*?<span class="value">([\d,]+)</span>', html_str, re.IGNORECASE)
    if not year_count or year_count == "0":
        nav_year = soup.find('a', href=f"/{username}/films/diary/")
        if nav_year:
            val_span = nav_year.find('span', class_='value')
            if val_span:
                year_count = val_span.text.strip()

    if year_match:
        year_count = year_match.group(1)
            
    return films_count, year_count

def update_readme(films, year):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r".*?"
    
    new_stats_block = (
        f"\n"
        f"🍿 **Total Films Watched:** {films} | 📅 **Films Watched in 2026:** {year} | 🎬 **Profile:** [Letterboxd](https://letterboxd.com/{LETTERBOXD_USERNAME}) *(Updates Daily!)*\n"
        f""
    )

    if not re.search(pattern, content, re.DOTALL):
        print("Error: Target comments missing from README.md template file.")
        return

    updated_content = re.sub(pattern, new_stats_block, content, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated_content)

if __name__ == "__main__":
    try:
        f_count, y_count = get_letterboxd_stats(LETTERBOXD_USERNAME)
        print(f"Scrape verified - Total Watched: {f_count}, Year Active: {y_count}")
        update_readme(f_count, y_count)
    except Exception as e:
        print(f"System error: {e}")

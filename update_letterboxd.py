import re
import urllib.request
from bs4 import BeautifulSoup

LETTERBOXD_USERNAME = "kayarecepomer"

def get_letterboxd_stats(username):
    url = f"[https://letterboxd.com/](https://letterboxd.com/){username}/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req) as response:
        html = response.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    nav_films = soup.find('a', href=f"/{username}/films/")
    films_count = "0"
    if nav_films:
        val_span = nav_films.find('span', class_='value')
        if val_span:
            films_count = val_span.text.strip()
            
    nav_this_year = soup.find('a', href=f"/{username}/films/diary/for/2026/")
    year_count = "0"
    if nav_this_year:
        val_span = nav_this_year.find('span', class_='value')
        if val_span:
            year_count = val_span.text.strip()
            
    return films_count, year_count

def update_readme(films, year):
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    stats_block = (
        f"<!-- LETTERBOXD-STATS:START -->\n"
        f"🍿 **Total Films Watched:** {films} | "
        f"📅 **Films Watched in 2026:** {year}\n"
        f"<!-- LETTERBOXD-STATS:END -->"
    )

    pattern = r"<!-- LETTERBOXD-STATS:START -->.*?<!-- LETTERBOXD-STATS:END -->"
    updated_readme = re.sub(pattern, stats_block, readme, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated_readme)

if __name__ == "__main__":
    try:
        f_count, y_count = get_letterboxd_stats(LETTERBOXD_USERNAME)
        update_readme(f_count, y_count)
    except Exception as e:
        print(f"Error updating Letterboxd stats: {e}")

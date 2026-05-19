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
    nav_this_year = soup.find('a', href=f"/{username}/films/diary/for/2026/")
    if nav_this_year:
        val_span = nav_this_year.find('span', class_='value')
        if val_span:
            year_count = val_span.text.strip()
        else:
            text_content = nav_this_year.get_text(separator=" ").strip()
            match = re.search(r'([\d,]+)', text_content)
            if match:
                year_count = match.group(1)
            
    return films_count, year_count

def update_readme(films, year):
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    stats_block = (
        f"\n"
        f"🍿 **Total Films Watched:** {films} | "
        f"📅 **Films Watched in 2026:** {year}\n"
        f""
    )

    pattern = r".*?"
    updated_readme = re.sub(pattern, stats_block, readme, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated_readme)

if __name__ == "__main__":
    try:
        f_count, y_count = get_letterboxd_stats(LETTERBOXD_USERNAME)
        print(f"Successfully retrieved stats - Total: {f_count}, 2026: {y_count}")
        update_readme(f_count, y_count)
    except Exception as e:
        print(f"Error updating Letterboxd stats: {e}")

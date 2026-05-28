import requests
from bs4 import BeautifulSoup
import json
import os

groups = {}
group_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

for letter in group_letters:
    url = f"https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_{letter}"
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        
        teams = []
        # Find all rows in the table body
        rows = soup.select("table.wikitable tbody tr")
        for row in rows:
            cols = row.find_all("td")
            # Team name is in the second column
            if len(cols) > 1:
                team_link = cols[1].find("a")

                if team_link:
                    teams.append(team_link.get_text(strip=True))
        if teams:
            groups[f"Group {letter}"] = teams
            print(f"Group {letter}: {teams}")
    except Exception as e:
        print(f"Error fetching Group {letter}: {e}")

# Ensure the data directory exists
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(data_dir, exist_ok=True)

# Write the groups data to a JSON file
output_path = os.path.join(data_dir, "groups.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(groups, f, ensure_ascii=False, indent=2)

print(f"\nSuccessfully extracted {len(groups)} groups and saved to {output_path}")
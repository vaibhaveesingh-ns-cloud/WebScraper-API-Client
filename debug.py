import requests
from bs4 import BeautifulSoup
import json

url = "https://americanliterature.com/childrens-stories/the-three-little-pigs"
resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")

# Try multiple possible containers
story_div = soup.find("div", class_="al-jumbotron")
if not story_div:
    story_div = soup.find("div", class_="jumbotron")
if not story_div:
    print("Story container not found.")
    exit()

# Extract paragraphs as scenes
scenes = []
for p in story_div.find_all("p"):
    text = p.get_text(strip=True)
    if text:
        scenes.append(text)

# Save scenes to JSON
with open("three_little_pigs_scenes.json", "w", encoding="utf-8") as f:
    json.dump({"scenes": scenes}, f, ensure_ascii=False, indent=2)

print("Scenes have been saved to 'three_little_pigs_scenes.json'.")

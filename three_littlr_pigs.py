import requests
from bs4 import BeautifulSoup
import json

def scrape_three_little_pigs(url):
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract title
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "Unknown Title"

    # Extract story paragraphs from the story-content div (by ID)
    story_div = soup.find("div", id="story-content")
    if not story_div:
        raise ValueError("❌ Could not find story content on the page")

    paragraphs = [p.get_text(strip=True) for p in story_div.find_all("p") if p.get_text(strip=True)]

    # Convert paragraphs into scenes
    scenes = [{"scene_number": i+1, "text": para} for i, para in enumerate(paragraphs)]

    return {"title": title, "link": url, "scenes": scenes}


if __name__ == "__main__":
    url = "https://americanliterature.com/childrens-stories/the-three-little-pigs"
    story_data = scrape_three_little_pigs(url)
    print(json.dumps(story_data, indent=2, ensure_ascii=False))




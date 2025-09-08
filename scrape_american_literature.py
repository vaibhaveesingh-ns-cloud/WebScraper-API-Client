import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin


BASE_URL = "https://americanliterature.com/childrens-stories/the-three-little-pigs"


def get_story_links(base_url):
    """
    Extracts all story links from the American Literature children's stories index page.
    """
    story_links = []
    response = requests.get(base_url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Stories are inside <div class="short-stories-list">
    for link in soup.select("div.short-stories-list a"):
        href = link.get("href")
        if href:
            story_links.append(urljoin(base_url, href))

    return list(set(story_links))  # unique links


def scrape_story(url):
    """
    Scrapes an individual story page and splits into scenes (paragraphs).
    """
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Title is in <h1>
    title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "Untitled Story"

    # Extract story paragraphs from <article>
    paragraphs = []
    article = soup.find("article")
    if article:
        paragraphs = [p.get_text(strip=True) for p in article.find_all("p") if p.get_text(strip=True)]

    # Convert paragraphs into scenes
    scenes = [{"scene_number": i + 1, "text": para} for i, para in enumerate(paragraphs)]

    return {
        "title": title,
        "link": url,
        "scenes": scenes
    }


def scrape_american_literature(output_file="americanliterature_stories.json"):
    """
    Scrapes all children's stories from American Literature and saves them in JSON.
    """
    print("🔍 Fetching story links...")
    story_links = get_story_links(BASE_URL)
    print(f"✅ Found {len(story_links)} stories")

    all_stories = []
    for idx, story_url in enumerate(story_links, start=1):
        print(f"📖 Scraping story {idx}/{len(story_links)}: {story_url}")
        story_data = scrape_story(story_url)
        all_stories.append(story_data)

    # Save to JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_stories, f, indent=4, ensure_ascii=False)

    print(f"\n🎉 All stories saved to {output_file}")


if __name__ == "__main__":
    scrape_american_literature()

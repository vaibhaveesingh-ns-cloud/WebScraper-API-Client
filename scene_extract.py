from requests_html import HTMLSession
import json

def scrape_three_little_pigs(url):
    session = HTMLSession()
    r = session.get(url)
    r.html.render(timeout=30)   # render JavaScript

    title = r.html.find("h1", first=True).text
    story_div = r.html.find("div#story-content", first=True)

    if not story_div:
        raise ValueError("❌ Still could not find story content")

    paragraphs = [p.text for p in story_div.find("p") if p.text.strip()]
    scenes = [{"scene_number": i+1, "text": para} for i, para in enumerate(paragraphs)]

    return {"title": title, "link": url, "scenes": scenes}


if __name__ == "__main__":
    url = "https://americanliterature.com/childrens-stories/the-three-little-pigs"
    story_data = scrape_three_little_pigs(url)
    print(json.dumps(story_data, indent=2, ensure_ascii=False))

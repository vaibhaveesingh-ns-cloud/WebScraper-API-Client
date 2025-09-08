import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_stories_from_url(url):
    """
    Scrapes a given URL and extracts potential short story links.
    Returns a list of dictionaries with story title and link.
    """
    stories = []
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.find_all("a", href=True):
            href = link["href"]
            title = link.get_text(strip=True)

            # Heuristic filter: include only story-related links
            if any(keyword in href.lower() for keyword in ["story", "stories", "fairy", "tale", "fable"]):
                full_url = urljoin(url, href)  # handle relative links
                if title:  # ignore empty text links
                    stories.append({
                        "title": title,
                        "link": full_url
                    })

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
    
    return stories


def scrape_all_sites(results_json, output_file="all_stories.json"):
    """
    Takes search results JSON, scrapes each site, and saves all stories to output file.
    """
    all_stories = {}

    for result in results_json:
        site_url = result["link"]
        print(f"🔍 Scraping stories from: {site_url}")

        site_stories = scrape_stories_from_url(site_url)
        all_stories[site_url] = site_stories
    
    # Save to JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_stories, f, indent=4, ensure_ascii=False)

    print(f"✅ Scraped stories saved to {output_file}")


if __name__ == "__main__":
    # Load your search results (paste your JSON here or load from file)
    search_results = [
    {
        "title": "Stories for Kids",
        "link": "https://www.freechildrenstories.com/",
        "snippet": "Check out some of our most popular free kids stories online. Fun stories that have been read by kids, parents, teachers, and guardians all over the world!"
    },
    {
        "title": "Short Stories for Children - American Literature",
        "link": "https://americanliterature.com/short-stories-for-children/",
        "snippet": "Short stories for Children, fairytales, nursery rhymes and fables; The Three Little Pigs, Snow White, Tom Thumb, Little Red Riding Hood, and other childhood ..."
    },
    {
        "title": "25 Best Short Moral Stories for Kids | Fun with Life Lessons",
        "link": "https://www.bachpanglobal.com/blog/best-short-moral-stories-for-kids/",
        "snippet": "Discover 25 engaging short moral stories for kids that teach honesty, kindness, and courage—perfect for bedtime or classroom learning."
    },
    {
        "title": "Short Kid Stories: Short Stories for Kids",
        "link": "https://www.shortkidstories.com/",
        "snippet": "Short kid stories is the best place online to find hundreds of short stories for kids. Select by age, reading time, author or type and read on any device."
    },
    {
        "title": "Can anyone recommend some good SHORT children's stories.",
        "link": "https://www.reddit.com/r/suggestmeabook/comments/1dkwjlo/can_anyone_recommend_some_good_short_childrens/",
        "snippet": "I found some other ideas like horrid Henry (lexile level 400 - 500) And the goosebumps series I really loved as a kid (lexile level 370 - 420) ..."
    },
    {
        "title": "Popular Bedtime Stories",
        "link": "https://www.readthetale.com/popular-bedtime-stories",
        "snippet": "Rapunzel by Age is a special collection where the classic fairy tale of Rapunzel is retold to suit different age groups, from toddlers to older children. · The ..."
    },
    {
        "title": "I am looking for some amazing short stories for 7-10 year old boys.",
        "link": "https://www.reddit.com/r/audiobooks/comments/orb91h/i_am_looking_for_some_amazing_short_stories_for/",
        "snippet": "The Book of Dragons – A more classic set of dragon stories, great for kids who love fantasy. We've listened to most of these either through the ..."
    },
    {
        "title": "15 Short Stories With Moral for Kids & Its Benefits | KLAY",
        "link": "https://klay.co.in/blog/short-moral-stories-in-english-for-kids/",
        "snippet": "These tales help children understand values like kindness, courage, and friendship, encouraging them to grow into thoughtful, compassionate individuals."
    },
    {
        "title": "40 Excellent Short Stories For Middle School in 2025 - reThink ELA",
        "link": "https://www.rethinkela.com/2014/05/40-excellent-short-stories-for-middle-school/",
        "snippet": "The 40 stories below are sometimes surprising, other times hair-raising. They are all guaranteed to raise questions and instigate discussions in your classroom."
    },
    {
        "title": "Free Bedtime Stories, Fairy Tales, Online Storybooks and Audio ...",
        "link": "https://www.storyberries.com/",
        "snippet": "The House on Chicken Legs. Beyond the thrice-nine kingdoms, beyond the fiery river... A dark fairy tale retelling of the fairytale Baba Yaga."
    }
]

    scrape_all_sites(search_results)

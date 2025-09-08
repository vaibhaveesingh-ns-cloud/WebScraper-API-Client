import os
import requests
import json
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Load environment variables from .env file (make sure SERPER_API_KEY is stored there)
load_dotenv()
API_KEY = os.getenv("SERPER_API_KEY")

if not API_KEY:
    raise ValueError("❌ SERPER_API_KEY not found in environment variables!")

# Custom exception for API errors
class SerperAPIError(Exception):
    pass

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), retry=retry_if_exception_type(SerperAPIError))
def search_google(query: str, num_results: int = 10):
    """
    Calls the Serper API to fetch Google search results.
    Returns a list of dictionaries with title, link, and snippet.
    """

    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}
    payload = {"q": query}

    response = requests.post(url, headers=headers, json=payload, timeout=10)

    if response.status_code != 200:
        raise SerperAPIError(f"API request failed with status {response.status_code}: {response.text}")

    data = response.json()

    results = []
    for item in data.get("organic", [])[:num_results]:
        results.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })

    return results

if __name__ == "__main__":
    topic = "Most Searched Short Stories for Kids"
    search_results = search_google(topic, num_results=10)

    # Save results to JSON
    output_file = "search_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(search_results, f, indent=4, ensure_ascii=False)

    print(f"✅ Top 10 search results for '{topic}' saved to {output_file}")

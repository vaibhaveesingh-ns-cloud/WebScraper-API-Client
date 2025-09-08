import requests
import json
import os

# Load your API key (store it in environment variable for safety)
SCENARIO_API_KEY = os.getenv("SCENARIO_API_KEY")

def generate_image_from_scene(scene_text, scene_number):
    url = "https://api.cloud.scenario.com/v1/generation/text-to-image"
 # ✅ correct endpoint

    headers = {
        "Authorization": f"Bearer {SCENARIO_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": f"Illustration of scene {scene_number}: {scene_text}",
        "width": 1024,
        "height": 1024,
        "num_images": 1
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    # Load scenes from JSON file
    with open("three_little_pigs_scenes.json", "r", encoding="utf-8") as f:
        story_data = json.load(f)

    results = []
    for idx, scene_text in enumerate(story_data["scenes"], 1):
        print(f"🎨 Generating image for Scene {idx}...")
        image_data = generate_image_from_scene(scene_text, idx)
        results.append({
            "scene_number": idx,
            "scene_text": scene_text,
            "image_data": image_data
        })

    # Save all results to a new JSON file
    with open("three_little_pigs_images.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("All images generated and saved to three_little_pigs_images.json.")

#!/usr/bin/env python3
"""
Generate images from scenes (JSON) using the Scenario API.
Saves output images to ./outputs/scene_<index>/
"""

import os
import time
import json
import base64
import pathlib
import argparse
from typing import Optional
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SCENARIO_BASE = "https://api.cloud.scenario.com/v1"
TXT2IMG_ENDPOINT = f"{SCENARIO_BASE}/generate/txt2img"
JOB_ENDPOINT = f"{SCENARIO_BASE}/jobs"          # use /jobs/{jobId} - for long running tasks (e.g. txt2img)
ASSET_ENDPOINT = f"{SCENARIO_BASE}/assets"      # use /assets/{assetId} - for short running tasks (e.g. asset download)

def load_scenes(json_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    scenes = data.get("scenes") or data.get("Scenes") or []
    if not isinstance(scenes, list):
        raise ValueError("JSON 'scenes' must be a list of strings.")
    return scenes

def make_auth_headers(api_key: str, api_secret: Optional[str]):
    """
    Create Basic Auth headers for Scenario API.
    Scenario API requires Basic authentication with api_key:api_secret encoded in base64.
    """
    if not api_secret:
        raise ValueError("Scenario API requires both API key and API secret for Basic authentication")
    
    credentials = f"{api_key}:{api_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode() # base64 encoded credentials for Basic Auth
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    return headers, None

def submit_txt2img(prompt: str, model_id: str, api_key: str, api_secret: Optional[str]=None, width=1024, height=1024, guidance=7.5, steps=30, num_samples=1):
    payload = {
        "prompt": prompt,
        "numSamples": num_samples,
        "guidance": guidance,
        "numInferenceSteps": steps,
        "width": width,
        "height": height,
        "modelId": model_id
    }
    headers, _ = make_auth_headers(api_key, api_secret)
    resp = requests.post(TXT2IMG_ENDPOINT, json=payload, headers=headers)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        print(f"Submission failed with status code {e.response.status_code}: {e.response.text}")
        raise
    return resp.json()   # contains job info with jobId

def poll_job(job_id: str, api_key: str, api_secret: Optional[str]=None, poll_interval=3, timeout=300):
    url = f"{SCENARIO_BASE}/jobs/{job_id}"
    headers, _ = make_auth_headers(api_key, api_secret)
    start = time.time()
    while True:
        r = requests.get(url, headers=headers)
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            print(f"Polling failed with status code {e.response.status_code}: {e.response.text}")
            raise
        data = r.json()
        status = data.get("job", {}).get("status")
        # print progress info
        progress = data.get("job", {}).get("progress")
        print(f"Polling job {job_id} — status: {status}, progress: {progress}")
        if status == "success":
            return data["job"]
        if status in ("failure", "canceled"):
            raise RuntimeError(f"Job {job_id} ended with status: {status} - {json.dumps(data)}")
        if (time.time() - start) > timeout:
            raise TimeoutError(f"Polling job {job_id} timed out after {timeout} seconds.")
        time.sleep(poll_interval)

def fetch_asset_url(asset_id: str, api_key: str, api_secret: Optional[str]=None):
    url = f"{ASSET_ENDPOINT}/{asset_id}"
    headers, _ = make_auth_headers(api_key, api_secret)
    r = requests.get(url, headers=headers)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        print(f"Failed to fetch asset URL with status code {e.response.status_code}: {e.response.text}")
        raise
    data = r.json()
    # expected: data["asset"]["url"]
    return data["asset"]["url"]

def download_file(url: str, dest_path: pathlib.Path):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, stream=True)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        print(f"Failed to download file with status code {e.response.status_code}: {e.response.text}")
        raise
    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return dest_path

def main(args):
    scenes = load_scenes(args.json)
    api_key = os.getenv("SCENARIO_API_KEY") or args.api_key
    api_secret = os.getenv("SCENARIO_API_SECRET") or args.api_secret
    
    # Debug: Check if API key is loaded
    if api_key:
        print(f"API Key loaded: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else api_key}")
    else:
        print("No API key found!")
    
    if not api_key:
        raise SystemExit("Provide SCENARIO_API_KEY in env or --api-key")
    
    if not api_secret:
        raise SystemExit("Provide SCENARIO_API_SECRET in env or --api-secret. Scenario API requires both key and secret for Basic authentication.")

    model_id = args.model_id or "flux.1-dev"  # change if you have a preferred model

    out_root = pathlib.Path(args.out_dir)
    out_root.mkdir(parents=True, exist_ok=True)

    for i, scene in enumerate(scenes, start=1):
        print(f"\n=== Scene {i}/{len(scenes)} ===")
        safe_scene = (scene[:80] + "...") if len(scene) > 80 else scene
        print("Prompt:", safe_scene)
        try:
            resp = submit_txt2img(
                prompt=scene,
                model_id=model_id,
                api_key=api_key,
                api_secret=api_secret,
                width=args.width,
                height=args.height,
                guidance=args.guidance,
                steps=args.steps,
                num_samples=args.num_samples
            )
        except requests.HTTPError as e:
            print("Submission failed:", e.response.text if e.response is not None else e)
            continue

        # extract jobId (response JSON layout: { "job": { "jobId": "..." } , ... })
        job_obj = resp.get("job") or resp.get("data") or {}
        job_id = job_obj.get("jobId") or job_obj.get("id")
        if not job_id:
            print("Could not find jobId in response:", resp)
            continue

        print("Submitted job:", job_id)
        job_info = poll_job(job_id, api_key=api_key, api_secret=api_secret, poll_interval=args.poll_interval, timeout=args.timeout)

        asset_ids = job_info.get("metadata", {}).get("assetIds", [])
        if not asset_ids:
            print("No assets returned for job", job_id)
            continue

        scene_out_dir = out_root / f"scene_{i:03d}"
        scene_out_dir.mkdir(parents=True, exist_ok=True)

        for idx, aid in enumerate(asset_ids, start=1):
            try:
                asset_url = fetch_asset_url(aid, api_key=api_key, api_secret=api_secret)
                fname = scene_out_dir / f"scene_{i:03d}_asset_{idx}.png"
                print(f"Downloading asset {aid} -> {fname}")
                download_file(asset_url, fname)
            except Exception as e:
                print(f"Failed to download asset {aid}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate images from scenes JSON using Scenario API")
    parser.add_argument("--json", default="scenes.json", help="Path to scenes JSON file")
    parser.add_argument("--api-key", help="Scenario API key (optional if env var set)")
    parser.add_argument("--api-secret", help="Scenario API secret (optional)")
    parser.add_argument("--model-id", help="Scenario modelId to use (default flux.1-dev)")
    parser.add_argument("--out-dir", default="outputs", help="Output directory")
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--guidance", type=float, default=10)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--num-samples", type=int, default=1)
    parser.add_argument("--poll-interval", type=int, default=3, help="Seconds between job polls")
    parser.add_argument("--timeout", type=int, default=300, help="Polling timeout in seconds per job")
    args = parser.parse_args()
    main(args)

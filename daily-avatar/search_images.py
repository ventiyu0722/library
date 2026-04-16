#!/usr/bin/env python3
"""Image search via Serper API — find avatar-suitable reference images online.

Usage:
    python3 search_images.py "<query>" [--count 5] [--download-dir <dir>]

Outputs structured JSON with downloaded candidate images.
"""

import argparse
import hashlib
import io
import json
import os
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor

import requests
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATHS = [
    os.path.join(SCRIPT_DIR, "config.json"),
    os.path.expanduser("~/.claude/skills/daily-avatar/config.json"),
]

DEFAULT_DOWNLOAD_DIR = os.path.join(SCRIPT_DIR, "search_cache")


def _load_config() -> dict:
    for path in CONFIG_PATHS:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    return json.load(f)
            except Exception:
                continue
    return {}


def _get_serper_key(cfg: dict) -> str:
    key = os.environ.get("SERPER_API_KEY", "")
    if key:
        return key
    return cfg.get("search_api", {}).get("api_key", "")


def _search_images_serper(query: str, api_key: str, num: int = 20) -> list[dict]:
    """Search images via Serper API."""
    resp = requests.post(
        "https://google.serper.dev/images",
        headers={
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
        },
        json={"q": query, "num": num},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    results = []
    for img in data.get("images", []):
        results.append({
            "title": img.get("title", ""),
            "url": img.get("imageUrl", ""),
            "thumbnail_url": img.get("thumbnailUrl", ""),
            "source": img.get("source", ""),
            "width": img.get("imageWidth", 0),
            "height": img.get("imageHeight", 0),
        })
    return results


def _download_image(url: str, save_path: str, timeout: int = 10) -> bool:
    """Download image and validate it's a valid image file."""
    try:
        resp = requests.get(url, timeout=timeout, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content))
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        img.save(save_path, format="JPEG", quality=90)
        return True
    except Exception:
        return False


def _compute_color_histogram(img_path: str, bins: int = 16) -> list[float]:
    """Compute normalized color histogram for diversity comparison."""
    try:
        img = Image.open(img_path).convert("RGB").resize((64, 64))
        hist = img.histogram()
        r = hist[0:256:256 // bins]
        g = hist[256:512:256 // bins]
        b = hist[512:768:256 // bins]
        combined = r + g + b
        total = sum(combined) or 1
        return [x / total for x in combined]
    except Exception:
        return []


def _histogram_similarity(h1: list[float], h2: list[float]) -> float:
    """Compute histogram intersection similarity (0=different, 1=identical)."""
    if not h1 or not h2 or len(h1) != len(h2):
        return 0.0
    return sum(min(a, b) for a, b in zip(h1, h2))


def _avatar_suitability_score(width: int, height: int) -> float:
    """Score how suitable an image is for avatar use (prefers square, min 256px)."""
    if width <= 0 or height <= 0:
        return 0.5
    aspect = min(width, height) / max(width, height)
    size_score = min(1.0, min(width, height) / 512)
    return aspect * 0.6 + size_score * 0.4


def search_and_select(
    query: str,
    target_count: int = 5,
    download_dir: str = DEFAULT_DOWNLOAD_DIR,
    similarity_threshold: float = 0.70,
) -> dict:
    """Search images, download candidates, filter for diversity, return structured result."""
    cfg = _load_config()
    api_key = _get_serper_key(cfg)
    if not api_key:
        return {
            "success": False,
            "error": "Serper API key not found. Set SERPER_API_KEY env var or configure config.json search_api.api_key.",
            "error_code": "API_KEY_MISSING",
        }

    try:
        raw_results = _search_images_serper(query, api_key, num=min(target_count * 4, 20))
    except Exception as e:
        return {
            "success": False,
            "error": f"Image search failed: {e}",
            "error_code": "SEARCH_FAILED",
        }

    if not raw_results:
        return {
            "success": False,
            "error": f"No images found for query: {query}",
            "error_code": "NO_RESULTS",
        }

    raw_results.sort(
        key=lambda x: _avatar_suitability_score(x.get("width", 0), x.get("height", 0)),
        reverse=True,
    )

    os.makedirs(download_dir, exist_ok=True)

    downloaded = []
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = []
        for i, item in enumerate(raw_results[:target_count * 3]):
            url = item.get("url", "")
            if not url:
                continue
            ext = ".jpg"
            filename = f"search_{uuid.uuid4().hex[:8]}{ext}"
            save_path = os.path.join(download_dir, filename)
            futures.append((i, item, save_path, pool.submit(_download_image, url, save_path)))

        for i, item, save_path, future in futures:
            try:
                if future.result(timeout=12):
                    downloaded.append({
                        "local_path": os.path.abspath(save_path),
                        "source_url": item["url"],
                        "title": item["title"],
                        "width": item.get("width", 0),
                        "height": item.get("height", 0),
                    })
            except Exception:
                continue

    if not downloaded:
        return {
            "success": False,
            "error": "Failed to download any candidate images",
            "error_code": "DOWNLOAD_FAILED",
        }

    selected = [downloaded[0]]
    selected_hists = [_compute_color_histogram(downloaded[0]["local_path"])]

    for candidate in downloaded[1:]:
        if len(selected) >= target_count:
            break
        hist = _compute_color_histogram(candidate["local_path"])
        too_similar = False
        for sh in selected_hists:
            if _histogram_similarity(hist, sh) > similarity_threshold:
                too_similar = True
                break
        if not too_similar:
            selected.append(candidate)
            selected_hists.append(hist)

    if len(selected) < target_count:
        for candidate in downloaded:
            if len(selected) >= target_count:
                break
            if candidate not in selected:
                selected.append(candidate)

    for i, item in enumerate(selected):
        item["index"] = i + 1

    for d in downloaded:
        if d not in selected:
            try:
                os.remove(d["local_path"])
            except Exception:
                pass

    return {
        "success": True,
        "query": query,
        "candidates": selected,
        "total_found": len(raw_results),
        "downloaded": len(downloaded),
        "filtered_count": len(selected),
    }


def main():
    parser = argparse.ArgumentParser(description="Avatar Image Search")
    parser.add_argument("query", help="Search query for avatar images")
    parser.add_argument("--count", type=int, default=5, help="Number of candidates (3-5)")
    parser.add_argument("--download-dir", default=DEFAULT_DOWNLOAD_DIR, help="Download directory")
    args = parser.parse_args()

    count = max(3, min(args.count, 5))
    result = search_and_select(
        query=args.query,
        target_count=count,
        download_dir=args.download_dir,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Fetch blog hero images from Pexels API.

Usage:
    # Fetch images for all articles (uses built-in search queries)
    PEXELS_API_KEY=xxx python3 scripts/fetch-blog-images.py

    # Fetch image for a specific article with custom query
    PEXELS_API_KEY=xxx python3 scripts/fetch-blog-images.py --slug my-article --query "church bible"

Images are saved to scss/image/blog/photos/{slug}.jpg
"""

import os
import sys
import json
import ssl
import urllib.request
import urllib.parse
import argparse

# Fix macOS Python SSL certificate issue
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

API_KEY = os.environ.get("PEXELS_API_KEY", "")
PHOTOS_DIR = os.path.join(os.path.dirname(__file__), "..", "scss", "image", "blog", "photos")

# Default search queries for existing articles
DEFAULT_QUERIES = {
    "how-to-take-sermon-notes": "person writing notes church sermon",
    "how-to-remember-sermons": "person reading bible peaceful",
    "digital-vs-paper-sermon-notes": "notebook and phone on desk",
    "best-sermon-notes-apps": "smartphone note taking app",
}

def fetch_photo(query, per_page=5):
    """Search Pexels and return the first landscape-oriented photo URL."""
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({
        "query": query,
        "per_page": per_page,
        "orientation": "landscape",
    })
    req = urllib.request.Request(url, headers={"Authorization": API_KEY})
    with urllib.request.urlopen(req, context=ssl_ctx) as resp:
        data = json.loads(resp.read())

    if not data.get("photos"):
        print(f"  No photos found for query: {query}")
        return None, None

    photo = data["photos"][0]
    # Use 'large' size — good balance of quality and file size (~1200px wide)
    image_url = photo["src"]["large"]
    photographer = photo["photographer"]
    photo_url = photo["url"]
    return image_url, f"Photo by {photographer} on Pexels"


def download_image(image_url, slug):
    """Download image and save as {slug}.jpg."""
    os.makedirs(PHOTOS_DIR, exist_ok=True)
    dest = os.path.join(PHOTOS_DIR, f"{slug}.jpg")

    req = urllib.request.Request(image_url)
    with urllib.request.urlopen(req, context=ssl_ctx) as resp:
        with open(dest, "wb") as f:
            f.write(resp.read())

    size_kb = os.path.getsize(dest) / 1024
    print(f"  Saved: {dest} ({size_kb:.0f} KB)")
    return dest


def main():
    parser = argparse.ArgumentParser(description="Fetch blog images from Pexels")
    parser.add_argument("--slug", help="Article slug (e.g. my-article)")
    parser.add_argument("--query", help="Search query for Pexels")
    args = parser.parse_args()

    if not API_KEY:
        print("Error: Set PEXELS_API_KEY environment variable")
        sys.exit(1)

    if args.slug:
        # Single article mode
        query = args.query or args.slug.replace("-", " ")
        articles = {args.slug: query}
    else:
        # All articles mode
        articles = DEFAULT_QUERIES

    for slug, query in articles.items():
        dest = os.path.join(PHOTOS_DIR, f"{slug}.jpg")
        if os.path.exists(dest) and not args.slug:
            print(f"[skip] {slug} — already exists")
            continue

        print(f"[fetch] {slug} — query: \"{query}\"")
        image_url, attribution = fetch_photo(query)
        if image_url:
            download_image(image_url, slug)
            print(f"  {attribution}")


if __name__ == "__main__":
    main()

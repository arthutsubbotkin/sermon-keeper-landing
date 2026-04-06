#!/usr/bin/env bash
# Fetch blog hero images from Pexels API
# Usage: PEXELS_API_KEY=xxx ./scripts/fetch-blog-images.sh [slug] [query]

set -e

API_KEY="${PEXELS_API_KEY}"
PHOTOS_DIR="$(dirname "$0")/../scss/image/blog/photos"
mkdir -p "$PHOTOS_DIR"

if [ -z "$API_KEY" ]; then
    echo "Error: Set PEXELS_API_KEY environment variable"
    exit 1
fi

fetch_image() {
    local slug="$1"
    local query="$2"
    local dest="$PHOTOS_DIR/${slug}.jpg"

    if [ -f "$dest" ] && [ -z "$FORCE" ]; then
        echo "[skip] $slug — already exists"
        return
    fi

    echo "[fetch] $slug — query: \"$query\""

    # Search Pexels
    local response
    response=$(curl -s -H "Authorization: $API_KEY" \
        "https://api.pexels.com/v1/search?query=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$query'))")&per_page=5&orientation=landscape")

    local image_url
    image_url=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['photos'][0]['src']['large'] if d.get('photos') else '')" 2>/dev/null)

    local photographer
    photographer=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['photos'][0]['photographer'] if d.get('photos') else '')" 2>/dev/null)

    if [ -z "$image_url" ]; then
        echo "  No photos found!"
        return 1
    fi

    # Download
    curl -sL -o "$dest" "$image_url"
    local size
    size=$(du -k "$dest" | cut -f1)
    echo "  Saved: $dest (${size} KB)"
    echo "  Photo by $photographer on Pexels"
}

if [ -n "$1" ]; then
    # Single article mode
    slug="$1"
    query="${2:-${slug//-/ }}"
    FORCE=1 fetch_image "$slug" "$query"
else
    # All articles
    fetch_image "how-to-take-sermon-notes" "person writing notes bible study"
    fetch_image "how-to-remember-sermons" "woman reading bible morning light"
    fetch_image "digital-vs-paper-sermon-notes" "notebook phone desk study"
    fetch_image "best-sermon-notes-apps" "smartphone notes app productivity"
fi

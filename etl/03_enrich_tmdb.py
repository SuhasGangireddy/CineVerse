"""
Step 3 (Optional): Enrich movie data with TMDb API.

Adds: poster_url, plot/overview, budget, revenue, language, country.

Requires a free TMDb API key. Get one at:
  https://developer.themoviedb.org/

Set your API key as an environment variable:
  export TMDB_API_KEY="your_key_here"

Or pass it as a command-line argument:
  python 03_enrich_tmdb.py --api-key YOUR_KEY
"""

import os
import sys
import time
import argparse
import pandas as pd
import requests
from pathlib import Path

CLEAN_DIR = Path(__file__).resolve().parent.parent / "data_clean"
TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
RATE_LIMIT_DELAY = 0.26  # TMDb allows ~40 requests per 10 seconds


def get_api_key():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", type=str, default=None)
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("TMDB_API_KEY")
    if not api_key:
        print("ERROR: No TMDb API key provided.")
        print("Set TMDB_API_KEY env var or pass --api-key YOUR_KEY")
        print("\nSkipping TMDb enrichment. Movies will load without posters/budget/revenue.")
        sys.exit(0)
    return api_key


def fetch_tmdb_movie(tmdb_id, api_key):
    """Fetch movie details from TMDb API."""
    url = f"{TMDB_BASE}/movie/{int(tmdb_id)}"
    params = {"api_key": api_key, "language": "en-US"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 429:
            # Rate limited — wait and retry
            time.sleep(2)
            return fetch_tmdb_movie(tmdb_id, api_key)
        else:
            return None
    except Exception:
        return None


def enrich_movies(api_key):
    movies_path = CLEAN_DIR / "movies.csv"
    if not movies_path.exists():
        print("ERROR: movies.csv not found. Run 02_process_data.py first.")
        sys.exit(1)

    movies = pd.read_csv(movies_path)
    total = len(movies)
    enriched = 0
    skipped = 0

    print(f"Enriching {total} movies from TMDb API ...")

    for idx, row in movies.iterrows():
        tmdb_id = row.get("tmdb_id")
        if pd.isna(tmdb_id):
            skipped += 1
            continue

        data = fetch_tmdb_movie(tmdb_id, api_key)
        if data:
            movies.at[idx, "plot"] = (data.get("overview") or "")[:1000]
            movies.at[idx, "budget"] = data.get("budget") or None
            movies.at[idx, "revenue"] = data.get("revenue") or None

            poster = data.get("poster_path")
            if poster:
                movies.at[idx, "poster_url"] = TMDB_IMAGE_BASE + poster

            # Language
            orig_lang = data.get("original_language", "en")
            lang_map = {"en": "English", "ja": "Japanese", "ko": "Korean",
                        "fr": "French", "es": "Spanish", "de": "German",
                        "it": "Italian", "zh": "Chinese", "hi": "Hindi"}
            movies.at[idx, "language"] = lang_map.get(orig_lang, orig_lang)

            # Country (first production country)
            countries = data.get("production_countries", [])
            if countries:
                movies.at[idx, "country"] = countries[0].get("name", "")

            # Release date (more accurate)
            release = data.get("release_date")
            if release:
                movies.at[idx, "release_date_full"] = release

            enriched += 1
        else:
            skipped += 1

        if (idx + 1) % 50 == 0:
            print(f"  Progress: {idx + 1}/{total} (enriched: {enriched}, skipped: {skipped})")

        time.sleep(RATE_LIMIT_DELAY)

    movies.to_csv(movies_path, index=False)
    print(f"\nDone! Enriched {enriched} movies, skipped {skipped}.")
    print(f"Updated: {movies_path}")

    # Also create external ratings for Rotten Tomatoes (if available via OMDb, skip for now)
    # The IMDb external ratings are already created in step 2


if __name__ == "__main__":
    print("=" * 60)
    print("CineVerse ETL - Step 3: TMDb Enrichment")
    print("=" * 60)
    api_key = get_api_key()
    enrich_movies(api_key)

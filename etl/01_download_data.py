"""
Step 1: Download raw datasets from IMDb and MovieLens.

IMDb Non-Commercial Datasets (TSV, gzipped):
  - title.basics.tsv.gz   (movies, genres, runtime, year)
  - title.ratings.tsv.gz  (IMDb average rating, vote count)
  - name.basics.tsv.gz    (people: actors, directors, etc.)
  - title.principals.tsv.gz (cast/crew credits per movie)

MovieLens Latest Small:
  - ratings.csv   (user ratings)
  - tags.csv      (user tags)
  - links.csv     (movieId -> imdbId, tmdbId bridge)
  - movies.csv    (movieId, title, genres)

MovieLens Tag Genome (2021):
  - tag_genome_tags.csv
  - tag_genome_scores.csv  (movie x tag relevance scores)
"""

import os
import urllib.request
import gzip
import shutil
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data_raw"
RAW_DIR.mkdir(exist_ok=True)

IMDB_BASE = "https://datasets.imdbws.com/"
IMDB_FILES = [
    "title.basics.tsv.gz",
    "title.ratings.tsv.gz",
    "name.basics.tsv.gz",
    "title.principals.tsv.gz",
]

MOVIELENS_SMALL_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
MOVIELENS_TAG_GENOME_URL = "https://files.grouplens.org/datasets/tag-genome-2021/genome_2021.zip"


def download_file(url, dest_path):
    """Download a file with progress indication."""
    if dest_path.exists():
        print(f"  [skip] {dest_path.name} already exists")
        return
    print(f"  Downloading {url} ...")
    urllib.request.urlretrieve(url, str(dest_path))
    print(f"  -> Saved to {dest_path.name}")


def decompress_gz(gz_path):
    """Decompress a .gz file."""
    out_path = gz_path.with_suffix("")  # remove .gz
    if out_path.exists():
        print(f"  [skip] {out_path.name} already decompressed")
        return
    print(f"  Decompressing {gz_path.name} ...")
    with gzip.open(str(gz_path), "rb") as f_in:
        with open(str(out_path), "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    print(f"  -> {out_path.name}")


def download_imdb():
    print("\n=== Downloading IMDb Datasets ===")
    for fname in IMDB_FILES:
        dest = RAW_DIR / fname
        download_file(IMDB_BASE + fname, dest)
        decompress_gz(dest)


def download_movielens():
    import zipfile

    print("\n=== Downloading MovieLens Latest Small ===")
    zip_path = RAW_DIR / "ml-latest-small.zip"
    download_file(MOVIELENS_SMALL_URL, zip_path)

    ml_dir = RAW_DIR / "ml-latest-small"
    if not ml_dir.exists():
        print("  Extracting ml-latest-small.zip ...")
        with zipfile.ZipFile(str(zip_path), "r") as z:
            z.extractall(str(RAW_DIR))
        print("  -> Extracted")
    else:
        print("  [skip] ml-latest-small already extracted")


def download_tag_genome():
    import zipfile

    print("\n=== Downloading MovieLens Tag Genome 2021 ===")
    zip_path = RAW_DIR / "genome_2021.zip"
    download_file(MOVIELENS_TAG_GENOME_URL, zip_path)

    genome_dir = RAW_DIR / "genome_2021"
    if not genome_dir.exists():
        print("  Extracting genome_2021.zip ...")
        with zipfile.ZipFile(str(zip_path), "r") as z:
            z.extractall(str(RAW_DIR))
        print("  -> Extracted")
    else:
        print("  [skip] genome_2021 already extracted")


if __name__ == "__main__":
    print("CineVerse ETL - Step 1: Download Raw Datasets")
    download_imdb()
    download_movielens()
    download_tag_genome()
    print("\n=== All downloads complete! ===")
    print(f"Raw data directory: {RAW_DIR}")

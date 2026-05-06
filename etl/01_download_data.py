# Download raw datasets from IMDb and MovieLens

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
    if dest_path.exists():
        print(f"  [skip] {dest_path.name} already exists")
        return
    print(f"  Downloading {url}")
    urllib.request.urlretrieve(url, str(dest_path))
    print(f"  Saved {dest_path.name}")


def decompress_gz(gz_path):
    out_path = gz_path.with_suffix("")
    if out_path.exists():
        print(f"  [skip] {out_path.name} already decompressed")
        return
    print(f"  Decompressing {gz_path.name}")
    with gzip.open(str(gz_path), "rb") as f_in:
        with open(str(out_path), "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


def download_imdb():
    print("\nDownloading IMDb datasets")
    for fname in IMDB_FILES:
        dest = RAW_DIR / fname
        download_file(IMDB_BASE + fname, dest)
        decompress_gz(dest)


def download_movielens():
    import zipfile

    print("\nDownloading MovieLens Latest Small")
    zip_path = RAW_DIR / "ml-latest-small.zip"
    download_file(MOVIELENS_SMALL_URL, zip_path)

    ml_dir = RAW_DIR / "ml-latest-small"
    if not ml_dir.exists():
        print("  Extracting ml-latest-small.zip")
        with zipfile.ZipFile(str(zip_path), "r") as z:
            z.extractall(str(RAW_DIR))
    else:
        print("  [skip] ml-latest-small already extracted")


def download_tag_genome():
    import zipfile

    print("\nDownloading MovieLens Tag Genome 2021")
    zip_path = RAW_DIR / "genome_2021.zip"
    download_file(MOVIELENS_TAG_GENOME_URL, zip_path)

    genome_dir = RAW_DIR / "genome_2021"
    if not genome_dir.exists():
        print("  Extracting genome_2021.zip")
        with zipfile.ZipFile(str(zip_path), "r") as z:
            z.extractall(str(RAW_DIR))
    else:
        print("  [skip] genome_2021 already extracted")


if __name__ == "__main__":
    print("Downloading raw datasets")
    download_imdb()
    download_movielens()
    download_tag_genome()
    print(f"\nAll downloads complete. Raw data in {RAW_DIR}")

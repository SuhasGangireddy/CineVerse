# Process and merge IMDb + MovieLens datasets into clean CSVs

import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data_raw"
CLEAN_DIR = Path(__file__).resolve().parent.parent / "data_clean"
CLEAN_DIR.mkdir(exist_ok=True)

MAX_MOVIES = 500
MIN_YEAR = 1970
MIN_IMDB_VOTES = 10000
MAX_USERS = 200
MAX_RATINGS = 20000
TAG_RELEVANCE_THRESHOLD = 0.5
MAX_TAGS_PER_MOVIE = 10


def load_imdb_basics():
    print("Loading IMDb title.basics")
    df = pd.read_csv(
        RAW_DIR / "title.basics.tsv", sep="\t", na_values="\\N",
        dtype={"tconst": str, "titleType": str, "primaryTitle": str,
               "startYear": str, "runtimeMinutes": str, "genres": str}
    )
    df = df[df["titleType"] == "movie"].copy()
    df["startYear"] = pd.to_numeric(df["startYear"], errors="coerce")
    df["runtimeMinutes"] = pd.to_numeric(df["runtimeMinutes"], errors="coerce")
    df = df[df["startYear"] >= MIN_YEAR].dropna(subset=["startYear"])
    print(f"  {len(df)} movies from {MIN_YEAR}+")
    return df


def load_imdb_ratings():
    print("Loading IMDb title.ratings")
    df = pd.read_csv(
        RAW_DIR / "title.ratings.tsv", sep="\t", na_values="\\N",
        dtype={"tconst": str}
    )
    return df


def load_movielens_links():
    print("Loading MovieLens links")
    df = pd.read_csv(RAW_DIR / "ml-latest-small" / "links.csv",
                      dtype={"movieId": int, "imdbId": str, "tmdbId": str})
    # Pad imdbId to match IMDb format: tt0000001
    df["imdb_id"] = "tt" + df["imdbId"].str.zfill(7)
    df["tmdb_id"] = pd.to_numeric(df["tmdbId"], errors="coerce")
    return df


def select_movies(imdb_basics, imdb_ratings, ml_links):
    print(f"\nSelecting top {MAX_MOVIES} movies")

    movies = imdb_basics.merge(imdb_ratings, on="tconst", how="inner")
    movies = movies[movies["numVotes"] >= MIN_IMDB_VOTES]
    print(f"  {len(movies)} with >= {MIN_IMDB_VOTES} votes")

    movies = movies.merge(ml_links[["imdb_id", "movieId", "tmdb_id"]],
                          left_on="tconst", right_on="imdb_id", how="inner")
    print(f"  {len(movies)} also in MovieLens")

    movies = movies.sort_values("numVotes", ascending=False).head(MAX_MOVIES)
    movies = movies.reset_index(drop=True)
    movies["movie_id"] = movies.index + 1
    print(f"  Selected {len(movies)} movies")

    return movies


def process_movies(movies):
    print("\nProcessing movies")
    out = pd.DataFrame({
        "movie_id": movies["movie_id"],
        "imdb_id": movies["tconst"],
        "tmdb_id": movies["tmdb_id"],
        "title": movies["primaryTitle"],
        "release_year": movies["startYear"].astype(int),
        "runtime_minutes": movies["runtimeMinutes"],
        "language": "English",   # default, TMDb enrichment can fix this
        "country": None,
        "plot": None,            # TMDb enrichment
        "budget": None,
        "revenue": None,
        "imdb_rating": movies["averageRating"],
        "imdb_votes": movies["numVotes"],
        "genres_raw": movies["genres"],
    })
    out.to_csv(CLEAN_DIR / "movies.csv", index=False)
    print(f"  Wrote {len(out)} movies")
    return out


def process_genres(movies_df):
    print("\nProcessing genres")
    genre_rows = []
    for _, row in movies_df.iterrows():
        if pd.isna(row["genres_raw"]):
            continue
        for g in row["genres_raw"].split(","):
            genre_rows.append({"movie_id": row["movie_id"], "genre_name": g.strip()})

    genre_df = pd.DataFrame(genre_rows)
    unique_genres = sorted(genre_df["genre_name"].unique())
    genre_lookup = pd.DataFrame({
        "genre_id": range(1, len(unique_genres) + 1),
        "genre_name": unique_genres
    })
    genre_lookup.to_csv(CLEAN_DIR / "genres.csv", index=False)
    print(f"  {len(genre_lookup)} genres")

    mg = genre_df.merge(genre_lookup, on="genre_name")[["movie_id", "genre_id"]]
    mg.to_csv(CLEAN_DIR / "movie_genres.csv", index=False)
    print(f"  {len(mg)} movie-genre links")
    return genre_lookup


def process_people_and_credits(movies):
    print("\nProcessing people and credits")

    movie_ids_map = dict(zip(movies["tconst"], movies["movie_id"]))
    movie_tconsts = set(movies["tconst"])

    print("  Loading title.principals (this may take a moment)")
    principals = pd.read_csv(
        RAW_DIR / "title.principals.tsv", sep="\t", na_values="\\N",
        dtype={"tconst": str, "nconst": str, "category": str, "characters": str}
    )
    principals = principals[principals["tconst"].isin(movie_tconsts)].copy()
    print(f"  {len(principals)} credits for selected movies")

    role_map = {
        "actor": "Actor", "actress": "Actor",
        "director": "Director", "producer": "Producer",
        "writer": "Writer", "self": "Actor",
        "composer": "Writer", "cinematographer": "Writer",
        "editor": "Writer",
    }
    principals["role_name"] = principals["category"].map(role_map)
    principals = principals.dropna(subset=["role_name"])

    person_nconsts = principals["nconst"].unique()
    print(f"  {len(person_nconsts)} unique people")

    print("  Loading name.basics")
    names = pd.read_csv(
        RAW_DIR / "name.basics.tsv", sep="\t", na_values="\\N",
        dtype={"nconst": str, "primaryName": str, "birthYear": str,
               "deathYear": str, "primaryProfession": str}
    )
    names = names[names["nconst"].isin(person_nconsts)].copy()
    names["birthYear"] = pd.to_numeric(names["birthYear"], errors="coerce")
    names["deathYear"] = pd.to_numeric(names["deathYear"], errors="coerce")

    names = names.reset_index(drop=True)
    names["person_id"] = names.index + 1
    person_id_map = dict(zip(names["nconst"], names["person_id"]))

    people_out = pd.DataFrame({
        "person_id": names["person_id"],
        "imdb_person_id": names["nconst"],
        "name": names["primaryName"],
        "birth_year": names["birthYear"],
        "death_year": names["deathYear"],
        "primary_profession": names["primaryProfession"].str.split(",").str[0],
    })
    people_out.to_csv(CLEAN_DIR / "people.csv", index=False)
    print(f"  Wrote {len(people_out)} people")

    role_types = pd.DataFrame({
        "role_type_id": [1, 2, 3, 4],
        "role_name": ["Actor", "Director", "Producer", "Writer"]
    })
    role_types.to_csv(CLEAN_DIR / "role_types.csv", index=False)
    role_id_map = dict(zip(role_types["role_name"], role_types["role_type_id"]))

    def parse_character(chars_str):
        if pd.isna(chars_str):
            return None
        try:
            import json
            chars = json.loads(chars_str)
            return chars[0] if chars else None
        except Exception:
            return chars_str[:255] if isinstance(chars_str, str) else None

    credits_rows = []
    credit_id = 1
    for _, row in principals.iterrows():
        movie_id = movie_ids_map.get(row["tconst"])
        person_id = person_id_map.get(row["nconst"])
        role_type_id = role_id_map.get(row["role_name"])
        if movie_id and person_id and role_type_id:
            credits_rows.append({
                "credit_id": credit_id,
                "movie_id": movie_id,
                "person_id": person_id,
                "role_type_id": role_type_id,
                "character_name": parse_character(row.get("characters")),
                "billing_order": row.get("ordering"),
            })
            credit_id += 1

    credits_df = pd.DataFrame(credits_rows)
    credits_df = credits_df.drop_duplicates(
        subset=["movie_id", "person_id", "role_type_id", "character_name"]
    )
    credits_df["credit_id"] = range(1, len(credits_df) + 1)
    credits_df.to_csv(CLEAN_DIR / "movie_credits.csv", index=False)
    print(f"  Wrote {len(credits_df)} credits")

    return people_out, credits_df


def process_user_ratings(movies):
    print("\nProcessing user ratings")
    ml_ratings = pd.read_csv(RAW_DIR / "ml-latest-small" / "ratings.csv")
    ml_links = pd.read_csv(RAW_DIR / "ml-latest-small" / "links.csv",
                            dtype={"imdbId": str})
    ml_links["imdb_id"] = "tt" + ml_links["imdbId"].str.zfill(7)

    movie_id_map = dict(zip(movies["tconst"], movies["movie_id"]))
    ml_links["movie_id"] = ml_links["imdb_id"].map(movie_id_map)
    ml_links = ml_links.dropna(subset=["movie_id"])
    ml_links["movie_id"] = ml_links["movie_id"].astype(int)

    ml_movie_map = dict(zip(ml_links["movieId"], ml_links["movie_id"]))

    ratings = ml_ratings.copy()
    ratings["movie_id"] = ratings["movieId"].map(ml_movie_map)
    ratings = ratings.dropna(subset=["movie_id"])
    ratings["movie_id"] = ratings["movie_id"].astype(int)

    user_ids = sorted(ratings["userId"].unique())[:MAX_USERS]
    ratings = ratings[ratings["userId"].isin(user_ids)]
    ratings = ratings.head(MAX_RATINGS)

    # Remap user IDs to 1..N
    unique_users = sorted(ratings["userId"].unique())
    user_id_remap = {old: new for new, old in enumerate(unique_users, 1)}
    ratings["user_id"] = ratings["userId"].map(user_id_remap)

    # Scale ratings from 0.5-5.0 to 1.0-10.0
    ratings["rating_scaled"] = ratings["rating"] * 2.0

    ratings["rating_date"] = pd.to_datetime(ratings["timestamp"], unit="s").dt.date

    users_df = pd.DataFrame({
        "user_id": range(1, len(unique_users) + 1),
        "username": [f"user_{uid}" for uid in unique_users],
        "email": [f"user{uid}@cineverse.example.com" for uid in unique_users],
        "age_group": np.random.choice(
            ["under_18", "18-24", "25-34", "35-44", "45-54", "55+"],
            size=len(unique_users),
            p=[0.05, 0.25, 0.30, 0.20, 0.12, 0.08]
        ),
        "preferred_language": "English",
    })
    users_df.to_csv(CLEAN_DIR / "users.csv", index=False)
    print(f"  Wrote {len(users_df)} users")

    ratings_out = ratings[["user_id", "movie_id", "rating_scaled", "rating_date"]].copy()
    ratings_out.columns = ["user_id", "movie_id", "rating", "rating_date"]
    ratings_out = ratings_out.drop_duplicates(subset=["user_id", "movie_id"])
    ratings_out.to_csv(CLEAN_DIR / "user_ratings.csv", index=False)
    print(f"  Wrote {len(ratings_out)} ratings")

    return users_df, ratings_out


def process_tags_and_relevance(movies):
    print("\nProcessing tags and relevance scores")

    movie_id_map = dict(zip(movies["tconst"], movies["movie_id"]))

    ml_links = pd.read_csv(RAW_DIR / "ml-latest-small" / "links.csv",
                            dtype={"imdbId": str})
    ml_links["imdb_id"] = "tt" + ml_links["imdbId"].str.zfill(7)
    ml_links["movie_id"] = ml_links["imdb_id"].map(movie_id_map)

    # Try to find tag genome files
    tag_file = None
    score_file = None

    for candidate_dir in [RAW_DIR / "genome_2021", RAW_DIR]:
        if not candidate_dir.exists():
            continue
        for f in candidate_dir.rglob("*"):
            fname = f.name.lower()
            if "tag" in fname and fname.endswith(".csv") and "score" not in fname:
                tag_file = f
            elif "score" in fname and fname.endswith(".csv"):
                score_file = f

    if tag_file and score_file:
        print(f"  Found {tag_file.name}, {score_file.name}")

        tags_raw = pd.read_csv(tag_file)
        print(f"  {len(tags_raw)} tags in genome")

        scores_chunks = []
        ml_movie_ids = set(ml_links.dropna(subset=["movie_id"])["movieId"].astype(int))

        for chunk in pd.read_csv(score_file, chunksize=500000):
            chunk_filtered = chunk[chunk["movieId"].isin(ml_movie_ids)]
            if len(chunk_filtered) > 0:
                scores_chunks.append(chunk_filtered)

        if scores_chunks:
            scores = pd.concat(scores_chunks, ignore_index=True)
            print(f"  {len(scores)} relevance scores for our movies")

            ml_to_movie = dict(zip(
                ml_links.dropna(subset=["movie_id"])["movieId"].astype(int),
                ml_links.dropna(subset=["movie_id"])["movie_id"].astype(int)
            ))
            scores["movie_id"] = scores["movieId"].map(ml_to_movie)
            scores = scores.dropna(subset=["movie_id"])
            scores["movie_id"] = scores["movie_id"].astype(int)

            scores = scores[scores["relevance"] >= TAG_RELEVANCE_THRESHOLD]

            scores = scores.sort_values("relevance", ascending=False)
            scores = scores.groupby("movie_id").head(MAX_TAGS_PER_MOVIE)

            used_tag_ids = scores["tagId"].unique()
            tags_used = tags_raw[tags_raw["tagId"].isin(used_tag_ids)].copy()
            tags_used = tags_used.reset_index(drop=True)
            tags_used["tag_id"] = tags_used.index + 1
            tag_id_remap = dict(zip(tags_used["tagId"], tags_used["tag_id"]))

            tags_used_out = tags_used[["tag_id", "tag"]].copy()
            tags_used_out.columns = ["tag_id", "tag_name"]
            tags_used_out.to_csv(CLEAN_DIR / "tags.csv", index=False)
            print(f"  Wrote {len(tags_used_out)} tags")

            scores["tag_id"] = scores["tagId"].map(tag_id_remap)
            scores = scores.dropna(subset=["tag_id"])
            scores["tag_id"] = scores["tag_id"].astype(int)
            rel_out = scores[["movie_id", "tag_id", "relevance"]].copy()
            rel_out.columns = ["movie_id", "tag_id", "relevance_score"]
            rel_out["relevance_score"] = rel_out["relevance_score"].round(3)
            rel_out = rel_out.drop_duplicates(subset=["movie_id", "tag_id"])
            rel_out.to_csv(CLEAN_DIR / "movie_tag_relevance.csv", index=False)
            print(f"  Wrote {len(rel_out)} relevance scores")
            return tags_used_out, rel_out

    # Fallback: use MovieLens user tags
    print("  Tag genome not found, falling back to MovieLens user tags")
    ml_tags = pd.read_csv(RAW_DIR / "ml-latest-small" / "tags.csv",
                           dtype={"userId": int, "movieId": int, "tag": str})

    ml_to_movie = dict(zip(
        ml_links.dropna(subset=["movie_id"])["movieId"].astype(int),
        ml_links.dropna(subset=["movie_id"])["movie_id"].astype(int)
    ))
    ml_tags["movie_id"] = ml_tags["movieId"].map(ml_to_movie)
    ml_tags = ml_tags.dropna(subset=["movie_id"])

    tag_counts = ml_tags.groupby("tag").size().reset_index(name="count")
    tag_counts = tag_counts[tag_counts["count"] >= 2].sort_values("count", ascending=False).head(200)
    tag_counts["tag_id"] = range(1, len(tag_counts) + 1)

    tags_out = tag_counts[["tag_id", "tag"]].copy()
    tags_out.columns = ["tag_id", "tag_name"]
    tags_out.to_csv(CLEAN_DIR / "tags.csv", index=False)
    print(f"  Wrote {len(tags_out)} tags")

    tag_name_to_id = dict(zip(tags_out["tag_name"], tags_out["tag_id"]))
    ml_tags["tag_id"] = ml_tags["tag"].map(tag_name_to_id)
    ml_tags = ml_tags.dropna(subset=["tag_id"])
    ml_tags["movie_id"] = ml_tags["movie_id"].astype(int)
    ml_tags["tag_id"] = ml_tags["tag_id"].astype(int)

    rel = ml_tags.groupby(["movie_id", "tag_id"]).size().reset_index(name="count")
    rel["relevance_score"] = (rel["count"] / rel["count"].max()).round(3).clip(0.1, 1.0)
    rel_out = rel[["movie_id", "tag_id", "relevance_score"]].drop_duplicates()
    rel_out.to_csv(CLEAN_DIR / "movie_tag_relevance.csv", index=False)
    print(f"  Wrote {len(rel_out)} relevance scores")

    return tags_out, rel_out


def process_external_ratings(movies):
    print("\nProcessing external ratings")
    rows = []
    for _, m in movies.iterrows():
        if pd.notna(m.get("imdb_rating")):
            rows.append({
                "movie_id": m["movie_id"],
                "source_name": "IMDb",
                "score": m["imdb_rating"],
                "max_score": 10.0,
                "vote_count": int(m["imdb_votes"]) if pd.notna(m.get("imdb_votes")) else None,
            })
    ext_df = pd.DataFrame(rows)
    ext_df.to_csv(CLEAN_DIR / "external_ratings.csv", index=False)
    print(f"  Wrote {len(ext_df)} external ratings")
    return ext_df


def generate_synthetic_support_data(movies_df, users_df):
    """Generate synthetic data for tables without a natural dataset source."""
    print("\nGenerating support data (distributors, platforms, awards, watchlists)")

    distributors = pd.DataFrame({
        "distributor_id": range(1, 21),
        "name": [
            "Warner Bros. Pictures", "Walt Disney Studios", "Universal Pictures",
            "Paramount Pictures", "Sony / Columbia Pictures", "20th Century Studios",
            "Lionsgate Films", "A24", "Miramax Films", "New Line Cinema",
            "MGM / United Artists", "Focus Features", "Toho Co., Ltd.",
            "Studio Ghibli Distribution", "CJ Entertainment", "Searchlight Pictures",
            "DreamWorks Pictures", "Netflix Distribution", "Amazon Studios", "Neon"
        ],
        "address": [
            "Burbank, CA", "Burbank, CA", "Universal City, CA", "Los Angeles, CA",
            "Culver City, CA", "Los Angeles, CA", "Santa Monica, CA", "New York, NY",
            "Los Angeles, CA", "Los Angeles, CA", "Beverly Hills, CA", "Universal City, CA",
            "Tokyo, Japan", "Tokyo, Japan", "Seoul, South Korea", "Los Angeles, CA",
            "Glendale, CA", "Los Angeles, CA", "Seattle, WA", "Los Angeles, CA"
        ],
        "country": [
            "USA","USA","USA","USA","USA","USA","USA","USA","USA","USA",
            "USA","USA","Japan","Japan","South Korea","USA","USA","USA","USA","USA"
        ]
    })
    distributors.to_csv(CLEAN_DIR / "distributors.csv", index=False)
    print(f"  {len(distributors)} distributors")

    np.random.seed(42)
    md_rows = []
    for _, m in movies_df.iterrows():
        dist_id = np.random.randint(1, 21)
        md_rows.append({"movie_id": m["movie_id"], "distributor_id": dist_id, "region": "Worldwide"})
    md_df = pd.DataFrame(md_rows)
    md_df.to_csv(CLEAN_DIR / "movie_distributors.csv", index=False)
    print(f"  {len(md_df)} movie-distributor links")

    platforms = pd.DataFrame({
        "platform_id": range(1, 11),
        "name": ["Netflix", "Amazon Prime Video", "Disney+", "Hulu", "Max (HBO)",
                 "Apple TV+", "Peacock", "Paramount+", "Crunchyroll", "Criterion Channel"],
        "country": ["USA"] * 10,
        "website_url": [
            "https://www.netflix.com", "https://www.amazon.com/primevideo",
            "https://www.disneyplus.com", "https://www.hulu.com",
            "https://www.max.com", "https://tv.apple.com",
            "https://www.peacocktv.com", "https://www.paramountplus.com",
            "https://www.crunchyroll.com", "https://www.criterionchannel.com"
        ]
    })
    platforms.to_csv(CLEAN_DIR / "streaming_platforms.csv", index=False)
    print(f"  {len(platforms)} streaming platforms")

    avail_rows = []
    access_types = ["subscription", "rent", "buy"]
    for _, m in movies_df.iterrows():
        n_platforms = np.random.randint(1, 4)
        chosen = np.random.choice(range(1, 11), size=n_platforms, replace=False)
        for pid in chosen:
            avail_rows.append({
                "movie_id": m["movie_id"],
                "platform_id": int(pid),
                "region": "US",
                "access_type": np.random.choice(access_types),
                "start_date": "2024-01-01",
                "end_date": None
            })
    avail_df = pd.DataFrame(avail_rows).drop_duplicates(
        subset=["movie_id", "platform_id", "region", "access_type"]
    )
    avail_df.to_csv(CLEAN_DIR / "movie_availability.csv", index=False)
    print(f"  {len(avail_df)} availability records")

    awards = pd.DataFrame({
        "award_id": range(1, 16),
        "award_name": [
            "Academy Awards","Academy Awards","Academy Awards","Academy Awards",
            "Academy Awards","Academy Awards","Academy Awards","Academy Awards",
            "Academy Awards","Academy Awards",
            "Golden Globe Awards","Golden Globe Awards",
            "BAFTA Awards","Cannes Film Festival","Academy Awards"
        ],
        "category": [
            "Best Picture","Best Director","Best Actor","Best Actress",
            "Best Supporting Actor","Best Supporting Actress","Best Animated Feature",
            "Best Original Screenplay","Best Adapted Screenplay","Best Cinematography",
            "Best Motion Picture - Drama","Best Director",
            "Best Film","Palme d'Or","Best International Feature Film"
        ]
    })
    awards.to_csv(CLEAN_DIR / "awards.csv", index=False)
    print(f"  {len(awards)} awards")

    award_rows = []
    ma_id = 1
    top_movies = movies_df.sort_values("imdb_rating", ascending=False).head(80)
    for _, m in top_movies.iterrows():
        n_awards = np.random.randint(1, 4)
        chosen_awards = np.random.choice(range(1, 16), size=n_awards, replace=False)
        for aid in chosen_awards:
            award_rows.append({
                "movie_award_id": ma_id,
                "movie_id": m["movie_id"],
                "award_id": int(aid),
                "person_id": None,
                "award_year": int(m["release_year"]) + 1,
                "result": np.random.choice(["won", "nominated"], p=[0.35, 0.65])
            })
            ma_id += 1
    award_df = pd.DataFrame(award_rows).drop_duplicates(
        subset=["movie_id", "award_id", "award_year"]
    )
    award_df["movie_award_id"] = range(1, len(award_df) + 1)
    award_df.to_csv(CLEAN_DIR / "movie_awards.csv", index=False)
    print(f"  {len(award_df)} movie awards")

    companies = pd.DataFrame({
        "company_id": range(1, 26),
        "name": [
            "Warner Bros. Pictures","Paramount Pictures","Universal Pictures",
            "Walt Disney Pictures","Columbia Pictures","20th Century Studios",
            "New Line Cinema","Marvel Studios","Lucasfilm","Amblin Entertainment",
            "Legendary Entertainment","Syncopy","Pixar Animation Studios",
            "Studio Ghibli","DreamWorks Pictures","Miramax Films","A Band Apart",
            "Lionsgate","Regency Enterprises","Barunson E&A",
            "Village Roadshow Pictures","Castle Rock Entertainment","GK Films",
            "Toho Co., Ltd.","CoMix Wave Films"
        ],
        "country": [
            "USA","USA","USA","USA","USA","USA","USA","USA","USA","USA",
            "USA","USA","USA","Japan","USA","USA","USA","USA","USA","South Korea",
            "Australia","USA","USA","Japan","Japan"
        ],
        "founded_year": [
            1923,1912,1912,1923,1924,1935,1967,1993,1971,1981,
            2000,2001,1986,1985,1994,1979,1991,1997,1982,2014,
            1986,1987,2007,1932,2007
        ]
    })
    companies.to_csv(CLEAN_DIR / "production_companies.csv", index=False)
    print(f"  {len(companies)} production companies")

    mpc_rows = []
    for _, m in movies_df.iterrows():
        n = np.random.randint(1, 3)
        chosen = np.random.choice(range(1, 26), size=n, replace=False)
        for cid in chosen:
            mpc_rows.append({"movie_id": m["movie_id"], "company_id": int(cid)})
    mpc_df = pd.DataFrame(mpc_rows).drop_duplicates()
    mpc_df.to_csv(CLEAN_DIR / "movie_production_companies.csv", index=False)
    print(f"  {len(mpc_df)} movie-company links")

    n_watchlists = min(50, len(users_df))
    wl_rows = []
    for i in range(1, n_watchlists + 1):
        wl_rows.append({
            "watchlist_id": i,
            "user_id": i,
            "name": "My Watchlist",
        })
    wl_df = pd.DataFrame(wl_rows)
    wl_df.to_csv(CLEAN_DIR / "watchlists.csv", index=False)
    print(f"  {len(wl_df)} watchlists")

    wi_rows = []
    movie_ids = movies_df["movie_id"].tolist()
    for wl_id in range(1, n_watchlists + 1):
        n_items = np.random.randint(2, 8)
        chosen = np.random.choice(movie_ids, size=n_items, replace=False)
        for mid in chosen:
            wi_rows.append({
                "watchlist_id": wl_id,
                "movie_id": int(mid),
                "watched_status": np.random.choice(
                    ["unwatched", "watching", "watched"], p=[0.4, 0.1, 0.5]
                ),
            })
    wi_df = pd.DataFrame(wi_rows).drop_duplicates(subset=["watchlist_id", "movie_id"])
    wi_df.to_csv(CLEAN_DIR / "watchlist_items.csv", index=False)
    print(f"  {len(wi_df)} watchlist items")

    n_parties = 15
    wp_rows = []
    for i in range(1, n_parties + 1):
        wp_rows.append({
            "party_id": i,
            "host_user_id": np.random.randint(1, min(41, len(users_df) + 1)),
            "party_name": np.random.choice([
                "Movie Night", "Weekend Marathon", "Classic Cinema Club",
                "Action Night", "Anime Watch Party", "Horror Night",
                "Comedy Fest", "Sci-Fi Saturday", "Drama Night",
                "Oscar Watch Party", "Nolan Marathon", "Thriller Thursday",
                "Family Movie Night", "World Cinema Night", "Date Night"
            ]),
            "planned_date": f"2025-{np.random.randint(1,13):02d}-{np.random.randint(1,29):02d}",
        })
    wp_df = pd.DataFrame(wp_rows)
    wp_df.to_csv(CLEAN_DIR / "watch_parties.csv", index=False)
    print(f"  {len(wp_df)} watch parties")

    wpm_rows = []
    for _, wp in wp_df.iterrows():
        n_members = np.random.randint(2, 5)
        members = np.random.choice(
            range(1, min(41, len(users_df) + 1)), size=n_members, replace=False
        )
        for uid in members:
            wpm_rows.append({"party_id": wp["party_id"], "user_id": int(uid)})
    wpm_df = pd.DataFrame(wpm_rows).drop_duplicates()
    wpm_df.to_csv(CLEAN_DIR / "watch_party_members.csv", index=False)
    print(f"  {len(wpm_df)} party members")

    wps_rows = []
    for _, wp in wp_df.iterrows():
        n_sugg = np.random.randint(2, 5)
        chosen = np.random.choice(movie_ids, size=n_sugg, replace=False)
        for mid in chosen:
            wps_rows.append({
                "party_id": wp["party_id"],
                "movie_id": int(mid),
                "group_score": round(np.random.uniform(6.5, 9.5), 3),
                "suggested_by": np.random.randint(1, min(41, len(users_df) + 1)),
            })
    wps_df = pd.DataFrame(wps_rows).drop_duplicates(subset=["party_id", "movie_id"])
    wps_df.to_csv(CLEAN_DIR / "watch_party_suggestions.csv", index=False)
    print(f"  {len(wps_df)} party suggestions")


def main():
    print("Processing datasets\n")

    imdb_basics = load_imdb_basics()
    imdb_ratings = load_imdb_ratings()
    ml_links = load_movielens_links()

    movies = select_movies(imdb_basics, imdb_ratings, ml_links)

    movies_df = process_movies(movies)
    process_genres(movies_df)
    process_people_and_credits(movies)
    users_df, _ = process_user_ratings(movies)
    process_tags_and_relevance(movies)
    process_external_ratings(movies_df)
    generate_synthetic_support_data(movies_df, users_df)

    print(f"\nAll CSVs written to {CLEAN_DIR}")
    print("Run 03_enrich_tmdb.py next to add posters/budget/revenue.")
    print("Then run 04_load_to_postgres.py to load into the database.")


if __name__ == "__main__":
    main()

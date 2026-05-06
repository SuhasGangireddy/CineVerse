"""Fix CSV files: convert float-formatted integers (278.0 -> 278) for PostgreSQL COPY."""

import pandas as pd
from pathlib import Path

CLEAN_DIR = Path(__file__).resolve().parent.parent / "data_clean"

# Columns that should be integer (not float) in each CSV
INT_COLUMNS = {
    "movies.csv": ["movie_id", "tmdb_id", "release_year", "runtime_minutes", "imdb_votes"],
    "people.csv": ["person_id", "birth_year", "death_year"],
    "role_types.csv": ["role_type_id"],
    "movie_credits.csv": ["credit_id", "movie_id", "person_id", "role_type_id", "billing_order"],
    "genres.csv": ["genre_id"],
    "movie_genres.csv": ["movie_id", "genre_id"],
    "distributors.csv": ["distributor_id"],
    "movie_distributors.csv": ["movie_id", "distributor_id"],
    "users.csv": ["user_id"],
    "user_ratings.csv": ["user_id", "movie_id"],
    "external_ratings.csv": ["movie_id", "vote_count"],
    "tags.csv": ["tag_id"],
    "movie_tag_relevance.csv": ["movie_id", "tag_id"],
    "streaming_platforms.csv": ["platform_id"],
    "movie_availability.csv": ["movie_id", "platform_id"],
    "awards.csv": ["award_id"],
    "movie_awards.csv": ["movie_award_id", "movie_id", "award_id", "person_id", "award_year"],
    "production_companies.csv": ["company_id", "founded_year"],
    "movie_production_companies.csv": ["movie_id", "company_id"],
    "watchlists.csv": ["watchlist_id", "user_id"],
    "watchlist_items.csv": ["watchlist_id", "movie_id"],
    "watch_parties.csv": ["party_id", "host_user_id"],
    "watch_party_members.csv": ["party_id", "user_id"],
    "watch_party_suggestions.csv": ["party_id", "movie_id", "suggested_by"],
}

fixed = 0
for csv_name, int_cols in INT_COLUMNS.items():
    path = CLEAN_DIR / csv_name
    if not path.exists():
        continue

    df = pd.read_csv(path)
    changed = False

    for col in int_cols:
        if col not in df.columns:
            continue
        # Convert float -> nullable Int64 -> string (drops .0, keeps NaN as empty)
        if df[col].dtype == float:
            df[col] = df[col].astype("Int64")
            changed = True

    if changed:
        df.to_csv(path, index=False)
        fixed += 1
        print(f"  Fixed: {csv_name}")
    else:
        print(f"  OK:    {csv_name}")

print(f"\nDone. Fixed {fixed} files.")

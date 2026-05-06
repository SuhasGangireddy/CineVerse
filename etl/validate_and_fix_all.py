# Validate all CSVs against the PostgreSQL schema and fix issues

import pandas as pd
import numpy as np
from pathlib import Path

CLEAN_DIR = Path(__file__).resolve().parent.parent / "data_clean"
issues_found = 0
issues_fixed = 0


def log_issue(msg):
    global issues_found
    issues_found += 1
    print(f"  [ISSUE] {msg}")


def log_fix(msg):
    global issues_fixed
    issues_fixed += 1
    print(f"  [FIXED] {msg}")


def fix_int_columns(df, columns, csv_name):
    for col in columns:
        if col not in df.columns:
            continue
        if df[col].dtype == float:
            log_issue(f"{csv_name}.{col} is float, converting to Int64")
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
            log_fix(f"{csv_name}.{col} -> Int64")
    return df


def fix_encoding(df, str_columns, csv_name):
    """Strip non-ASCII characters from string columns."""
    for col in str_columns:
        if col not in df.columns:
            continue
        if df[col].dtype == object:
            original = df[col].copy()
            df[col] = df[col].fillna('').astype(str)
            has_non_ascii = df[col].str.contains(r'[^\x00-\x7F]', regex=True, na=False)
            if has_non_ascii.any():
                count = has_non_ascii.sum()
                log_issue(f"{csv_name}.{col} has {count} rows with non-ASCII chars")
                df[col] = df[col].str.encode('ascii', errors='ignore').str.decode('ascii')
                log_fix(f"{csv_name}.{col} cleaned non-ASCII chars")
            df.loc[original.isna(), col] = None
    return df


def validate_foreign_keys(child_df, child_col, parent_df, parent_col, child_name, parent_name):
    child_vals = set(child_df[child_col].dropna().astype(int))
    parent_vals = set(parent_df[parent_col].dropna().astype(int))
    orphans = child_vals - parent_vals
    if orphans:
        log_issue(f"{child_name}.{child_col} has {len(orphans)} orphan FK values not in {parent_name}.{parent_col}")
        mask = child_df[child_col].isin(orphans)
        removed = mask.sum()
        child_df = child_df[~mask].copy()
        log_fix(f"Removed {removed} orphan rows from {child_name}")
    return child_df


def validate_unique(df, columns, csv_name):
    if isinstance(columns, str):
        columns = [columns]
    dupes = df.duplicated(subset=columns, keep='first')
    if dupes.any():
        count = dupes.sum()
        log_issue(f"{csv_name} has {count} duplicate rows on {columns}")
        df = df[~dupes].copy()
        log_fix(f"Removed {count} duplicates from {csv_name}")
    return df


def validate_check_constraints(df, csv_name):
    if csv_name == "movies.csv":
        bad = df['runtime_minutes'].notna() & (df['runtime_minutes'] <= 0)
        if bad.any():
            log_issue(f"movies: {bad.sum()} rows with runtime_minutes <= 0")
            df.loc[bad, 'runtime_minutes'] = pd.NA
            log_fix("Set invalid runtime_minutes to NULL")

        if 'budget' in df.columns:
            bad = df['budget'].notna() & (pd.to_numeric(df['budget'], errors='coerce') < 0)
            if bad.any():
                log_issue(f"movies: {bad.sum()} rows with negative budget")
                df.loc[bad, 'budget'] = pd.NA
                log_fix("Set negative budget to NULL")

        if 'revenue' in df.columns:
            bad = df['revenue'].notna() & (pd.to_numeric(df['revenue'], errors='coerce') < 0)
            if bad.any():
                log_issue(f"movies: {bad.sum()} rows with negative revenue")
                df.loc[bad, 'revenue'] = pd.NA
                log_fix("Set negative revenue to NULL")

        if 'imdb_rating' in df.columns:
            bad = df['imdb_rating'].notna() & ((df['imdb_rating'] < 0) | (df['imdb_rating'] > 10))
            if bad.any():
                log_issue(f"movies: {bad.sum()} rows with imdb_rating out of 0-10")
                df.loc[bad, 'imdb_rating'] = pd.NA
                log_fix("Set invalid imdb_rating to NULL")

        if 'release_year' in df.columns:
            bad = df['release_year'].notna() & (df['release_year'] < 1888)
            if bad.any():
                log_issue(f"movies: {bad.sum()} rows with release_year < 1888")
                df = df[~bad]
                log_fix("Removed movies with release_year < 1888")

    elif csv_name == "people.csv":
        both = df['death_year'].notna() & df['birth_year'].notna()
        bad = both & (df['death_year'] < df['birth_year'])
        if bad.any():
            log_issue(f"people: {bad.sum()} rows with death_year < birth_year")
            df.loc[bad, 'birth_year'] = pd.NA
            df.loc[bad, 'death_year'] = pd.NA
            log_fix("Nullified years for invalid death/birth combos")

    elif csv_name == "user_ratings.csv":
        bad = (df['rating'] < 0) | (df['rating'] > 10)
        if bad.any():
            log_issue(f"user_ratings: {bad.sum()} rows with rating out of 0-10")
            df = df[~bad]
            log_fix("Removed ratings outside 0-10")

    elif csv_name == "movie_tag_relevance.csv":
        bad = (df['relevance_score'] < 0) | (df['relevance_score'] > 1)
        if bad.any():
            log_issue(f"movie_tag_relevance: {bad.sum()} rows with score out of 0-1")
            df = df[~bad]
            log_fix("Removed tag relevance scores outside 0-1")

    elif csv_name == "movie_availability.csv":
        valid = {'subscription', 'rent', 'buy', 'free', 'theater'}
        bad = ~df['access_type'].isin(valid)
        if bad.any():
            log_issue(f"movie_availability: {bad.sum()} rows with invalid access_type")
            df = df[~bad]
            log_fix("Removed invalid access_type rows")

    elif csv_name == "movie_awards.csv":
        if 'result' in df.columns:
            valid = {'won', 'nominated'}
            bad = ~df['result'].isin(valid)
            if bad.any():
                log_issue(f"movie_awards: {bad.sum()} rows with invalid result")
                df = df[~bad]
                log_fix("Removed invalid award result rows")
        if 'award_year' in df.columns:
            bad = df['award_year'].notna() & (df['award_year'] < 1900)
            if bad.any():
                log_issue(f"movie_awards: {bad.sum()} rows with award_year < 1900")
                df = df[~bad]
                log_fix("Removed award rows with year < 1900")

    elif csv_name == "users.csv":
        valid = {'under_18', '18-24', '25-34', '35-44', '45-54', '55+'}
        bad = ~df['age_group'].isin(valid)
        if bad.any():
            log_issue(f"users: {bad.sum()} rows with invalid age_group")
            df.loc[bad, 'age_group'] = '25-34'
            log_fix("Set invalid age_groups to '25-34'")

    elif csv_name == "watchlist_items.csv":
        valid = {'unwatched', 'watching', 'watched'}
        bad = ~df['watched_status'].isin(valid)
        if bad.any():
            log_issue(f"watchlist_items: {bad.sum()} rows with invalid watched_status")
            df.loc[bad, 'watched_status'] = 'unwatched'
            log_fix("Set invalid watched_status to 'unwatched'")

    elif csv_name == "movie_credits.csv":
        if 'billing_order' in df.columns:
            bad = df['billing_order'].notna() & (df['billing_order'] <= 0)
            if bad.any():
                log_issue(f"movie_credits: {bad.sum()} rows with billing_order <= 0")
                df.loc[bad, 'billing_order'] = pd.NA
                log_fix("Set invalid billing_order to NULL")

    elif csv_name == "external_ratings.csv":
        bad = df['score'] < 0
        if bad.any():
            log_issue(f"external_ratings: {bad.sum()} rows with negative score")
            df = df[~bad]
            log_fix("Removed negative score rows")
        bad = df['max_score'] <= 0
        if bad.any():
            log_issue(f"external_ratings: {bad.sum()} rows with max_score <= 0")
            df = df[~bad]
            log_fix("Removed invalid max_score rows")

    return df


def validate_not_null(df, columns, csv_name):
    for col in columns:
        if col not in df.columns:
            continue
        nulls = df[col].isna() | (df[col].astype(str).str.strip() == '')
        if nulls.any():
            count = nulls.sum()
            log_issue(f"{csv_name}.{col} has {count} NULL/empty values")
            df = df[~nulls]
            log_fix(f"Removed {count} rows with NULL {col} from {csv_name}")
    return df


def main():
    global issues_found, issues_fixed
    print("Validating and fixing CSVs\n")

    csvs = {}
    for f in sorted(CLEAN_DIR.glob("*.csv")):
        csvs[f.name] = pd.read_csv(f, encoding='utf-8', encoding_errors='replace')

    # movies
    print("[movies.csv]")
    df = csvs["movies.csv"]
    df = fix_encoding(df, ['title', 'plot', 'language', 'country', 'genres_raw', 'imdb_id'], "movies.csv")
    df = fix_int_columns(df, ['movie_id', 'tmdb_id', 'release_year', 'runtime_minutes', 'imdb_votes'], "movies.csv")
    df = validate_not_null(df, ['movie_id', 'imdb_id', 'title'], "movies.csv")
    df = validate_unique(df, ['movie_id'], "movies.csv")
    df = validate_unique(df, ['imdb_id'], "movies.csv")
    df = validate_check_constraints(df, "movies.csv")
    csvs["movies.csv"] = df

    # people
    print("\n[people.csv]")
    df = csvs["people.csv"]
    df = fix_encoding(df, ['name', 'imdb_person_id', 'primary_profession'], "people.csv")
    df = fix_int_columns(df, ['person_id', 'birth_year', 'death_year'], "people.csv")
    df = validate_not_null(df, ['person_id', 'name'], "people.csv")
    df = validate_unique(df, ['person_id'], "people.csv")
    df = validate_check_constraints(df, "people.csv")
    csvs["people.csv"] = df

    # role_types
    print("\n[role_types.csv]")
    df = csvs["role_types.csv"]
    df = validate_not_null(df, ['role_type_id', 'role_name'], "role_types.csv")
    csvs["role_types.csv"] = df

    # movie_credits
    print("\n[movie_credits.csv]")
    df = csvs["movie_credits.csv"]
    df = fix_encoding(df, ['character_name'], "movie_credits.csv")
    df = fix_int_columns(df, ['credit_id', 'movie_id', 'person_id', 'role_type_id', 'billing_order'], "movie_credits.csv")
    df = validate_not_null(df, ['movie_id', 'person_id', 'role_type_id'], "movie_credits.csv")
    df = validate_check_constraints(df, "movie_credits.csv")
    df = validate_foreign_keys(df, 'movie_id', csvs["movies.csv"], 'movie_id', "movie_credits", "movies")
    df = validate_foreign_keys(df, 'person_id', csvs["people.csv"], 'person_id', "movie_credits", "people")
    df = validate_foreign_keys(df, 'role_type_id', csvs["role_types.csv"], 'role_type_id', "movie_credits", "role_types")
    df = validate_unique(df, ['movie_id', 'person_id', 'role_type_id', 'character_name'], "movie_credits")
    df['credit_id'] = range(1, len(df) + 1)
    csvs["movie_credits.csv"] = df

    # genres
    print("\n[genres.csv]")
    df = csvs["genres.csv"]
    df = validate_not_null(df, ['genre_id', 'genre_name'], "genres.csv")
    df = validate_unique(df, ['genre_name'], "genres.csv")
    csvs["genres.csv"] = df

    # movie_genres
    print("\n[movie_genres.csv]")
    df = csvs["movie_genres.csv"]
    df = validate_foreign_keys(df, 'movie_id', csvs["movies.csv"], 'movie_id', "movie_genres", "movies")
    df = validate_foreign_keys(df, 'genre_id', csvs["genres.csv"], 'genre_id', "movie_genres", "genres")
    df = validate_unique(df, ['movie_id', 'genre_id'], "movie_genres")
    csvs["movie_genres.csv"] = df

    # distributors
    print("\n[distributors.csv]")
    df = csvs["distributors.csv"]
    df = fix_encoding(df, ['name', 'address', 'country'], "distributors.csv")
    csvs["distributors.csv"] = df

    # movie_distributors
    print("\n[movie_distributors.csv]")
    df = csvs["movie_distributors.csv"]
    df = validate_foreign_keys(df, 'movie_id', csvs["movies.csv"], 'movie_id', "movie_distributors", "movies")
    df = validate_foreign_keys(df, 'distributor_id', csvs["distributors.csv"], 'distributor_id', "movie_distributors", "distributors")
    df = validate_unique(df, ['movie_id', 'distributor_id', 'region'], "movie_distributors")
    csvs["movie_distributors.csv"] = df

    # users
    print("\n[users.csv]")
    df = csvs["users.csv"]
    df = validate_not_null(df, ['user_id', 'username'], "users.csv")
    df = validate_unique(df, ['username'], "users.csv")
    df = validate_check_constraints(df, "users.csv")
    csvs["users.csv"] = df

    # user_ratings
    print("\n[user_ratings.csv]")
    df = csvs["user_ratings.csv"]
    df = validate_foreign_keys(df, 'movie_id', csvs["movies.csv"], 'movie_id', "user_ratings", "movies")
    df = validate_foreign_keys(df, 'user_id', csvs["users.csv"], 'user_id', "user_ratings", "users")
    df = validate_unique(df, ['user_id', 'movie_id'], "user_ratings")
    df = validate_check_constraints(df, "user_ratings.csv")
    csvs["user_ratings.csv"] = df

    # external_ratings
    print("\n[external_ratings.csv]")
    df = csvs["external_ratings.csv"]
    df = validate_foreign_keys(df, 'movie_id', csvs["movies.csv"], 'movie_id', "external_ratings", "movies")
    df = validate_unique(df, ['movie_id', 'source_name'], "external_ratings")
    df = validate_check_constraints(df, "external_ratings.csv")
    csvs["external_ratings.csv"] = df

    # tags
    print("\n[tags.csv]")
    df = csvs["tags.csv"]
    df = fix_encoding(df, ['tag_name'], "tags.csv")
    df = validate_not_null(df, ['tag_id', 'tag_name'], "tags.csv")
    df = validate_unique(df, ['tag_name'], "tags.csv")
    csvs["tags.csv"] = df

    # movie_tag_relevance
    print("\n[movie_tag_relevance.csv]")
    df = csvs["movie_tag_relevance.csv"]
    df = validate_foreign_keys(df, 'movie_id', csvs["movies.csv"], 'movie_id', "movie_tag_relevance", "movies")
    df = validate_foreign_keys(df, 'tag_id', csvs["tags.csv"], 'tag_id', "movie_tag_relevance", "tags")
    df = validate_unique(df, ['movie_id', 'tag_id'], "movie_tag_relevance")
    df = validate_check_constraints(df, "movie_tag_relevance.csv")
    csvs["movie_tag_relevance.csv"] = df

    # streaming_platforms
    print("\n[streaming_platforms.csv]")
    df = csvs["streaming_platforms.csv"]
    csvs["streaming_platforms.csv"] = df

    # movie_availability
    print("\n[movie_availability.csv]")
    df = csvs["movie_availability.csv"]
    df = validate_foreign_keys(df, 'movie_id', csvs["movies.csv"], 'movie_id', "movie_availability", "movies")
    df = validate_foreign_keys(df, 'platform_id', csvs["streaming_platforms.csv"], 'platform_id', "movie_availability", "streaming_platforms")
    df = validate_unique(df, ['movie_id', 'platform_id', 'region', 'access_type'], "movie_availability")
    df = validate_check_constraints(df, "movie_availability.csv")
    csvs["movie_availability.csv"] = df

    # awards
    print("\n[awards.csv]")
    df = csvs["awards.csv"]
    df = fix_encoding(df, ['award_name', 'category'], "awards.csv")
    csvs["awards.csv"] = df

    # movie_awards
    print("\n[movie_awards.csv]")
    df = csvs["movie_awards.csv"]
    df = fix_int_columns(df, ['movie_award_id', 'movie_id', 'award_id', 'person_id', 'award_year'], "movie_awards.csv")
    df = validate_foreign_keys(df, 'movie_id', csvs["movies.csv"], 'movie_id', "movie_awards", "movies")
    df = validate_foreign_keys(df, 'award_id', csvs["awards.csv"], 'award_id', "movie_awards", "awards")
    # person_id FK is nullable, only check non-null values
    if df['person_id'].notna().any():
        non_null = df[df['person_id'].notna()]
        valid_persons = set(csvs["people.csv"]['person_id'].dropna().astype(int))
        bad_persons = non_null[~non_null['person_id'].astype(int).isin(valid_persons)]
        if len(bad_persons) > 0:
            log_issue(f"movie_awards: {len(bad_persons)} rows with invalid person_id FK")
            df.loc[bad_persons.index, 'person_id'] = pd.NA
            log_fix("Set invalid person_id to NULL in movie_awards")
    df = validate_unique(df, ['movie_id', 'award_id', 'award_year'], "movie_awards")
    df = validate_check_constraints(df, "movie_awards.csv")
    df['movie_award_id'] = range(1, len(df) + 1)
    csvs["movie_awards.csv"] = df

    # production_companies
    print("\n[production_companies.csv]")
    df = csvs["production_companies.csv"]
    csvs["production_companies.csv"] = df

    # movie_production_companies
    print("\n[movie_production_companies.csv]")
    df = csvs["movie_production_companies.csv"]
    df = validate_foreign_keys(df, 'movie_id', csvs["movies.csv"], 'movie_id', "movie_prod_companies", "movies")
    df = validate_foreign_keys(df, 'company_id', csvs["production_companies.csv"], 'company_id', "movie_prod_companies", "production_companies")
    df = validate_unique(df, ['movie_id', 'company_id'], "movie_prod_companies")
    csvs["movie_production_companies.csv"] = df

    # watchlists
    print("\n[watchlists.csv]")
    df = csvs["watchlists.csv"]
    df = validate_foreign_keys(df, 'user_id', csvs["users.csv"], 'user_id', "watchlists", "users")
    csvs["watchlists.csv"] = df

    # watchlist_items
    print("\n[watchlist_items.csv]")
    df = csvs["watchlist_items.csv"]
    df = validate_foreign_keys(df, 'watchlist_id', csvs["watchlists.csv"], 'watchlist_id', "watchlist_items", "watchlists")
    df = validate_foreign_keys(df, 'movie_id', csvs["movies.csv"], 'movie_id', "watchlist_items", "movies")
    df = validate_unique(df, ['watchlist_id', 'movie_id'], "watchlist_items")
    df = validate_check_constraints(df, "watchlist_items.csv")
    csvs["watchlist_items.csv"] = df

    # watch_parties
    print("\n[watch_parties.csv]")
    df = csvs["watch_parties.csv"]
    df = validate_foreign_keys(df, 'host_user_id', csvs["users.csv"], 'user_id', "watch_parties", "users")
    csvs["watch_parties.csv"] = df

    # watch_party_members
    print("\n[watch_party_members.csv]")
    df = csvs["watch_party_members.csv"]
    df = validate_foreign_keys(df, 'party_id', csvs["watch_parties.csv"], 'party_id', "watch_party_members", "watch_parties")
    df = validate_foreign_keys(df, 'user_id', csvs["users.csv"], 'user_id', "watch_party_members", "users")
    df = validate_unique(df, ['party_id', 'user_id'], "watch_party_members")
    csvs["watch_party_members.csv"] = df

    # watch_party_suggestions
    print("\n[watch_party_suggestions.csv]")
    df = csvs["watch_party_suggestions.csv"]
    df = validate_foreign_keys(df, 'party_id', csvs["watch_parties.csv"], 'party_id', "watch_party_suggestions", "watch_parties")
    df = validate_foreign_keys(df, 'movie_id', csvs["movies.csv"], 'movie_id', "watch_party_suggestions", "movies")
    if 'suggested_by' in df.columns:
        df = validate_foreign_keys(df, 'suggested_by', csvs["users.csv"], 'user_id', "watch_party_suggestions", "users")
    df = validate_unique(df, ['party_id', 'movie_id'], "watch_party_suggestions")
    csvs["watch_party_suggestions.csv"] = df

    # Save everything
    print("\nSaving fixed CSVs")
    total_rows = 0
    for name, df in csvs.items():
        path = CLEAN_DIR / name
        df.to_csv(path, index=False, encoding='utf-8')
        total_rows += len(df)
        print(f"  {name:45s} {len(df):>6} rows")

    print(f"\n  {'TOTAL':45s} {total_rows:>6} rows")
    print(f"\nIssues found: {issues_found}")
    print(f"Issues fixed: {issues_fixed}")

    if issues_found == 0:
        print("All CSVs are clean. Ready to load.")
    else:
        print(f"All {issues_fixed} issues have been fixed. Ready to load.")


if __name__ == "__main__":
    main()

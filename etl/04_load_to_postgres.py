"""
Step 4: Load clean CSVs into PostgreSQL.

This script:
  1. Reads all CSVs from data_clean/
  2. Generates and executes SQL INSERT statements
  3. Resets sequences to correct values

Usage:
  python 04_load_to_postgres.py --host localhost --port 5432 --db cineverse --user postgres --password yourpass

Or set environment variables:
  export PGHOST=localhost PGPORT=5432 PGDATABASE=cineverse PGUSER=postgres PGPASSWORD=yourpass
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
from pathlib import Path

CLEAN_DIR = Path(__file__).resolve().parent.parent / "data_clean"
SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def generate_sql_load_script():
    """Generate 02_load_data.sql from CSVs — pure SQL COPY commands."""
    print("Generating 02_load_data.sql from CSVs ...")

    lines = [
        "-- ============================================================================",
        "-- CineVerse: Data Loading Script (generated from real datasets)",
        "-- ISE 503: Data Management - Spring 2026",
        "-- ",
        "-- Script: 02_load_data.sql",
        "-- Purpose: Load processed CSV data into PostgreSQL tables",
        "-- Usage: Run from the project root directory:",
        "--   psql -U postgres -d cineverse -f sql/02_load_data.sql",
        "-- ============================================================================",
        "",
        "-- NOTE: Adjust file paths below to match your system.",
        "-- The \\copy command uses client-side paths (relative to where psql is run).",
        "",
    ]

    # Define load order (respecting foreign key dependencies)
    load_order = [
        ("movies.csv", "Movie",
         "movie_id, imdb_id, tmdb_id, title, release_year, runtime_minutes, language, country, plot, budget, revenue, imdb_rating, imdb_votes, genres_raw",
         "movie_id, imdb_id, tmdb_id, title, release_date, runtime_minutes, language, country, plot, budget, revenue",
         True),
        ("people.csv", "Person",
         "person_id, imdb_person_id, name, birth_year, death_year, primary_profession",
         None, True),
        ("role_types.csv", "RoleType",
         "role_type_id, role_name",
         None, True),
        ("movie_credits.csv", "MovieCredit",
         "credit_id, movie_id, person_id, role_type_id, character_name, billing_order",
         None, True),
        ("genres.csv", "Genre",
         "genre_id, genre_name",
         None, True),
        ("movie_genres.csv", "MovieGenre",
         "movie_id, genre_id",
         None, False),
        ("distributors.csv", "Distributor",
         "distributor_id, name, address, country",
         None, True),
        ("movie_distributors.csv", "MovieDistributor",
         "movie_id, distributor_id, region",
         None, False),
        ("users.csv", "UserProfile",
         "user_id, username, email, age_group, preferred_language",
         None, True),
        ("user_ratings.csv", "UserRating",
         "user_id, movie_id, rating, rating_date",
         None, False),
        ("external_ratings.csv", "ExternalRating",
         "movie_id, source_name, score, max_score, vote_count",
         None, False),
        ("tags.csv", "Tag",
         "tag_id, tag_name",
         None, True),
        ("movie_tag_relevance.csv", "MovieTagRelevance",
         "movie_id, tag_id, relevance_score",
         None, False),
        ("streaming_platforms.csv", "StreamingPlatform",
         "platform_id, name, country, website_url",
         None, True),
        ("movie_availability.csv", "MovieAvailability",
         "movie_id, platform_id, region, access_type, start_date, end_date",
         None, False),
        ("awards.csv", "Award",
         "award_id, award_name, category",
         None, True),
        ("movie_awards.csv", "MovieAward",
         "movie_award_id, movie_id, award_id, person_id, award_year, result",
         None, True),
        ("production_companies.csv", "ProductionCompany",
         "company_id, name, country, founded_year",
         None, True),
        ("movie_production_companies.csv", "MovieProductionCompany",
         "movie_id, company_id",
         None, False),
        ("watchlists.csv", "Watchlist",
         "watchlist_id, user_id, name",
         None, True),
        ("watchlist_items.csv", "WatchlistItem",
         "watchlist_id, movie_id, watched_status",
         None, False),
        ("watch_parties.csv", "WatchParty",
         "party_id, host_user_id, party_name, planned_date",
         None, True),
        ("watch_party_members.csv", "WatchPartyMember",
         "party_id, user_id",
         None, False),
        ("watch_party_suggestions.csv", "WatchPartySuggestion",
         "party_id, movie_id, group_score, suggested_by",
         None, False),
    ]

    for csv_name, table_name, columns, _, has_sequence in load_order:
        csv_path = CLEAN_DIR / csv_name
        if not csv_path.exists():
            lines.append(f"-- WARNING: {csv_name} not found, skipping {table_name}")
            lines.append("")
            continue

        lines.append(f"-- Load {table_name}")
        lines.append(f"\\copy {table_name}({columns}) FROM 'data_clean/{csv_name}' WITH (FORMAT csv, HEADER true, NULL '');")
        lines.append("")

    # Reset sequences
    lines.append("-- Reset sequences to max ID + 1")
    sequence_resets = [
        ("movie_movie_id_seq", "Movie", "movie_id"),
        ("person_person_id_seq", "Person", "person_id"),
        ("roletype_role_type_id_seq", "RoleType", "role_type_id"),
        ("moviecredit_credit_id_seq", "MovieCredit", "credit_id"),
        ("genre_genre_id_seq", "Genre", "genre_id"),
        ("distributor_distributor_id_seq", "Distributor", "distributor_id"),
        ("userprofile_user_id_seq", "UserProfile", "user_id"),
        ("review_review_id_seq", "Review", "review_id"),
        ("tag_tag_id_seq", "Tag", "tag_id"),
        ("recommendationlog_recommendation_id_seq", "RecommendationLog", "recommendation_id"),
        ("streamingplatform_platform_id_seq", "StreamingPlatform", "platform_id"),
        ("award_award_id_seq", "Award", "award_id"),
        ("movieaward_movie_award_id_seq", "MovieAward", "movie_award_id"),
        ("productioncompany_company_id_seq", "ProductionCompany", "company_id"),
        ("watchlist_watchlist_id_seq", "Watchlist", "watchlist_id"),
        ("watchparty_party_id_seq", "WatchParty", "party_id"),
    ]
    for seq, table, col in sequence_resets:
        lines.append(f"SELECT setval('{seq}', COALESCE((SELECT MAX({col}) FROM {table}), 0) + 1, false);")

    lines.append("")
    lines.append("-- Data loading complete!")
    lines.append("-- Verify with: SELECT tablename, n_live_tup FROM pg_stat_user_tables ORDER BY tablename;")

    sql_content = "\n".join(lines)
    out_path = SQL_DIR / "02_load_data.sql"
    out_path.write_text(sql_content, encoding="utf-8")
    print(f"  -> {out_path}")


def generate_insert_sql():
    """Alternative: Generate INSERT statements instead of COPY for portability."""
    print("\nGenerating 02_insert_data.sql (INSERT-based alternative) ...")

    lines = [
        "-- ============================================================================",
        "-- CineVerse: Data Loading Script (INSERT statements, generated from real data)",
        "-- ISE 503: Data Management - Spring 2026",
        "-- Alternative to COPY-based loading for portability.",
        "-- ============================================================================",
        "",
    ]

    # Load order with table info
    tables_to_load = [
        ("genres.csv", "Genre", ["genre_id", "genre_name"]),
        ("role_types.csv", "RoleType", ["role_type_id", "role_name"]),
        ("distributors.csv", "Distributor", ["distributor_id", "name", "address", "country"]),
        ("streaming_platforms.csv", "StreamingPlatform", ["platform_id", "name", "country", "website_url"]),
        ("awards.csv", "Award", ["award_id", "award_name", "category"]),
        ("production_companies.csv", "ProductionCompany", ["company_id", "name", "country", "founded_year"]),
        ("tags.csv", "Tag", ["tag_id", "tag_name"]),
        ("movies.csv", "Movie", ["movie_id", "imdb_id", "tmdb_id", "title", "runtime_minutes",
                                  "language", "country", "plot", "budget", "revenue"]),
        ("people.csv", "Person", ["person_id", "imdb_person_id", "name", "birth_year",
                                   "death_year", "primary_profession"]),
        ("users.csv", "UserProfile", ["user_id", "username", "email", "age_group", "preferred_language"]),
        ("movie_credits.csv", "MovieCredit", ["credit_id", "movie_id", "person_id",
                                               "role_type_id", "character_name", "billing_order"]),
        ("movie_genres.csv", "MovieGenre", ["movie_id", "genre_id"]),
        ("movie_distributors.csv", "MovieDistributor", ["movie_id", "distributor_id", "region"]),
        ("user_ratings.csv", "UserRating", ["user_id", "movie_id", "rating", "rating_date"]),
        ("external_ratings.csv", "ExternalRating", ["movie_id", "source_name", "score", "max_score", "vote_count"]),
        ("movie_tag_relevance.csv", "MovieTagRelevance", ["movie_id", "tag_id", "relevance_score"]),
        ("movie_availability.csv", "MovieAvailability", ["movie_id", "platform_id", "region",
                                                          "access_type", "start_date", "end_date"]),
        ("movie_awards.csv", "MovieAward", ["movie_award_id", "movie_id", "award_id",
                                             "person_id", "award_year", "result"]),
        ("movie_production_companies.csv", "MovieProductionCompany", ["movie_id", "company_id"]),
        ("watchlists.csv", "Watchlist", ["watchlist_id", "user_id", "name"]),
        ("watchlist_items.csv", "WatchlistItem", ["watchlist_id", "movie_id", "watched_status"]),
        ("watch_parties.csv", "WatchParty", ["party_id", "host_user_id", "party_name", "planned_date"]),
        ("watch_party_members.csv", "WatchPartyMember", ["party_id", "user_id"]),
        ("watch_party_suggestions.csv", "WatchPartySuggestion", ["party_id", "movie_id",
                                                                   "group_score", "suggested_by"]),
    ]

    for csv_name, table_name, columns in tables_to_load:
        csv_path = CLEAN_DIR / csv_name
        if not csv_path.exists():
            lines.append(f"-- {csv_name} not found, skipping {table_name}")
            continue

        df = pd.read_csv(csv_path)
        # Only use columns that exist in the CSV
        available_cols = [c for c in columns if c in df.columns]
        if not available_cols:
            continue

        df = df[available_cols]
        lines.append(f"-- {table_name} ({len(df)} rows)")

        # Generate INSERT statements in batches
        batch_size = 50
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i + batch_size]
            values_list = []
            for _, row in batch.iterrows():
                vals = []
                for c in available_cols:
                    v = row[c]
                    if pd.isna(v):
                        vals.append("NULL")
                    elif isinstance(v, (int, np.integer)):
                        vals.append(str(int(v)))
                    elif isinstance(v, (float, np.floating)):
                        vals.append(str(round(v, 3)))
                    else:
                        escaped = str(v).replace("'", "''")
                        vals.append(f"'{escaped}'")
                values_list.append(f"({', '.join(vals)})")

            cols_str = ", ".join(available_cols)
            lines.append(f"INSERT INTO {table_name} ({cols_str}) VALUES")
            lines.append(",\n".join(values_list) + ";")

        lines.append("")

    sql_content = "\n".join(lines)
    out_path = SQL_DIR / "02_insert_data.sql"
    out_path.write_text(sql_content, encoding="utf-8")
    print(f"  -> {out_path}")
    print(f"  (File size: {out_path.stat().st_size / 1024:.0f} KB)")


def print_summary():
    """Print row counts for all CSVs."""
    print("\n" + "=" * 60)
    print("DATA SUMMARY")
    print("=" * 60)
    total = 0
    csv_files = sorted(CLEAN_DIR.glob("*.csv"))
    for f in csv_files:
        df = pd.read_csv(f)
        count = len(df)
        total += count
        print(f"  {f.name:40s} {count:>6} rows")
    print(f"  {'TOTAL':40s} {total:>6} rows")
    n_tables = len(csv_files)
    print(f"  {'AVERAGE per table':40s} {total // n_tables:>6} rows")
    print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("CineVerse ETL - Step 4: Generate SQL Load Scripts")
    print("=" * 60)

    generate_sql_load_script()
    generate_insert_sql()
    print_summary()

    print("\nNext steps:")
    print("  1. Create the database: createdb -U postgres cineverse")
    print("  2. Create tables: psql -U postgres -d cineverse -f sql/01_create_tables.sql")
    print("  3. Load data (option A - COPY): cd project_root && psql -U postgres -d cineverse -f sql/02_load_data.sql")
    print("  4. Load data (option B - INSERT): psql -U postgres -d cineverse -f sql/02_insert_data.sql")
    print("  5. Run queries: psql -U postgres -d cineverse -f sql/03_complex_queries.sql")

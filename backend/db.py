"""Database connection and query functions for CineVerse FastAPI backend."""

import os
from pathlib import Path
import psycopg2
import psycopg2.extras
from decimal import Decimal
from datetime import date, datetime

# Load .env from project root if present
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def get_connection():
    return psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ.get("PGDATABASE", "cineverse"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", ""),
    )


def _serialize(rows):
    """Convert psycopg2 RealDictRow to JSON-safe dicts."""
    result = []
    for row in rows:
        d = {}
        for k, v in row.items():
            if isinstance(v, Decimal):
                d[k] = float(v)
            elif isinstance(v, (date, datetime)):
                d[k] = v.isoformat()
            else:
                d[k] = v
        result.append(d)
    return result


def query(sql, params=None):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return _serialize(cur.fetchall())
    finally:
        conn.close()


def execute(sql, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()
    finally:
        conn.close()


def execute_returning(sql, params=None):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            result = _serialize(cur.fetchall())
        conn.commit()
        return result
    finally:
        conn.close()


# ── Query Functions ──────────────────────────────────────────────────────────

def get_users():
    return query("SELECT user_id, username, email, age_group FROM UserProfile ORDER BY user_id LIMIT 50")


def get_dashboard_stats():
    return query("""
        SELECT
            (SELECT COUNT(*) FROM Movie) AS total_movies,
            (SELECT COUNT(*) FROM Person) AS total_people,
            (SELECT COUNT(*) FROM UserProfile) AS total_users,
            (SELECT COUNT(*) FROM UserRating) AS total_ratings
    """)[0]


def get_top_movies(limit=15):
    return query("""
        SELECT m.movie_id, m.title, m.release_year, m.imdb_rating, m.genres_raw,
               m.runtime_minutes, m.poster_url,
               ROUND(AVG(ur.rating), 2) AS avg_user_rating,
               COUNT(ur.user_id) AS num_ratings
        FROM Movie m
        LEFT JOIN UserRating ur ON ur.movie_id = m.movie_id
        GROUP BY m.movie_id
        ORDER BY avg_user_rating DESC NULLS LAST
        LIMIT %s
    """, [limit])


def get_trending_movies(limit=15):
    return query("""
        SELECT m.movie_id, m.title, m.release_year, m.imdb_rating, m.genres_raw,
               m.runtime_minutes, m.poster_url, COUNT(ur.user_id) AS num_ratings
        FROM Movie m
        JOIN UserRating ur ON ur.movie_id = m.movie_id
        GROUP BY m.movie_id
        ORDER BY num_ratings DESC
        LIMIT %s
    """, [limit])


def get_recently_released(limit=15):
    return query("""
        SELECT movie_id, title, release_year, imdb_rating, genres_raw,
               runtime_minutes, poster_url
        FROM Movie
        WHERE release_year IS NOT NULL
        ORDER BY release_year DESC, imdb_rating DESC NULLS LAST
        LIMIT %s
    """, [limit])


def search_movies(title=None, genre=None, year_from=None, year_to=None,
                  min_rating=None, platform=None, director=None, actor=None,
                  tag=None, limit=50):
    conditions = []
    params = []

    if title:
        conditions.append("(m.title ILIKE %s OR p_search.name ILIKE %s)")
        params.extend([f"%{title}%", f"%{title}%"])
    if genre:
        conditions.append("g.genre_name = %s")
        params.append(genre)
    if year_from:
        conditions.append("m.release_year >= %s")
        params.append(year_from)
    if year_to:
        conditions.append("m.release_year <= %s")
        params.append(year_to)
    if min_rating:
        conditions.append("m.imdb_rating >= %s")
        params.append(min_rating)
    if platform:
        conditions.append("sp.name = %s")
        params.append(platform)
    if director:
        conditions.append("p_dir.name ILIKE %s AND rt_dir.role_name = 'Director'")
        params.append(f"%{director}%")
    if actor:
        conditions.append("p_act.name ILIKE %s AND rt_act.role_name = 'Actor'")
        params.append(f"%{actor}%")
    if tag:
        conditions.append("t.tag_name ILIKE %s AND mtr.relevance_score >= 0.5")
        params.append(f"%{tag}%")

    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    sql = f"""
    SELECT DISTINCT m.movie_id, m.title, m.release_year, m.runtime_minutes,
           m.imdb_rating, m.imdb_votes, m.language, m.genres_raw, m.poster_url
    FROM Movie m
    LEFT JOIN MovieGenre mg ON mg.movie_id = m.movie_id
    LEFT JOIN Genre g ON g.genre_id = mg.genre_id
    LEFT JOIN MovieAvailability ma ON ma.movie_id = m.movie_id
    LEFT JOIN StreamingPlatform sp ON sp.platform_id = ma.platform_id
    LEFT JOIN MovieCredit mc_search ON mc_search.movie_id = m.movie_id
    LEFT JOIN Person p_search ON p_search.person_id = mc_search.person_id
    LEFT JOIN MovieCredit mc_dir ON mc_dir.movie_id = m.movie_id
    LEFT JOIN Person p_dir ON p_dir.person_id = mc_dir.person_id
    LEFT JOIN RoleType rt_dir ON rt_dir.role_type_id = mc_dir.role_type_id
    LEFT JOIN MovieCredit mc_act ON mc_act.movie_id = m.movie_id
    LEFT JOIN Person p_act ON p_act.person_id = mc_act.person_id
    LEFT JOIN RoleType rt_act ON rt_act.role_type_id = mc_act.role_type_id
    LEFT JOIN MovieTagRelevance mtr ON mtr.movie_id = m.movie_id
    LEFT JOIN Tag t ON t.tag_id = mtr.tag_id
    {where}
    ORDER BY m.imdb_rating DESC NULLS LAST
    LIMIT %s
    """
    params.append(limit)
    return query(sql, params)


def get_movie_details(movie_id):
    movie = query("SELECT * FROM Movie WHERE movie_id = %s", [movie_id])
    if not movie:
        return None
    movie = movie[0]

    movie["genres"] = query("""
        SELECT g.genre_name FROM Genre g
        JOIN MovieGenre mg ON mg.genre_id = g.genre_id
        WHERE mg.movie_id = %s ORDER BY g.genre_name
    """, [movie_id])

    movie["cast"] = query("""
        SELECT p.person_id, p.name, mc.character_name, rt.role_name, mc.billing_order
        FROM MovieCredit mc
        JOIN Person p ON p.person_id = mc.person_id
        JOIN RoleType rt ON rt.role_type_id = mc.role_type_id
        WHERE mc.movie_id = %s
        ORDER BY rt.role_name, mc.billing_order NULLS LAST
    """, [movie_id])

    movie["external_ratings"] = query("""
        SELECT source_name, score, max_score, vote_count
        FROM ExternalRating WHERE movie_id = %s
    """, [movie_id])

    movie["user_rating_stats"] = query("""
        SELECT ROUND(AVG(rating), 2) as avg_rating, COUNT(*) as count
        FROM UserRating WHERE movie_id = %s
    """, [movie_id])[0]

    movie["platforms"] = query("""
        SELECT sp.name, ma.access_type, ma.region
        FROM MovieAvailability ma
        JOIN StreamingPlatform sp ON sp.platform_id = ma.platform_id
        WHERE ma.movie_id = %s ORDER BY sp.name
    """, [movie_id])

    movie["awards"] = query("""
        SELECT a.award_name, a.category, ma.award_year, ma.result
        FROM MovieAward ma JOIN Award a ON a.award_id = ma.award_id
        WHERE ma.movie_id = %s ORDER BY ma.award_year DESC
    """, [movie_id])

    movie["tags"] = query("""
        SELECT t.tag_name, mtr.relevance_score
        FROM MovieTagRelevance mtr JOIN Tag t ON t.tag_id = mtr.tag_id
        WHERE mtr.movie_id = %s ORDER BY mtr.relevance_score DESC LIMIT 10
    """, [movie_id])

    movie["reviews"] = query("""
        SELECT r.review_text, r.sentiment, r.review_date, u.username
        FROM Review r JOIN UserProfile u ON u.user_id = r.user_id
        WHERE r.movie_id = %s ORDER BY r.review_date DESC LIMIT 10
    """, [movie_id])

    return movie


def get_similar_movies(movie_id, limit=8):
    return query("""
        SELECT DISTINCT m2.movie_id, m2.title, m2.release_year, m2.imdb_rating,
               m2.genres_raw, m2.poster_url,
               COUNT(DISTINCT shared_g.genre_id) + COUNT(DISTINCT shared_t.tag_id) AS similarity_score
        FROM Movie m2
        LEFT JOIN MovieGenre mg2 ON mg2.movie_id = m2.movie_id
        LEFT JOIN MovieGenre mg1 ON mg1.genre_id = mg2.genre_id AND mg1.movie_id = %s
        LEFT JOIN Genre shared_g ON shared_g.genre_id = mg1.genre_id
        LEFT JOIN MovieTagRelevance mtr2 ON mtr2.movie_id = m2.movie_id AND mtr2.relevance_score >= 0.6
        LEFT JOIN MovieTagRelevance mtr1 ON mtr1.tag_id = mtr2.tag_id AND mtr1.movie_id = %s AND mtr1.relevance_score >= 0.6
        LEFT JOIN Tag shared_t ON shared_t.tag_id = mtr1.tag_id
        WHERE m2.movie_id != %s
          AND (mg1.movie_id IS NOT NULL OR mtr1.movie_id IS NOT NULL)
        GROUP BY m2.movie_id
        ORDER BY similarity_score DESC, m2.imdb_rating DESC NULLS LAST
        LIMIT %s
    """, [movie_id, movie_id, movie_id, limit])


def get_genres():
    return query("SELECT genre_id, genre_name FROM Genre ORDER BY genre_name")


def get_platforms():
    return query("SELECT platform_id, name FROM StreamingPlatform ORDER BY name")


def get_tags():
    return query("SELECT tag_id, tag_name FROM Tag ORDER BY tag_name")


def get_recommendations(user_id, tags=None, platform=None, min_rating=None, limit=15):
    extra_conditions = []
    params = [user_id, user_id]

    base_tag_filter = """
        t.tag_name IN (
            SELECT DISTINCT t2.tag_name
            FROM UserRating ur2
            JOIN MovieTagRelevance mtr2 ON mtr2.movie_id = ur2.movie_id
            JOIN Tag t2 ON t2.tag_id = mtr2.tag_id
            WHERE ur2.user_id = %s AND ur2.rating >= 7.0 AND mtr2.relevance_score >= 0.5
        )
    """

    if tags:
        tag_placeholders = ",".join(["%s"] * len(tags))
        base_tag_filter = f"t.tag_name IN ({tag_placeholders})"
        params = [user_id]  # only need user_id for the LEFT JOIN
        params.extend(tags)

    if platform:
        extra_conditions.append("""
            m.movie_id IN (
                SELECT ma.movie_id FROM MovieAvailability ma
                JOIN StreamingPlatform sp ON sp.platform_id = ma.platform_id
                WHERE sp.name = %s
            )
        """)
        params.append(platform)

    if min_rating:
        extra_conditions.append("m.imdb_rating >= %s")
        params.append(min_rating)

    extra_where = (" AND " + " AND ".join(extra_conditions)) if extra_conditions else ""

    sql = f"""
        SELECT m.movie_id, m.title, m.release_year, m.imdb_rating, m.poster_url,
               m.genres_raw, m.runtime_minutes,
               ROUND(SUM(mtr.relevance_score), 3) AS rec_score,
               STRING_AGG(DISTINCT t.tag_name, ', ' ORDER BY t.tag_name) AS matching_tags,
               COUNT(DISTINCT t.tag_id) AS tag_match_count
        FROM MovieTagRelevance mtr
        JOIN Tag t ON t.tag_id = mtr.tag_id
        JOIN Movie m ON m.movie_id = mtr.movie_id
        LEFT JOIN UserRating ur ON ur.movie_id = m.movie_id AND ur.user_id = %s
        WHERE mtr.relevance_score >= 0.5
          AND ur.user_id IS NULL
          AND {base_tag_filter}
          {extra_where}
        GROUP BY m.movie_id, m.title, m.release_year, m.imdb_rating, m.poster_url,
                 m.genres_raw, m.runtime_minutes
        ORDER BY rec_score DESC
        LIMIT %s
    """
    params.append(limit)
    return query(sql, params)


def get_user_watchlist(user_id):
    return query("""
        SELECT wi.watched_status, m.movie_id, m.title, m.release_year,
               m.imdb_rating, m.genres_raw, m.poster_url,
               w.watchlist_id, w.name as watchlist_name
        FROM Watchlist w
        JOIN WatchlistItem wi ON wi.watchlist_id = w.watchlist_id
        JOIN Movie m ON m.movie_id = wi.movie_id
        WHERE w.user_id = %s
        ORDER BY wi.watched_status, m.title
    """, [user_id])


def add_to_watchlist(user_id, movie_id):
    # Get or create default watchlist
    wl = query("SELECT watchlist_id FROM Watchlist WHERE user_id = %s LIMIT 1", [user_id])
    if not wl:
        wl = execute_returning(
            "INSERT INTO Watchlist (user_id, name) VALUES (%s, 'My Watchlist') RETURNING watchlist_id",
            [user_id]
        )
    wl_id = wl[0]["watchlist_id"]
    execute("""
        INSERT INTO WatchlistItem (watchlist_id, movie_id, watched_status)
        VALUES (%s, %s, 'unwatched')
        ON CONFLICT (watchlist_id, movie_id) DO NOTHING
    """, [wl_id, movie_id])


def update_watchlist_status(watchlist_id, movie_id, status):
    execute("""
        UPDATE WatchlistItem SET watched_status = %s
        WHERE watchlist_id = %s AND movie_id = %s
    """, [status, watchlist_id, movie_id])


def remove_from_watchlist(watchlist_id, movie_id):
    execute("DELETE FROM WatchlistItem WHERE watchlist_id = %s AND movie_id = %s",
            [watchlist_id, movie_id])


def submit_rating(user_id, movie_id, rating):
    execute("""
        INSERT INTO UserRating (user_id, movie_id, rating, rating_date)
        VALUES (%s, %s, %s, CURRENT_DATE)
        ON CONFLICT (user_id, movie_id) DO UPDATE SET rating = EXCLUDED.rating, rating_date = CURRENT_DATE
    """, [user_id, movie_id, rating])


def submit_review(user_id, movie_id, text, sentiment):
    execute("""
        INSERT INTO Review (user_id, movie_id, review_text, sentiment, review_date)
        VALUES (%s, %s, %s, %s, CURRENT_DATE)
        ON CONFLICT (user_id, movie_id) DO UPDATE SET review_text = EXCLUDED.review_text, sentiment = EXCLUDED.sentiment
    """, [user_id, movie_id, text, sentiment])


def get_group_watch_parties():
    return query("""
        SELECT wp.party_id, wp.party_name, wp.planned_date, u.username as host_name,
               COUNT(wpm.user_id) as member_count
        FROM WatchParty wp
        JOIN UserProfile u ON u.user_id = wp.host_user_id
        LEFT JOIN WatchPartyMember wpm ON wpm.party_id = wp.party_id
        GROUP BY wp.party_id, wp.party_name, wp.planned_date, u.username
        ORDER BY wp.party_id
    """)


def get_group_recommendation(party_id, limit=10):
    return query("""
        SELECT m.movie_id, m.title, m.release_year, m.imdb_rating, m.genres_raw,
               m.poster_url, ROUND(AVG(all_r.rating), 2) AS avg_community_rating,
               COUNT(DISTINCT all_r.user_id) AS times_rated,
               STRING_AGG(DISTINCT g.genre_name, ', ' ORDER BY g.genre_name) AS genres
        FROM Movie m
        JOIN UserRating all_r ON all_r.movie_id = m.movie_id
        JOIN MovieGenre mg ON mg.movie_id = m.movie_id
        JOIN Genre g ON g.genre_id = mg.genre_id
        WHERE NOT EXISTS (
            SELECT 1 FROM WatchPartyMember wpm
            JOIN UserRating ur_seen ON ur_seen.user_id = wpm.user_id AND ur_seen.movie_id = m.movie_id
            WHERE wpm.party_id = %s
        )
        GROUP BY m.movie_id
        HAVING COUNT(DISTINCT all_r.user_id) >= 3
        ORDER BY avg_community_rating DESC
        LIMIT %s
    """, [party_id, limit])


# ── Insight Queries (the 10 complex queries) ─────────────────────────────────

INSIGHT_QUERIES = {
    1: {
        "title": "Top-Rated Movies by Genre",
        "description": "Highest-rated movies within each genre with minimum 5 user ratings",
        "sql": """
            SELECT g.genre_name, m.title, m.release_year,
                   ROUND(AVG(ur.rating), 2) AS avg_user_rating,
                   COUNT(ur.user_id) AS num_ratings,
                   RANK() OVER (PARTITION BY g.genre_name ORDER BY AVG(ur.rating) DESC) AS genre_rank
            FROM Movie m
            JOIN MovieGenre mg ON mg.movie_id = m.movie_id
            JOIN Genre g ON g.genre_id = mg.genre_id
            JOIN UserRating ur ON ur.movie_id = m.movie_id
            GROUP BY g.genre_name, m.movie_id, m.title, m.release_year
            HAVING COUNT(ur.user_id) >= 5
            ORDER BY g.genre_name, genre_rank
            LIMIT 50
        """
    },
    2: {
        "title": "Actor-Director Collaborations",
        "description": "Most frequent actor-director partnerships across multiple films",
        "sql": """
            SELECT p_actor.name AS actor_name, p_director.name AS director_name,
                   COUNT(DISTINCT m.movie_id) AS movies_together,
                   STRING_AGG(DISTINCT m.title, '; ' ORDER BY m.title) AS shared_movies
            FROM MovieCredit mc_actor
            JOIN RoleType rt_actor ON rt_actor.role_type_id = mc_actor.role_type_id AND rt_actor.role_name = 'Actor'
            JOIN Person p_actor ON p_actor.person_id = mc_actor.person_id
            JOIN MovieCredit mc_director ON mc_director.movie_id = mc_actor.movie_id
            JOIN RoleType rt_director ON rt_director.role_type_id = mc_director.role_type_id AND rt_director.role_name = 'Director'
            JOIN Person p_director ON p_director.person_id = mc_director.person_id
            JOIN Movie m ON m.movie_id = mc_actor.movie_id
            GROUP BY p_actor.name, p_director.name
            HAVING COUNT(DISTINCT m.movie_id) >= 2
            ORDER BY movies_together DESC, actor_name LIMIT 30
        """
    },
    3: {
        "title": "Audience vs Critic Score Gap",
        "description": "Movies where user ratings significantly differ from IMDb critic scores",
        "sql": """
            SELECT m.title, m.release_year, ROUND(AVG(ur.rating), 2) AS avg_user_rating,
                   er.score AS imdb_score,
                   ROUND(AVG(ur.rating) - er.score, 2) AS gap,
                   CASE WHEN AVG(ur.rating) - er.score > 1.0 THEN 'Audience Favorite'
                        WHEN er.score - AVG(ur.rating) > 1.0 THEN 'Critic Favorite'
                        ELSE 'Consensus' END AS category
            FROM Movie m
            JOIN UserRating ur ON ur.movie_id = m.movie_id
            JOIN ExternalRating er ON er.movie_id = m.movie_id AND er.source_name = 'IMDb'
            GROUP BY m.movie_id, m.title, m.release_year, er.score
            HAVING COUNT(ur.user_id) >= 3
            ORDER BY ABS(AVG(ur.rating) - er.score) DESC LIMIT 25
        """
    },
    4: {
        "title": "Mood-Based Recommendations",
        "description": "Explainable recommendations based on tag matching for user 1",
        "sql": """
            SELECT m.movie_id, m.title, m.release_year, m.imdb_rating,
                   ROUND(SUM(mtr.relevance_score), 3) AS recommendation_score,
                   STRING_AGG(DISTINCT t.tag_name, ', ' ORDER BY t.tag_name) AS matching_tags
            FROM MovieTagRelevance mtr
            JOIN Tag t ON t.tag_id = mtr.tag_id
            JOIN Movie m ON m.movie_id = mtr.movie_id
            LEFT JOIN UserRating ur ON ur.movie_id = m.movie_id AND ur.user_id = 1
            WHERE mtr.relevance_score >= 0.5 AND ur.user_id IS NULL
              AND t.tag_name IN (
                  SELECT DISTINCT t2.tag_name FROM UserRating ur2
                  JOIN MovieTagRelevance mtr2 ON mtr2.movie_id = ur2.movie_id
                  JOIN Tag t2 ON t2.tag_id = mtr2.tag_id
                  WHERE ur2.user_id = 1 AND ur2.rating >= 8.0 AND mtr2.relevance_score >= 0.6)
            GROUP BY m.movie_id, m.title, m.release_year, m.imdb_rating
            ORDER BY recommendation_score DESC LIMIT 15
        """
    },
    5: {
        "title": "Hidden Gems",
        "description": "Highly rated movies with relatively few total votes",
        "sql": """
            SELECT m.title, m.release_year, ROUND(AVG(ur.rating), 2) AS avg_user_rating,
                   COUNT(ur.user_id) AS num_ratings, m.imdb_votes, m.imdb_rating
            FROM Movie m JOIN UserRating ur ON ur.movie_id = m.movie_id
            WHERE m.imdb_votes < (SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY imdb_votes) FROM Movie)
            GROUP BY m.movie_id, m.title, m.release_year, m.imdb_votes, m.imdb_rating
            HAVING COUNT(ur.user_id) >= 3 AND AVG(ur.rating) >= 7.5
            ORDER BY avg_user_rating DESC LIMIT 20
        """
    },
    6: {
        "title": "Most Versatile Actors",
        "description": "Actors with the widest genre range across their filmography",
        "sql": """
            SELECT p.name AS actor_name, COUNT(DISTINCT g.genre_id) AS genre_count,
                   STRING_AGG(DISTINCT g.genre_name, ', ' ORDER BY g.genre_name) AS genres,
                   COUNT(DISTINCT mc.movie_id) AS total_movies
            FROM Person p
            JOIN MovieCredit mc ON mc.person_id = p.person_id
            JOIN RoleType rt ON rt.role_type_id = mc.role_type_id AND rt.role_name = 'Actor'
            JOIN MovieGenre mg ON mg.movie_id = mc.movie_id
            JOIN Genre g ON g.genre_id = mg.genre_id
            GROUP BY p.person_id, p.name
            HAVING COUNT(DISTINCT mc.movie_id) >= 3
            ORDER BY genre_count DESC, total_movies DESC LIMIT 20
        """
    },
    7: {
        "title": "Most Profitable Directors",
        "description": "Directors ranked by total profit and ROI of their films",
        "sql": """
            SELECT p.name AS director_name, COUNT(DISTINCT m.movie_id) AS num_films,
                   ROUND(SUM(m.revenue)::NUMERIC / 1000000, 1) AS revenue_M,
                   ROUND(SUM(m.budget)::NUMERIC / 1000000, 1) AS budget_M,
                   ROUND((SUM(m.revenue) - SUM(m.budget))::NUMERIC / 1000000, 1) AS profit_M
            FROM Person p
            JOIN MovieCredit mc ON mc.person_id = p.person_id
            JOIN RoleType rt ON rt.role_type_id = mc.role_type_id AND rt.role_name = 'Director'
            JOIN Movie m ON m.movie_id = mc.movie_id
            WHERE m.budget > 0 AND m.revenue > 0
            GROUP BY p.person_id, p.name HAVING COUNT(DISTINCT m.movie_id) >= 2
            ORDER BY profit_M DESC NULLS LAST LIMIT 20
        """
    },
    8: {
        "title": "Streaming Availability Search",
        "description": "Action/Sci-Fi/Thriller movies on major platforms via subscription",
        "sql": """
            SELECT DISTINCT m.title, m.release_year, m.imdb_rating, g.genre_name,
                   sp.name AS platform, ma.access_type
            FROM Movie m
            JOIN MovieAvailability ma ON ma.movie_id = m.movie_id
            JOIN StreamingPlatform sp ON sp.platform_id = ma.platform_id
            JOIN MovieGenre mg ON mg.movie_id = m.movie_id
            JOIN Genre g ON g.genre_id = mg.genre_id
            WHERE g.genre_name IN ('Action', 'Sci-Fi', 'Thriller')
              AND ma.access_type = 'subscription'
            ORDER BY m.imdb_rating DESC NULLS LAST LIMIT 30
        """
    },
    9: {
        "title": "Award Winners on Streaming",
        "description": "Award-winning films currently available for streaming",
        "sql": """
            SELECT m.title, m.release_year, m.imdb_rating,
                   STRING_AGG(DISTINCT a.award_name || ' - ' || a.category, '; ') AS awards_won,
                   COUNT(DISTINCT ma2.award_id) AS total_wins,
                   STRING_AGG(DISTINCT sp.name, ', ') AS available_on
            FROM Movie m
            JOIN MovieAward ma2 ON ma2.movie_id = m.movie_id AND ma2.result = 'won'
            JOIN Award a ON a.award_id = ma2.award_id
            JOIN MovieAvailability ma ON ma.movie_id = m.movie_id
            JOIN StreamingPlatform sp ON sp.platform_id = ma.platform_id
            WHERE ma.access_type = 'subscription'
            GROUP BY m.movie_id, m.title, m.release_year, m.imdb_rating
            HAVING COUNT(DISTINCT ma2.award_id) >= 1
            ORDER BY total_wins DESC, m.imdb_rating DESC NULLS LAST LIMIT 20
        """
    },
    10: {
        "title": "Group-Watch Recommendation",
        "description": "Best movies for watch party #1 excluding already-seen titles",
        "sql": """
            SELECT m.title, m.release_year, m.imdb_rating,
                   ROUND(AVG(all_r.rating), 2) AS avg_community_rating,
                   COUNT(DISTINCT all_r.user_id) AS times_rated,
                   STRING_AGG(DISTINCT g.genre_name, ', ' ORDER BY g.genre_name) AS genres
            FROM Movie m
            JOIN UserRating all_r ON all_r.movie_id = m.movie_id
            JOIN MovieGenre mg ON mg.movie_id = m.movie_id
            JOIN Genre g ON g.genre_id = mg.genre_id
            WHERE NOT EXISTS (
                SELECT 1 FROM WatchPartyMember wpm
                JOIN UserRating ur_seen ON ur_seen.user_id = wpm.user_id AND ur_seen.movie_id = m.movie_id
                WHERE wpm.party_id = 1
            )
            GROUP BY m.movie_id, m.title, m.release_year, m.imdb_rating
            HAVING COUNT(DISTINCT all_r.user_id) >= 3
            ORDER BY avg_community_rating DESC LIMIT 10
        """
    },
}


def get_insight(query_id):
    q = INSIGHT_QUERIES.get(query_id)
    if not q:
        return None
    results = query(q["sql"])
    return {"title": q["title"], "description": q["description"], "results": results}

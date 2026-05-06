-- ============================================================================
-- CineVerse: 10 Complex SQL Queries
-- ISE 503: Data Management - Spring 2026
--
-- Script: 03_complex_queries.sql
-- Purpose: Demonstrate advanced SQL with multi-table joins, aggregations,
--          subqueries, window functions, and analytical queries.
-- Database: PostgreSQL
-- ============================================================================


-- ============================================================================
-- Q1: Top-Rated Movies by Genre (with minimum vote threshold)
--
-- Business purpose: Find the highest-rated movies within each genre,
-- requiring at least 5 user ratings to qualify (avoids sampling bias).
-- Techniques: JOIN, GROUP BY, HAVING, AVG, RANK() window function
-- Tables: Movie, MovieGenre, Genre, UserRating
-- ============================================================================
SELECT
    g.genre_name,
    m.title,
    m.release_year,
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
LIMIT 50;


-- ============================================================================
-- Q2: Most Frequent Actor-Director Collaborations
--
-- Business purpose: Identify recurring creative partnerships — actors and
-- directors who have worked together on multiple films.
-- Techniques: Self-join on MovieCredit, COUNT, HAVING, STRING_AGG
-- Tables: MovieCredit (x2), RoleType (x2), Person (x2), Movie
-- ============================================================================
SELECT
    p_actor.name AS actor_name,
    p_director.name AS director_name,
    COUNT(DISTINCT m.movie_id) AS movies_together,
    STRING_AGG(DISTINCT m.title, '; ' ORDER BY m.title) AS shared_movies
FROM MovieCredit mc_actor
JOIN RoleType rt_actor ON rt_actor.role_type_id = mc_actor.role_type_id
    AND rt_actor.role_name = 'Actor'
JOIN Person p_actor ON p_actor.person_id = mc_actor.person_id
JOIN MovieCredit mc_director ON mc_director.movie_id = mc_actor.movie_id
JOIN RoleType rt_director ON rt_director.role_type_id = mc_director.role_type_id
    AND rt_director.role_name = 'Director'
JOIN Person p_director ON p_director.person_id = mc_director.person_id
JOIN Movie m ON m.movie_id = mc_actor.movie_id
GROUP BY p_actor.name, p_director.name
HAVING COUNT(DISTINCT m.movie_id) >= 2
ORDER BY movies_together DESC, actor_name
LIMIT 30;


-- ============================================================================
-- Q3: Audience-Loved but Critic-Disliked Movies (and vice versa)
--
-- Business purpose: Find movies where user ratings significantly diverge
-- from professional critic scores (IMDb external rating). Highlights
-- hidden gems loved by audiences or critic darlings ignored by viewers.
-- Techniques: JOIN, AVG, subquery, HAVING, CASE, absolute difference
-- Tables: Movie, UserRating, ExternalRating
-- ============================================================================
SELECT
    m.title,
    m.release_year,
    ROUND(AVG(ur.rating), 2) AS avg_user_rating,
    er.score AS imdb_score,
    ROUND(AVG(ur.rating) - er.score, 2) AS user_vs_critic_gap,
    COUNT(ur.user_id) AS num_user_ratings,
    CASE
        WHEN AVG(ur.rating) - er.score > 1.0 THEN 'Audience Favorite'
        WHEN er.score - AVG(ur.rating) > 1.0 THEN 'Critic Favorite'
        ELSE 'Consensus'
    END AS gap_category
FROM Movie m
JOIN UserRating ur ON ur.movie_id = m.movie_id
JOIN ExternalRating er ON er.movie_id = m.movie_id AND er.source_name = 'IMDb'
GROUP BY m.movie_id, m.title, m.release_year, er.score
HAVING COUNT(ur.user_id) >= 3
ORDER BY ABS(AVG(ur.rating) - er.score) DESC
LIMIT 25;


-- ============================================================================
-- Q4: Mood-Based Explainable Recommendation for a User
--
-- Business purpose: Recommend movies to a specific user based on their
-- preferred mood/theme tags, excluding movies they have already rated.
-- The recommendation explains WHY each movie matches via tag overlap.
-- Techniques: Multi-join, SUM, LEFT JOIN exclusion, STRING_AGG, LIMIT
-- Tables: UserPreferenceTag, Tag, MovieTagRelevance, Movie, UserRating
-- ============================================================================

-- First, generate user preferences from their rating history
-- (users who rate highly on certain genres/tags implicitly prefer those)
-- For demo, we'll use tag relevance directly:
SELECT
    m.movie_id,
    m.title,
    m.release_year,
    m.imdb_rating,
    ROUND(SUM(mtr.relevance_score), 3) AS recommendation_score,
    STRING_AGG(DISTINCT t.tag_name, ', ' ORDER BY t.tag_name) AS matching_tags,
    COUNT(DISTINCT t.tag_id) AS tag_match_count
FROM MovieTagRelevance mtr
JOIN Tag t ON t.tag_id = mtr.tag_id
JOIN Movie m ON m.movie_id = mtr.movie_id
LEFT JOIN UserRating ur ON ur.movie_id = m.movie_id AND ur.user_id = 1
WHERE mtr.relevance_score >= 0.5
  AND ur.user_id IS NULL  -- exclude already-rated movies
  AND t.tag_name IN (
      -- Get tags from movies user 1 rated highly
      SELECT DISTINCT t2.tag_name
      FROM UserRating ur2
      JOIN MovieTagRelevance mtr2 ON mtr2.movie_id = ur2.movie_id
      JOIN Tag t2 ON t2.tag_id = mtr2.tag_id
      WHERE ur2.user_id = 1 AND ur2.rating >= 8.0 AND mtr2.relevance_score >= 0.6
  )
GROUP BY m.movie_id, m.title, m.release_year, m.imdb_rating
ORDER BY recommendation_score DESC
LIMIT 15;


-- ============================================================================
-- Q5: Hidden Gems — High Rating, Low Popularity
--
-- Business purpose: Find movies that are highly rated by users but have
-- relatively few total votes (not mainstream blockbusters). Great for
-- discovery features.
-- Techniques: JOIN, AVG, COUNT, HAVING, subquery for percentile, ORDER BY
-- Tables: Movie, UserRating, ExternalRating
-- ============================================================================
SELECT
    m.title,
    m.release_year,
    ROUND(AVG(ur.rating), 2) AS avg_user_rating,
    COUNT(ur.user_id) AS num_ratings,
    m.imdb_votes,
    m.imdb_rating,
    ROUND(AVG(ur.rating) * LOG(COUNT(ur.user_id) + 1), 2) AS weighted_score
FROM Movie m
JOIN UserRating ur ON ur.movie_id = m.movie_id
WHERE m.imdb_votes < (SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY imdb_votes) FROM Movie)
GROUP BY m.movie_id, m.title, m.release_year, m.imdb_votes, m.imdb_rating
HAVING COUNT(ur.user_id) >= 3 AND AVG(ur.rating) >= 7.5
ORDER BY avg_user_rating DESC, num_ratings DESC
LIMIT 20;


-- ============================================================================
-- Q6: Actors with the Widest Genre Range
--
-- Business purpose: Identify the most versatile actors — those who have
-- performed across the greatest number of distinct genres.
-- Techniques: JOIN chain, COUNT DISTINCT, DENSE_RANK, STRING_AGG
-- Tables: Person, MovieCredit, RoleType, MovieGenre, Genre
-- ============================================================================
SELECT
    p.name AS actor_name,
    COUNT(DISTINCT g.genre_id) AS genre_count,
    STRING_AGG(DISTINCT g.genre_name, ', ' ORDER BY g.genre_name) AS genres,
    COUNT(DISTINCT mc.movie_id) AS total_movies,
    DENSE_RANK() OVER (ORDER BY COUNT(DISTINCT g.genre_id) DESC) AS versatility_rank
FROM Person p
JOIN MovieCredit mc ON mc.person_id = p.person_id
JOIN RoleType rt ON rt.role_type_id = mc.role_type_id AND rt.role_name = 'Actor'
JOIN MovieGenre mg ON mg.movie_id = mc.movie_id
JOIN Genre g ON g.genre_id = mg.genre_id
GROUP BY p.person_id, p.name
HAVING COUNT(DISTINCT mc.movie_id) >= 3
ORDER BY genre_count DESC, total_movies DESC
LIMIT 20;


-- ============================================================================
-- Q7: Most Profitable Directors (Return on Investment)
--
-- Business purpose: Rank directors by the total profit and ROI of their
-- films. Useful for industry analytics — which directors deliver
-- consistently profitable movies?
-- Techniques: JOIN, SUM, arithmetic expressions, CASE, NULLIF, filtering
-- Tables: Movie, MovieCredit, Person, RoleType
-- ============================================================================
SELECT
    p.name AS director_name,
    COUNT(DISTINCT m.movie_id) AS num_films,
    ROUND(SUM(m.revenue)::NUMERIC / 1000000, 1) AS total_revenue_millions,
    ROUND(SUM(m.budget)::NUMERIC / 1000000, 1) AS total_budget_millions,
    ROUND((SUM(m.revenue) - SUM(m.budget))::NUMERIC / 1000000, 1) AS total_profit_millions,
    ROUND(
        CASE
            WHEN SUM(m.budget) > 0
            THEN ((SUM(m.revenue) - SUM(m.budget))::NUMERIC / NULLIF(SUM(m.budget), 0)) * 100
            ELSE NULL
        END, 1
    ) AS roi_percent
FROM Person p
JOIN MovieCredit mc ON mc.person_id = p.person_id
JOIN RoleType rt ON rt.role_type_id = mc.role_type_id AND rt.role_name = 'Director'
JOIN Movie m ON m.movie_id = mc.movie_id
WHERE m.budget > 0 AND m.revenue > 0
GROUP BY p.person_id, p.name
HAVING COUNT(DISTINCT m.movie_id) >= 2
ORDER BY total_profit_millions DESC NULLS LAST
LIMIT 20;


-- ============================================================================
-- Q8: Streaming Availability Search — Find Movies by Region, Platform, Genre
--
-- Business purpose: A user wants to find Action movies available on Netflix
-- or Disney+ in the US via subscription. This simulates a real streaming
-- search feature.
-- Techniques: Multi-table JOIN, WHERE with IN, AND filters
-- Tables: Movie, MovieAvailability, StreamingPlatform, MovieGenre, Genre
-- ============================================================================
SELECT DISTINCT
    m.title,
    m.release_year,
    m.imdb_rating,
    g.genre_name,
    sp.name AS platform_name,
    ma.access_type,
    ma.region
FROM Movie m
JOIN MovieAvailability ma ON ma.movie_id = m.movie_id
JOIN StreamingPlatform sp ON sp.platform_id = ma.platform_id
JOIN MovieGenre mg ON mg.movie_id = m.movie_id
JOIN Genre g ON g.genre_id = mg.genre_id
WHERE g.genre_name IN ('Action', 'Sci-Fi', 'Thriller')
  AND sp.name IN ('Netflix', 'Disney+', 'Max (HBO)')
  AND ma.region = 'US'
  AND ma.access_type = 'subscription'
ORDER BY m.imdb_rating DESC NULLS LAST, m.title
LIMIT 30;


-- ============================================================================
-- Q9: Award-Winning Movies Currently Available on Streaming
--
-- Business purpose: Find prestige/award-winning films that users can watch
-- right now on a streaming platform. Combines awards data with availability.
-- Techniques: 5-table JOIN, WHERE filters, aggregate STRING_AGG
-- Tables: Movie, MovieAward, Award, MovieAvailability, StreamingPlatform
-- ============================================================================
SELECT
    m.title,
    m.release_year,
    m.imdb_rating,
    STRING_AGG(DISTINCT a.award_name || ' - ' || a.category, '; ') AS awards_won,
    COUNT(DISTINCT ma2.award_id) AS total_wins,
    STRING_AGG(DISTINCT sp.name, ', ') AS available_on
FROM Movie m
JOIN MovieAward ma2 ON ma2.movie_id = m.movie_id AND ma2.result = 'won'
JOIN Award a ON a.award_id = ma2.award_id
JOIN MovieAvailability ma ON ma.movie_id = m.movie_id
JOIN StreamingPlatform sp ON sp.platform_id = ma.platform_id
WHERE ma.region = 'US'
  AND ma.access_type = 'subscription'
  AND (ma.end_date IS NULL OR ma.end_date >= CURRENT_DATE)
GROUP BY m.movie_id, m.title, m.release_year, m.imdb_rating
HAVING COUNT(DISTINCT ma2.award_id) >= 1
ORDER BY total_wins DESC, m.imdb_rating DESC NULLS LAST
LIMIT 20;


-- ============================================================================
-- Q10: Group-Watch Recommendation (Watch Party)
--
-- Business purpose: For a watch party, recommend movies that the group
-- members have not yet watched but that score highly based on the
-- combined preferences (ratings) of all group members. Excludes movies
-- any member has already rated.
-- Techniques: Complex multi-join, NOT EXISTS, aggregation, subquery
-- Tables: WatchParty, WatchPartyMember, UserRating, Movie, MovieGenre, Genre
-- ============================================================================
SELECT
    m.title,
    m.release_year,
    m.imdb_rating,
    ROUND(AVG(all_ratings.rating), 2) AS avg_community_rating,
    COUNT(DISTINCT all_ratings.user_id) AS times_rated,
    STRING_AGG(DISTINCT g.genre_name, ', ' ORDER BY g.genre_name) AS genres
FROM Movie m
JOIN UserRating all_ratings ON all_ratings.movie_id = m.movie_id
JOIN MovieGenre mg ON mg.movie_id = m.movie_id
JOIN Genre g ON g.genre_id = mg.genre_id
WHERE NOT EXISTS (
    -- Exclude movies any party member has already rated
    SELECT 1
    FROM WatchPartyMember wpm
    JOIN UserRating ur_seen ON ur_seen.user_id = wpm.user_id
        AND ur_seen.movie_id = m.movie_id
    WHERE wpm.party_id = 1  -- Party ID 1: "Weekend Movie Night"
)
AND m.movie_id IN (
    -- Only consider movies in genres the party members tend to rate highly
    SELECT DISTINCT mg2.movie_id
    FROM WatchPartyMember wpm2
    JOIN UserRating ur2 ON ur2.user_id = wpm2.user_id AND ur2.rating >= 7.0
    JOIN MovieGenre mg2 ON mg2.movie_id = ur2.movie_id
    WHERE wpm2.party_id = 1
)
GROUP BY m.movie_id, m.title, m.release_year, m.imdb_rating
HAVING COUNT(DISTINCT all_ratings.user_id) >= 3
ORDER BY avg_community_rating DESC
LIMIT 10;


-- ============================================================================
-- End of complex queries.
-- Each query demonstrates multi-table joins and at least one advanced SQL
-- technique (window functions, subqueries, aggregations, STRING_AGG, etc.)
-- ============================================================================

-- recommend movies for watch party 1 that no member has seen,
-- filtered to genres the group tends to rate highly
SELECT
    m.title,
    m.release_year,
    m.imdb_rating,
    ROUND(AVG(all_ratings.rating)::numeric, 2) AS avg_community_rating,
    COUNT(DISTINCT all_ratings.user_id) AS times_rated,
    STRING_AGG(DISTINCT g.genre_name, ', ' ORDER BY g.genre_name) AS genres
FROM Movie m
JOIN UserRating all_ratings ON all_ratings.movie_id = m.movie_id
JOIN MovieGenre mg ON mg.movie_id = m.movie_id
JOIN Genre g ON g.genre_id = mg.genre_id
WHERE NOT EXISTS (
    -- exclude movies any party member has already rated
    SELECT 1
    FROM WatchPartyMember wpm
    JOIN UserRating ur_seen ON ur_seen.user_id = wpm.user_id
        AND ur_seen.movie_id = m.movie_id
    WHERE wpm.party_id = 1
)
AND m.movie_id IN (
    -- only genres the group rates well
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

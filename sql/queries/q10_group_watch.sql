-- movies no watch party member has seen, ranked by community rating
SELECT
    m.title,
    m.release_year,
    m.imdb_rating,
    ROUND(AVG(ur.rating)::numeric, 2) AS avg_user_rating,
    COUNT(DISTINCT ur.user_id) AS times_rated,
    STRING_AGG(DISTINCT g.genre_name, ', ' ORDER BY g.genre_name) AS genres
FROM Movie m
JOIN UserRating ur ON ur.movie_id = m.movie_id
JOIN MovieGenre mg ON mg.movie_id = m.movie_id
JOIN Genre g ON g.genre_id = mg.genre_id
WHERE NOT EXISTS (
    SELECT 1 FROM WatchPartyMember wpm
    JOIN UserRating seen ON seen.user_id = wpm.user_id AND seen.movie_id = m.movie_id
    WHERE wpm.party_id = 1
)
GROUP BY m.movie_id, m.title, m.release_year, m.imdb_rating
HAVING COUNT(DISTINCT ur.user_id) >= 3
ORDER BY avg_user_rating DESC
LIMIT 10;

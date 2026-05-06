-- high-rated movies with below-median vote counts (hidden gems)
SELECT
    m.title,
    m.release_year,
    ROUND(AVG(ur.rating)::numeric, 2) AS avg_user_rating,
    COUNT(ur.user_id) AS num_ratings,
    m.imdb_votes,
    m.imdb_rating,
    ROUND((AVG(ur.rating) * LOG(COUNT(ur.user_id) + 1))::numeric, 2) AS weighted_score
FROM Movie m
JOIN UserRating ur ON ur.movie_id = m.movie_id
WHERE m.imdb_votes < (SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY imdb_votes) FROM Movie)
GROUP BY m.movie_id, m.title, m.release_year, m.imdb_votes, m.imdb_rating
HAVING COUNT(ur.user_id) >= 3 AND AVG(ur.rating) >= 7.5
ORDER BY avg_user_rating DESC, num_ratings DESC
LIMIT 20;

-- directors ranked by average IMDb rating and total audience reach
-- (uses imdb_rating and imdb_votes since budget/revenue require TMDb enrichment)
SELECT
    p.name AS director_name,
    COUNT(DISTINCT m.movie_id) AS num_films,
    ROUND(AVG(m.imdb_rating)::numeric, 2) AS avg_imdb_rating,
    SUM(m.imdb_votes) AS total_votes,
    ROUND(AVG(ur.rating)::numeric, 2) AS avg_user_rating,
    COUNT(DISTINCT ur.user_id) AS unique_raters,
    STRING_AGG(DISTINCT m.title, '; ' ORDER BY m.title) AS films
FROM Person p
JOIN MovieCredit mc ON mc.person_id = p.person_id
JOIN RoleType rt ON rt.role_type_id = mc.role_type_id AND rt.role_name = 'Director'
JOIN Movie m ON m.movie_id = mc.movie_id
LEFT JOIN UserRating ur ON ur.movie_id = m.movie_id
WHERE m.imdb_rating IS NOT NULL
GROUP BY p.person_id, p.name
HAVING COUNT(DISTINCT m.movie_id) >= 3
ORDER BY avg_imdb_rating DESC, total_votes DESC
LIMIT 20;

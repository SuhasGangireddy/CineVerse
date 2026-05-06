-- movies where user ratings diverge significantly from IMDb critic scores
SELECT
    m.title,
    m.release_year,
    ROUND(AVG(ur.rating)::numeric, 2) AS avg_user_rating,
    er.score AS imdb_score,
    ROUND((AVG(ur.rating) - er.score)::numeric, 2) AS user_vs_critic_gap,
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

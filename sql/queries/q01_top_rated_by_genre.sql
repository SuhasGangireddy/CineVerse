-- top 3 rated movies per genre, requires at least 5 user ratings to qualify
SELECT genre_name, title, release_year, avg_user_rating, num_ratings, genre_rank
FROM (
    SELECT
        g.genre_name,
        m.title,
        m.release_year,
        ROUND(AVG(ur.rating)::numeric, 2) AS avg_user_rating,
        COUNT(ur.user_id) AS num_ratings,
        RANK() OVER (PARTITION BY g.genre_name ORDER BY AVG(ur.rating) DESC) AS genre_rank
    FROM Movie m
    JOIN MovieGenre mg ON mg.movie_id = m.movie_id
    JOIN Genre g ON g.genre_id = mg.genre_id
    JOIN UserRating ur ON ur.movie_id = m.movie_id
    GROUP BY g.genre_name, m.movie_id, m.title, m.release_year
    HAVING COUNT(ur.user_id) >= 5
) ranked
WHERE genre_rank <= 3
ORDER BY genre_name, genre_rank;

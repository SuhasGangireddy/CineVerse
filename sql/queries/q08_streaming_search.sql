-- find action/sci-fi/thriller movies on Netflix, Disney+, or Max via subscription in the US
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

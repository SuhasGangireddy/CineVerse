-- award-winning movies currently available to stream in the US
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

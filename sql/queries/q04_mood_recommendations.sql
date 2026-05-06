-- recommend movies to user 1 based on tags from their highly-rated movies,
-- excluding anything they've already rated
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
      -- get tags from movies user 1 rated highly
      SELECT DISTINCT t2.tag_name
      FROM UserRating ur2
      JOIN MovieTagRelevance mtr2 ON mtr2.movie_id = ur2.movie_id
      JOIN Tag t2 ON t2.tag_id = mtr2.tag_id
      WHERE ur2.user_id = 1 AND ur2.rating >= 8.0 AND mtr2.relevance_score >= 0.6
  )
GROUP BY m.movie_id, m.title, m.release_year, m.imdb_rating
ORDER BY recommendation_score DESC
LIMIT 15;

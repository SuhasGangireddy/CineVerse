-- actors who have appeared in the most distinct genres
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

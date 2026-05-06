-- actors and directors who have worked together on 2+ films
SELECT
    p_actor.name AS actor_name,
    p_director.name AS director_name,
    COUNT(DISTINCT m.movie_id) AS movies_together,
    STRING_AGG(DISTINCT m.title, '; ' ORDER BY m.title) AS shared_movies
FROM MovieCredit mc_actor
JOIN RoleType rt_actor ON rt_actor.role_type_id = mc_actor.role_type_id
    AND rt_actor.role_name = 'Actor'
JOIN Person p_actor ON p_actor.person_id = mc_actor.person_id
JOIN MovieCredit mc_director ON mc_director.movie_id = mc_actor.movie_id
JOIN RoleType rt_director ON rt_director.role_type_id = mc_director.role_type_id
    AND rt_director.role_name = 'Director'
JOIN Person p_director ON p_director.person_id = mc_director.person_id
JOIN Movie m ON m.movie_id = mc_actor.movie_id
GROUP BY p_actor.name, p_director.name
HAVING COUNT(DISTINCT m.movie_id) >= 2
ORDER BY movies_together DESC, actor_name
LIMIT 30;

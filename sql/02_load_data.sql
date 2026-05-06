-- Load Movie
\copy Movie(movie_id, imdb_id, tmdb_id, title, release_year, runtime_minutes, language, country, plot, budget, revenue, imdb_rating, imdb_votes, genres_raw) FROM 'data_clean/movies.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load Person
\copy Person(person_id, imdb_person_id, name, birth_year, death_year, primary_profession) FROM 'data_clean/people.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load RoleType
\copy RoleType(role_type_id, role_name) FROM 'data_clean/role_types.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load MovieCredit
\copy MovieCredit(credit_id, movie_id, person_id, role_type_id, character_name, billing_order) FROM 'data_clean/movie_credits.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load Genre
\copy Genre(genre_id, genre_name) FROM 'data_clean/genres.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load MovieGenre
\copy MovieGenre(movie_id, genre_id) FROM 'data_clean/movie_genres.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load Distributor
\copy Distributor(distributor_id, name, address, country) FROM 'data_clean/distributors.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load MovieDistributor
\copy MovieDistributor(movie_id, distributor_id, region) FROM 'data_clean/movie_distributors.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load UserProfile
\copy UserProfile(user_id, username, email, age_group, preferred_language) FROM 'data_clean/users.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load UserRating
\copy UserRating(user_id, movie_id, rating, rating_date) FROM 'data_clean/user_ratings.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load ExternalRating
\copy ExternalRating(movie_id, source_name, score, max_score, vote_count) FROM 'data_clean/external_ratings.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load Tag
\copy Tag(tag_id, tag_name) FROM 'data_clean/tags.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load MovieTagRelevance
\copy MovieTagRelevance(movie_id, tag_id, relevance_score) FROM 'data_clean/movie_tag_relevance.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load StreamingPlatform
\copy StreamingPlatform(platform_id, name, country, website_url) FROM 'data_clean/streaming_platforms.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load MovieAvailability
\copy MovieAvailability(movie_id, platform_id, region, access_type, start_date, end_date) FROM 'data_clean/movie_availability.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load Award
\copy Award(award_id, award_name, category) FROM 'data_clean/awards.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load MovieAward
\copy MovieAward(movie_award_id, movie_id, award_id, person_id, award_year, result) FROM 'data_clean/movie_awards.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load ProductionCompany
\copy ProductionCompany(company_id, name, country, founded_year) FROM 'data_clean/production_companies.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load MovieProductionCompany
\copy MovieProductionCompany(movie_id, company_id) FROM 'data_clean/movie_production_companies.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load Watchlist
\copy Watchlist(watchlist_id, user_id, name) FROM 'data_clean/watchlists.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load WatchlistItem
\copy WatchlistItem(watchlist_id, movie_id, watched_status) FROM 'data_clean/watchlist_items.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load WatchParty
\copy WatchParty(party_id, host_user_id, party_name, planned_date) FROM 'data_clean/watch_parties.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load WatchPartyMember
\copy WatchPartyMember(party_id, user_id) FROM 'data_clean/watch_party_members.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Load WatchPartySuggestion
\copy WatchPartySuggestion(party_id, movie_id, group_score, suggested_by) FROM 'data_clean/watch_party_suggestions.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Reset sequences to max ID + 1
SELECT setval('movie_movie_id_seq', COALESCE((SELECT MAX(movie_id) FROM Movie), 0) + 1, false);
SELECT setval('person_person_id_seq', COALESCE((SELECT MAX(person_id) FROM Person), 0) + 1, false);
SELECT setval('roletype_role_type_id_seq', COALESCE((SELECT MAX(role_type_id) FROM RoleType), 0) + 1, false);
SELECT setval('moviecredit_credit_id_seq', COALESCE((SELECT MAX(credit_id) FROM MovieCredit), 0) + 1, false);
SELECT setval('genre_genre_id_seq', COALESCE((SELECT MAX(genre_id) FROM Genre), 0) + 1, false);
SELECT setval('distributor_distributor_id_seq', COALESCE((SELECT MAX(distributor_id) FROM Distributor), 0) + 1, false);
SELECT setval('userprofile_user_id_seq', COALESCE((SELECT MAX(user_id) FROM UserProfile), 0) + 1, false);
SELECT setval('review_review_id_seq', COALESCE((SELECT MAX(review_id) FROM Review), 0) + 1, false);
SELECT setval('tag_tag_id_seq', COALESCE((SELECT MAX(tag_id) FROM Tag), 0) + 1, false);
SELECT setval('recommendationlog_recommendation_id_seq', COALESCE((SELECT MAX(recommendation_id) FROM RecommendationLog), 0) + 1, false);
SELECT setval('streamingplatform_platform_id_seq', COALESCE((SELECT MAX(platform_id) FROM StreamingPlatform), 0) + 1, false);
SELECT setval('award_award_id_seq', COALESCE((SELECT MAX(award_id) FROM Award), 0) + 1, false);
SELECT setval('movieaward_movie_award_id_seq', COALESCE((SELECT MAX(movie_award_id) FROM MovieAward), 0) + 1, false);
SELECT setval('productioncompany_company_id_seq', COALESCE((SELECT MAX(company_id) FROM ProductionCompany), 0) + 1, false);
SELECT setval('watchlist_watchlist_id_seq', COALESCE((SELECT MAX(watchlist_id) FROM Watchlist), 0) + 1, false);
SELECT setval('watchparty_party_id_seq', COALESCE((SELECT MAX(party_id) FROM WatchParty), 0) + 1, false);

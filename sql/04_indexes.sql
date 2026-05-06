-- performance indexes

-- movie search
CREATE INDEX IF NOT EXISTS idx_movie_title ON Movie(title);
CREATE INDEX IF NOT EXISTS idx_movie_release_year ON Movie(release_year);
CREATE INDEX IF NOT EXISTS idx_movie_imdb_rating ON Movie(imdb_rating);
CREATE INDEX IF NOT EXISTS idx_movie_language ON Movie(language);

-- person lookup
CREATE INDEX IF NOT EXISTS idx_person_name ON Person(name);
CREATE INDEX IF NOT EXISTS idx_person_profession ON Person(primary_profession);

-- credits (heavily joined)
CREATE INDEX IF NOT EXISTS idx_moviecredit_movie ON MovieCredit(movie_id);
CREATE INDEX IF NOT EXISTS idx_moviecredit_person ON MovieCredit(person_id);
CREATE INDEX IF NOT EXISTS idx_moviecredit_role ON MovieCredit(role_type_id);
CREATE INDEX IF NOT EXISTS idx_moviecredit_movie_role ON MovieCredit(movie_id, role_type_id);

-- genre joins
CREATE INDEX IF NOT EXISTS idx_moviegenre_genre ON MovieGenre(genre_id);

-- ratings
CREATE INDEX IF NOT EXISTS idx_userrating_movie ON UserRating(movie_id);
CREATE INDEX IF NOT EXISTS idx_userrating_user ON UserRating(user_id);
CREATE INDEX IF NOT EXISTS idx_userrating_rating ON UserRating(rating);

-- reviews
CREATE INDEX IF NOT EXISTS idx_review_movie ON Review(movie_id);
CREATE INDEX IF NOT EXISTS idx_review_user ON Review(user_id);

-- external ratings
CREATE INDEX IF NOT EXISTS idx_externalrating_source ON ExternalRating(source_name);

-- tag relevance
CREATE INDEX IF NOT EXISTS idx_movietagrel_tag ON MovieTagRelevance(tag_id);
CREATE INDEX IF NOT EXISTS idx_movietagrel_movie ON MovieTagRelevance(movie_id);
CREATE INDEX IF NOT EXISTS idx_movietagrel_score ON MovieTagRelevance(relevance_score);

-- streaming availability
CREATE INDEX IF NOT EXISTS idx_movieavail_platform ON MovieAvailability(platform_id);
CREATE INDEX IF NOT EXISTS idx_movieavail_region ON MovieAvailability(region);
CREATE INDEX IF NOT EXISTS idx_movieavail_access ON MovieAvailability(access_type);

-- awards
CREATE INDEX IF NOT EXISTS idx_movieaward_movie ON MovieAward(movie_id);
CREATE INDEX IF NOT EXISTS idx_movieaward_result ON MovieAward(result);

-- watchlists
CREATE INDEX IF NOT EXISTS idx_watchlist_user ON Watchlist(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlistitem_movie ON WatchlistItem(movie_id);
CREATE INDEX IF NOT EXISTS idx_watchlistitem_status ON WatchlistItem(watched_status);

-- watch parties
CREATE INDEX IF NOT EXISTS idx_watchparty_host ON WatchParty(host_user_id);
CREATE INDEX IF NOT EXISTS idx_watchpartymember_user ON WatchPartyMember(user_id);

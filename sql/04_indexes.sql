-- ============================================================================
-- CineVerse: Performance Indexes
-- ISE 503: Data Management - Spring 2026
--
-- Script: 04_indexes.sql
-- Purpose: Create indexes on commonly filtered/joined columns for performance.
-- ============================================================================

-- Movie search indexes
CREATE INDEX IF NOT EXISTS idx_movie_title ON Movie(title);
CREATE INDEX IF NOT EXISTS idx_movie_release_year ON Movie(release_year);
CREATE INDEX IF NOT EXISTS idx_movie_imdb_rating ON Movie(imdb_rating);
CREATE INDEX IF NOT EXISTS idx_movie_language ON Movie(language);

-- Person name search
CREATE INDEX IF NOT EXISTS idx_person_name ON Person(name);
CREATE INDEX IF NOT EXISTS idx_person_profession ON Person(primary_profession);

-- MovieCredit joins (most critical for query performance)
CREATE INDEX IF NOT EXISTS idx_moviecredit_movie ON MovieCredit(movie_id);
CREATE INDEX IF NOT EXISTS idx_moviecredit_person ON MovieCredit(person_id);
CREATE INDEX IF NOT EXISTS idx_moviecredit_role ON MovieCredit(role_type_id);
CREATE INDEX IF NOT EXISTS idx_moviecredit_movie_role ON MovieCredit(movie_id, role_type_id);

-- Genre joins
CREATE INDEX IF NOT EXISTS idx_moviegenre_genre ON MovieGenre(genre_id);

-- User ratings
CREATE INDEX IF NOT EXISTS idx_userrating_movie ON UserRating(movie_id);
CREATE INDEX IF NOT EXISTS idx_userrating_user ON UserRating(user_id);
CREATE INDEX IF NOT EXISTS idx_userrating_rating ON UserRating(rating);

-- Reviews
CREATE INDEX IF NOT EXISTS idx_review_movie ON Review(movie_id);
CREATE INDEX IF NOT EXISTS idx_review_user ON Review(user_id);

-- External ratings
CREATE INDEX IF NOT EXISTS idx_externalrating_source ON ExternalRating(source_name);

-- Tag relevance
CREATE INDEX IF NOT EXISTS idx_movietagrel_tag ON MovieTagRelevance(tag_id);
CREATE INDEX IF NOT EXISTS idx_movietagrel_movie ON MovieTagRelevance(movie_id);
CREATE INDEX IF NOT EXISTS idx_movietagrel_score ON MovieTagRelevance(relevance_score);

-- Streaming availability
CREATE INDEX IF NOT EXISTS idx_movieavail_platform ON MovieAvailability(platform_id);
CREATE INDEX IF NOT EXISTS idx_movieavail_region ON MovieAvailability(region);
CREATE INDEX IF NOT EXISTS idx_movieavail_access ON MovieAvailability(access_type);

-- Awards
CREATE INDEX IF NOT EXISTS idx_movieaward_movie ON MovieAward(movie_id);
CREATE INDEX IF NOT EXISTS idx_movieaward_result ON MovieAward(result);

-- Watchlist
CREATE INDEX IF NOT EXISTS idx_watchlist_user ON Watchlist(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlistitem_movie ON WatchlistItem(movie_id);
CREATE INDEX IF NOT EXISTS idx_watchlistitem_status ON WatchlistItem(watched_status);

-- Watch party
CREATE INDEX IF NOT EXISTS idx_watchparty_host ON WatchParty(host_user_id);
CREATE INDEX IF NOT EXISTS idx_watchpartymember_user ON WatchPartyMember(user_id);

-- ============================================================================
-- Indexes created. These support the complex queries in 03_complex_queries.sql
-- and the application's search/filter operations.
-- ============================================================================

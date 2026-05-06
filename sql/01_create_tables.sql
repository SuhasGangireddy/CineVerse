-- CineVerse: An IMDb/Netflix-Inspired Movie Database System

-- Drop tables if they exist
DROP TABLE IF EXISTS WatchPartySuggestion CASCADE;
DROP TABLE IF EXISTS WatchPartyMember CASCADE;
DROP TABLE IF EXISTS WatchParty CASCADE;
DROP TABLE IF EXISTS WatchlistItem CASCADE;
DROP TABLE IF EXISTS Watchlist CASCADE;
DROP TABLE IF EXISTS MovieAward CASCADE;
DROP TABLE IF EXISTS Award CASCADE;
DROP TABLE IF EXISTS MovieAvailability CASCADE;
DROP TABLE IF EXISTS StreamingPlatform CASCADE;
DROP TABLE IF EXISTS RecommendationLog CASCADE;
DROP TABLE IF EXISTS UserPreferenceTag CASCADE;
DROP TABLE IF EXISTS MovieTagRelevance CASCADE;
DROP TABLE IF EXISTS Tag CASCADE;
DROP TABLE IF EXISTS ExternalRating CASCADE;
DROP TABLE IF EXISTS Review CASCADE;
DROP TABLE IF EXISTS UserRating CASCADE;
DROP TABLE IF EXISTS UserProfile CASCADE;
DROP TABLE IF EXISTS MovieProductionCompany CASCADE;
DROP TABLE IF EXISTS ProductionCompany CASCADE;
DROP TABLE IF EXISTS MovieGenre CASCADE;
DROP TABLE IF EXISTS Genre CASCADE;
DROP TABLE IF EXISTS MovieCredit CASCADE;
DROP TABLE IF EXISTS RoleType CASCADE;
DROP TABLE IF EXISTS Person CASCADE;
DROP TABLE IF EXISTS MovieDistributor CASCADE;
DROP TABLE IF EXISTS Distributor CASCADE;
DROP TABLE IF EXISTS Movie CASCADE;

-- CORE TABLES

-- 1. Movie
CREATE TABLE Movie (
    movie_id        SERIAL PRIMARY KEY,
    imdb_id         VARCHAR(20) UNIQUE NOT NULL,
    tmdb_id         INTEGER,
    title           VARCHAR(255) NOT NULL,
    release_year    INTEGER CHECK (release_year >= 1888),
    release_date    DATE,
    runtime_minutes INTEGER CHECK (runtime_minutes > 0),
    language        VARCHAR(50) DEFAULT 'English',
    country         VARCHAR(100),
    plot            TEXT,
    budget          NUMERIC(14,2) CHECK (budget >= 0),
    revenue         NUMERIC(14,2) CHECK (revenue >= 0),
    imdb_rating     NUMERIC(3,1) CHECK (imdb_rating BETWEEN 0 AND 10),
    imdb_votes      INTEGER CHECK (imdb_votes >= 0),
    poster_url      TEXT,
    genres_raw      VARCHAR(255),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Person
CREATE TABLE Person (
    person_id          SERIAL PRIMARY KEY,
    imdb_person_id     VARCHAR(20) UNIQUE,
    name               VARCHAR(255) NOT NULL,
    birth_year         INTEGER,
    death_year         INTEGER,
    primary_profession VARCHAR(100),
    CONSTRAINT chk_person_years CHECK (death_year IS NULL OR death_year >= birth_year)
);

-- 3. RoleType
CREATE TABLE RoleType (
    role_type_id SERIAL PRIMARY KEY,
    role_name    VARCHAR(50) UNIQUE NOT NULL
);

-- 4. MovieCredit
CREATE TABLE MovieCredit (
    credit_id      SERIAL PRIMARY KEY,
    movie_id       INTEGER NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    person_id      INTEGER NOT NULL REFERENCES Person(person_id) ON DELETE CASCADE,
    role_type_id   INTEGER NOT NULL REFERENCES RoleType(role_type_id),
    character_name VARCHAR(255),
    billing_order  INTEGER CHECK (billing_order > 0),
    CONSTRAINT uq_movie_person_role_char UNIQUE (movie_id, person_id, role_type_id, character_name)
);

-- 5. Genre
CREATE TABLE Genre (
    genre_id   SERIAL PRIMARY KEY,
    genre_name VARCHAR(50) UNIQUE NOT NULL
);

-- 6. MovieGenre
CREATE TABLE MovieGenre (
    movie_id INTEGER NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    genre_id INTEGER NOT NULL REFERENCES Genre(genre_id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, genre_id)
);

-- 7. Distributor
CREATE TABLE Distributor (
    distributor_id SERIAL PRIMARY KEY,
    name           VARCHAR(255) NOT NULL,
    address        TEXT,
    country        VARCHAR(100)
);

-- 8. MovieDistributor
CREATE TABLE MovieDistributor (
    movie_id       INTEGER NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    distributor_id INTEGER NOT NULL REFERENCES Distributor(distributor_id) ON DELETE CASCADE,
    region         VARCHAR(100) DEFAULT 'Worldwide',
    PRIMARY KEY (movie_id, distributor_id, region)
);

-- USER, RATING, AND REVIEW TABLES

-- 9. UserProfile
CREATE TABLE UserProfile (
    user_id            SERIAL PRIMARY KEY,
    username           VARCHAR(100) UNIQUE NOT NULL,
    email              VARCHAR(255) UNIQUE,
    age_group          VARCHAR(20) CHECK (age_group IN ('under_18', '18-24', '25-34', '35-44', '45-54', '55+')),
    preferred_language VARCHAR(50) DEFAULT 'English',
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. UserRating
CREATE TABLE UserRating (
    user_id     INTEGER NOT NULL REFERENCES UserProfile(user_id) ON DELETE CASCADE,
    movie_id    INTEGER NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    rating      NUMERIC(3,1) NOT NULL CHECK (rating BETWEEN 0.0 AND 10.0),
    rating_date DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (user_id, movie_id)
);

-- 11. Review
CREATE TABLE Review (
    review_id   SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES UserProfile(user_id) ON DELETE CASCADE,
    movie_id    INTEGER NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    review_text TEXT NOT NULL,
    sentiment   VARCHAR(20) CHECK (sentiment IN ('positive', 'negative', 'neutral', 'mixed')),
    review_date DATE DEFAULT CURRENT_DATE,
    CONSTRAINT uq_user_movie_review UNIQUE (user_id, movie_id)
);

-- 12. ExternalRating
CREATE TABLE ExternalRating (
    movie_id    INTEGER NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    source_name VARCHAR(100) NOT NULL,
    score       NUMERIC(5,2) NOT NULL CHECK (score >= 0),
    max_score   NUMERIC(5,2) NOT NULL CHECK (max_score > 0),
    vote_count  INTEGER CHECK (vote_count >= 0),
    PRIMARY KEY (movie_id, source_name)
);

-- RECOMMENDATION AND MOOD TABLES

-- 13. Tag
CREATE TABLE Tag (
    tag_id   SERIAL PRIMARY KEY,
    tag_name VARCHAR(100) UNIQUE NOT NULL
);

-- 14. MovieTagRelevance
CREATE TABLE MovieTagRelevance (
    movie_id        INTEGER NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    tag_id          INTEGER NOT NULL REFERENCES Tag(tag_id) ON DELETE CASCADE,
    relevance_score NUMERIC(4,3) NOT NULL CHECK (relevance_score BETWEEN 0.0 AND 1.0),
    PRIMARY KEY (movie_id, tag_id)
);

-- 15. UserPreferenceTag
CREATE TABLE UserPreferenceTag (
    user_id           INTEGER NOT NULL REFERENCES UserProfile(user_id) ON DELETE CASCADE,
    tag_id            INTEGER NOT NULL REFERENCES Tag(tag_id) ON DELETE CASCADE,
    preference_weight NUMERIC(4,3) NOT NULL CHECK (preference_weight BETWEEN 0.0 AND 1.0),
    PRIMARY KEY (user_id, tag_id)
);

-- 16. RecommendationLog
CREATE TABLE RecommendationLog (
    recommendation_id SERIAL PRIMARY KEY,
    user_id           INTEGER NOT NULL REFERENCES UserProfile(user_id) ON DELETE CASCADE,
    movie_id          INTEGER NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    score             NUMERIC(6,3) NOT NULL,
    explanation       TEXT NOT NULL,
    generated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- STREAMING AVAILABILITY TABLES

-- 17. StreamingPlatform
CREATE TABLE StreamingPlatform (
    platform_id SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    country     VARCHAR(100),
    website_url TEXT,
    CONSTRAINT uq_platform_country UNIQUE (name, country)
);

-- 18. MovieAvailability
CREATE TABLE MovieAvailability (
    movie_id    INTEGER NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    platform_id INTEGER NOT NULL REFERENCES StreamingPlatform(platform_id) ON DELETE CASCADE,
    region      VARCHAR(50) NOT NULL DEFAULT 'US',
    access_type VARCHAR(20) NOT NULL CHECK (access_type IN ('subscription', 'rent', 'buy', 'free', 'theater')),
    start_date  DATE,
    end_date    DATE,
    PRIMARY KEY (movie_id, platform_id, region, access_type)
);

-- AWARDS TABLES

-- 19. Award
CREATE TABLE Award (
    award_id   SERIAL PRIMARY KEY,
    award_name VARCHAR(255) NOT NULL,
    category   VARCHAR(255) NOT NULL,
    CONSTRAINT uq_award_category UNIQUE (award_name, category)
);

-- 20. MovieAward
CREATE TABLE MovieAward (
    movie_award_id SERIAL PRIMARY KEY,
    movie_id       INTEGER NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    award_id       INTEGER NOT NULL REFERENCES Award(award_id) ON DELETE CASCADE,
    person_id      INTEGER REFERENCES Person(person_id) ON DELETE SET NULL,
    award_year     INTEGER NOT NULL CHECK (award_year >= 1900),
    result         VARCHAR(20) NOT NULL CHECK (result IN ('won', 'nominated')),
    CONSTRAINT uq_movie_award_year UNIQUE (movie_id, award_id, award_year)
);

-- PRODUCTION COMPANY TABLES

-- 21. ProductionCompany
CREATE TABLE ProductionCompany (
    company_id SERIAL PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    country    VARCHAR(100),
    founded_year INTEGER
);

-- 22. MovieProductionCompany
CREATE TABLE MovieProductionCompany (
    movie_id   INTEGER NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    company_id INTEGER NOT NULL REFERENCES ProductionCompany(company_id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, company_id)
);

-- WATCHLIST TABLES

-- 23. Watchlist
CREATE TABLE Watchlist (
    watchlist_id SERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES UserProfile(user_id) ON DELETE CASCADE,
    name         VARCHAR(100) NOT NULL DEFAULT 'My Watchlist',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_watchlist_name UNIQUE (user_id, name)
);

-- 24. WatchlistItem
CREATE TABLE WatchlistItem (
    watchlist_id    INTEGER NOT NULL REFERENCES Watchlist(watchlist_id) ON DELETE CASCADE,
    movie_id        INTEGER NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    added_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    watched_status  VARCHAR(20) DEFAULT 'unwatched' CHECK (watched_status IN ('unwatched', 'watching', 'watched')),
    PRIMARY KEY (watchlist_id, movie_id)
);

-- GROUP WATCH / WATCH PARTY TABLES

-- 25. WatchParty
CREATE TABLE WatchParty (
    party_id     SERIAL PRIMARY KEY,
    host_user_id INTEGER NOT NULL REFERENCES UserProfile(user_id) ON DELETE CASCADE,
    party_name   VARCHAR(255) NOT NULL,
    planned_date DATE,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 26. WatchPartyMember
CREATE TABLE WatchPartyMember (
    party_id INTEGER NOT NULL REFERENCES WatchParty(party_id) ON DELETE CASCADE,
    user_id  INTEGER NOT NULL REFERENCES UserProfile(user_id) ON DELETE CASCADE,
    PRIMARY KEY (party_id, user_id)
);

-- 27. WatchPartySuggestion
CREATE TABLE WatchPartySuggestion (
    party_id    INTEGER NOT NULL REFERENCES WatchParty(party_id) ON DELETE CASCADE,
    movie_id    INTEGER NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    group_score NUMERIC(6,3),
    suggested_by INTEGER REFERENCES UserProfile(user_id) ON DELETE SET NULL,
    PRIMARY KEY (party_id, movie_id)
);

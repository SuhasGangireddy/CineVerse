# CineVerse -- An IMDb/Netflix-Inspired Movie Database System

## ISE 503: Data Management -- Final Project Report

**Spring 2026**

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Database Design -- Conceptual Design](#2-database-design--conceptual-design)
3. [Relational Mapping](#3-relational-mapping)
4. [SQL Queries](#4-sql-queries)
5. [Data Sources and Volume](#5-data-sources-and-volume)
6. [Application Interface](#6-application-interface)
7. [Deliverables Checklist](#7-deliverables-checklist)
8. [References](#8-references)

---

## 1. Project Overview

### 1.1 Project Title

**CineVerse -- An IMDb/Netflix-Inspired Movie Database System**

### 1.2 Problem Statement

The modern film landscape is fragmented across dozens of streaming services, review aggregators, and social platforms. A viewer who wants to find a highly rated science-fiction thriller available on their streaming subscription, check whether their friends have already seen it, and understand *why* the film is recommended to them must juggle IMDb, Rotten Tomatoes, JustWatch, and Letterboxd simultaneously. No single open-source, relational system unifies movie metadata, user preferences, streaming availability, award history, mood-based discovery, and group-watch planning into one coherent data model.

CineVerse addresses this gap. It is a full-stack relational database application that consolidates real-world data from IMDb, MovieLens, and TMDb into a normalized PostgreSQL schema, exposes it through a RESTful API, and renders it in an interactive React frontend. The system demonstrates the practical application of relational database principles -- normalization, referential integrity, complex multi-table joins, and transactional operations -- within a domain that is intuitive, data-rich, and immediately useful.

### 1.3 Objectives

1. **Design a normalized relational schema** comprising 27 tables (14 entities + 13 bridge/junction tables) that captures movies, people, genres, ratings, reviews, tags, streaming availability, awards, production companies, watchlists, and group watch parties, enforced with primary keys, foreign keys, CHECK constraints, UNIQUE constraints, and cascading delete rules.

2. **Source, clean, and load real-world data** from IMDb Non-Commercial Datasets, MovieLens Latest Small, and the TMDb API, totaling over 31,000 rows across all tables, with a minimum of 30 rows in every populated table.

3. **Implement 10 complex SQL queries** that exercise advanced relational techniques including multi-table JOINs, window functions (RANK, DENSE_RANK), aggregate functions with HAVING filters, correlated subqueries, NOT EXISTS anti-join patterns, STRING_AGG for denormalized display, CASE expressions, and statistical functions (PERCENTILE_CONT).

4. **Build a Python FastAPI backend** that exposes a RESTful API with endpoints for search, movie detail, recommendations, watchlist management, group watch, database insights, and administrative transactions (INSERT, UPDATE, DELETE).

5. **Develop a React single-page application** with 9 distinct screens that demonstrate the full breadth of the data model -- from Netflix-style browsing and multi-filter search to mood-based explainable recommendations and group watch party planning.

6. **Document the entire system** with an ER diagram, relational mapping, constraints summary, and this final report, providing a complete academic deliverable for ISE 503.

### 1.4 Team Members and Contributions

| Member | Primary Contributions |
|---|---|
| **Student 1** | Database schema design, ER modeling, constraint definitions, normalization decisions, DDL authoring (`01_create_tables.sql`), complex query design (Q01--Q10), index strategy |
| **Student 2** | ETL pipeline development, data sourcing (IMDb, MovieLens, TMDb), data cleaning and validation scripts, CSV generation, data loading (`02_load_data.sql`), data quality assurance |
| **Student 3** | Frontend development (React + Vite + TailwindCSS), backend API (FastAPI), UI/UX design, API endpoint implementation, integration testing, deployment documentation |

### 1.5 What Makes CineVerse Unique

CineVerse goes beyond a basic movie-lookup database in four key ways:

| Feature | Description | Tables Involved |
|---|---|---|
| **Explainable Recommendations** | Recommendations are generated via tag-matching between user preferences and movie mood tags; the system explains *why* each movie is recommended by listing the matching tags and their relevance scores. | UserPreferenceTag, MovieTagRelevance, Tag, RecommendationLog |
| **Mood/Theme Tags** | Every movie is annotated with mood tags (e.g., "mind-bending," "dark," "funny," "visually stunning") and a relevance score (0.0--1.0), enabling discovery beyond genre. | Tag, MovieTagRelevance |
| **Group Watch Planning** | Users can create watch parties, invite members, and receive group-optimized suggestions -- movies that no member has seen yet, filtered to genres the group collectively rates highly. | WatchParty, WatchPartyMember, WatchPartySuggestion |
| **Streaming Availability** | Each movie is linked to streaming platforms with region and access type (subscription, rent, buy, free, theater), enabling "where can I watch this?" queries. | StreamingPlatform, MovieAvailability |

---

## 2. Database Design -- Conceptual Design

### 2.1 Entity Summary

The CineVerse schema contains **14 primary entities**, each representing a distinct real-world concept:

| # | Entity | Description | Primary Key | Key Attributes |
|---|--------|-------------|-------------|----------------|
| 1 | **Movie** | Central catalog of films with metadata | `movie_id` (SERIAL) | imdb_id, tmdb_id, title, release_year, release_date, runtime_minutes, language, country, plot, budget, revenue, imdb_rating, imdb_votes, poster_url, genres_raw |
| 2 | **Person** | Actors, directors, producers, writers -- unified in one table | `person_id` (SERIAL) | imdb_person_id, name, birth_year, death_year, primary_profession |
| 3 | **RoleType** | Lookup table for role categories | `role_type_id` (SERIAL) | role_name (Actor, Director, Producer, Writer) |
| 4 | **Genre** | Normalized genre list | `genre_id` (SERIAL) | genre_name (Action, Drama, Comedy, etc.) |
| 5 | **Distributor** | Film distribution companies | `distributor_id` (SERIAL) | name, address, country |
| 6 | **UserProfile** | Application users who rate and review movies | `user_id` (SERIAL) | username, email, age_group, preferred_language |
| 7 | **Tag** | Mood and theme tags for recommendation engine | `tag_id` (SERIAL) | tag_name (dark, funny, mind-bending, etc.) |
| 8 | **StreamingPlatform** | Streaming services where movies are available | `platform_id` (SERIAL) | name, country, website_url |
| 9 | **Award** | Award ceremonies and categories | `award_id` (SERIAL) | award_name, category |
| 10 | **ProductionCompany** | Studios behind each film | `company_id` (SERIAL) | name, country, founded_year |
| 11 | **Watchlist** | User-created watchlists | `watchlist_id` (SERIAL) | user_id (FK), name |
| 12 | **WatchParty** | Group watch events | `party_id` (SERIAL) | host_user_id (FK), party_name, planned_date |
| 13 | **RecommendationLog** | Persisted recommendation results with explanations | `recommendation_id` (SERIAL) | user_id (FK), movie_id (FK), score, explanation |
| 14 | **Review** | User-written movie reviews with sentiment | `review_id` (SERIAL) | user_id (FK), movie_id (FK), review_text, sentiment |

### 2.2 Bridge/Junction Tables

The schema contains **13 bridge tables** that resolve many-to-many relationships and composite-key associations:

| # | Bridge Table | Resolves Relationship | Primary Key | Additional Columns |
|---|---|---|---|---|
| 1 | **MovieCredit** | Movie -- Person (via RoleType) | `credit_id` (surrogate) | character_name, billing_order; UNIQUE(movie_id, person_id, role_type_id, character_name) |
| 2 | **MovieGenre** | Movie -- Genre | (movie_id, genre_id) | -- |
| 3 | **MovieDistributor** | Movie -- Distributor | (movie_id, distributor_id, region) | region |
| 4 | **MovieAvailability** | Movie -- StreamingPlatform | (movie_id, platform_id, region, access_type) | start_date, end_date |
| 5 | **MovieAward** | Movie -- Award (optionally Person) | `movie_award_id` (surrogate) | person_id (nullable FK), award_year, result; UNIQUE(movie_id, award_id, award_year) |
| 6 | **MovieProductionCompany** | Movie -- ProductionCompany | (movie_id, company_id) | -- |
| 7 | **MovieTagRelevance** | Movie -- Tag | (movie_id, tag_id) | relevance_score |
| 8 | **UserRating** | UserProfile -- Movie (ratings) | (user_id, movie_id) | rating, rating_date |
| 9 | **ExternalRating** | Movie -- external sources | (movie_id, source_name) | score, max_score, vote_count |
| 10 | **UserPreferenceTag** | UserProfile -- Tag | (user_id, tag_id) | preference_weight |
| 11 | **WatchlistItem** | Watchlist -- Movie | (watchlist_id, movie_id) | added_at, watched_status |
| 12 | **WatchPartyMember** | WatchParty -- UserProfile | (party_id, user_id) | -- |
| 13 | **WatchPartySuggestion** | WatchParty -- Movie | (party_id, movie_id) | group_score, suggested_by |

### 2.3 Key Relationships and Cardinalities

| # | Relationship | Cardinality | Type | Resolved By |
|---|---|---|---|---|
| 1 | Movie -- Person (cast/crew) | M : N | Many-to-Many | MovieCredit (ternary: includes RoleType) |
| 2 | Movie -- Genre | M : N | Many-to-Many | MovieGenre |
| 3 | Movie -- StreamingPlatform | M : N | Many-to-Many | MovieAvailability (with region + access_type) |
| 4 | Movie -- Award | M : N | Many-to-Many | MovieAward (with optional Person link) |
| 5 | Movie -- ProductionCompany | M : N | Many-to-Many | MovieProductionCompany |
| 6 | Movie -- Distributor | M : N | Many-to-Many | MovieDistributor (with region) |
| 7 | Movie -- Tag | M : N | Many-to-Many | MovieTagRelevance (with relevance_score) |
| 8 | UserProfile -- Movie (rating) | M : N | Many-to-Many | UserRating (one rating per user-movie pair) |
| 9 | UserProfile -- Movie (review) | 1 : 1 per pair | Many-to-Many (constrained) | Review (UNIQUE on user_id, movie_id) |
| 10 | UserProfile -- Tag (preference) | M : N | Many-to-Many | UserPreferenceTag |
| 11 | UserProfile -- Watchlist | 1 : M | One-to-Many | Watchlist.user_id FK |
| 12 | Watchlist -- Movie | M : N | Many-to-Many | WatchlistItem |
| 13 | UserProfile -- WatchParty (host) | 1 : M | One-to-Many | WatchParty.host_user_id FK |
| 14 | WatchParty -- UserProfile (members) | M : N | Many-to-Many | WatchPartyMember |
| 15 | WatchParty -- Movie (suggestions) | M : N | Many-to-Many | WatchPartySuggestion |
| 16 | UserProfile -- Movie (recommendation) | 1 : M | One-to-Many | RecommendationLog |

### 2.4 Design Decisions and Rationale

#### Why a Unified Person Table Instead of Separate Actor/Director/Producer Tables

In the film industry, a single individual frequently serves in multiple capacities. Christopher Nolan is a director, producer, and writer. Clint Eastwood is an actor and director. Creating separate Actor, Director, and Producer tables would either duplicate personal data (name, birth_year) across tables or require a fragile cross-table identity system. The unified Person table stores each individual once, while the MovieCredit bridge table paired with RoleType captures the *role* a person played on a specific film. This design:

- Eliminates data redundancy for multi-role individuals
- Simplifies queries that need to identify "all work by a person regardless of role"
- Follows the generalization/specialization pattern recommended for overlapping subtypes

#### Why MovieCredit Is a Ternary Relationship (Three Foreign Keys)

MovieCredit links three entities: **Movie**, **Person**, and **RoleType**. This ternary design is necessary because the same person can be associated with the same movie in multiple roles (e.g., Clint Eastwood as both Actor and Director in *Unforgiven*), and the same person-role combination can appear in different movies. The three foreign keys (movie_id, person_id, role_type_id) together with the character_name column form a UNIQUE constraint that prevents truly duplicate entries while allowing the same actor to play multiple characters in the same film.

#### Why MovieAvailability Has a 4-Column Composite Primary Key

A single movie can appear on the same streaming platform in the same region with *different access types* -- for example, a film might be available on Amazon Prime Video in the US both via subscription (included with Prime) and for rent ($3.99). The four-column composite key `(movie_id, platform_id, region, access_type)` captures this real-world reality. Reducing the key to fewer columns would either lose information or require artificial constraints.

#### Why MovieAward.person_id Uses ON DELETE SET NULL

Awards are sometimes given to individuals (Best Actor, Best Director) and sometimes to films as a whole (Best Picture). When an award is associated with a person and that person's record is deleted, the award history for the *film* should be preserved -- only the person linkage should be nullified. ON DELETE SET NULL achieves this: the MovieAward row survives, recording that the film won the award, but the person reference becomes NULL. This is semantically distinct from ON DELETE CASCADE, which would destroy the entire award record.

### 2.5 ER Diagram

The full entity-relationship diagram is available at:

```
docs/database_design/er_diagram.png
```

![ER Diagram](database_design/er_diagram.png)

The schema is organized into logical layers:

- **Core Layer**: Movie, Person, RoleType, MovieCredit, Genre, MovieGenre
- **User Layer**: UserProfile, UserRating, Review, ExternalRating
- **Discovery Layer**: Tag, MovieTagRelevance, UserPreferenceTag, RecommendationLog
- **Streaming Layer**: StreamingPlatform, MovieAvailability
- **Industry Layer**: Award, MovieAward, ProductionCompany, MovieProductionCompany, Distributor, MovieDistributor
- **Social Layer**: Watchlist, WatchlistItem, WatchParty, WatchPartyMember, WatchPartySuggestion

Additional design diagrams:

- Relational Mapping: `docs/database_design/relational_mapping.png`
- Constraints Summary: `docs/database_design/constraints_summary.png`

### 2.6 Constraint Strategy

The CineVerse schema employs a defense-in-depth constraint strategy. Every constraint type supported by PostgreSQL is utilized to ensure data integrity at the database level, independent of any application logic.

| Constraint Type | Count | Example 1 | Example 2 | Example 3 |
|---|---|---|---|---|
| **PRIMARY KEY (surrogate)** | 15 | `Movie.movie_id SERIAL PRIMARY KEY` | `Person.person_id SERIAL PRIMARY KEY` | `Award.award_id SERIAL PRIMARY KEY` |
| **PRIMARY KEY (composite)** | 11 | `UserRating(user_id, movie_id)` | `MovieGenre(movie_id, genre_id)` | `MovieAvailability(movie_id, platform_id, region, access_type)` |
| **FOREIGN KEY** | 40+ | `MovieCredit.movie_id REFERENCES Movie(movie_id)` | `UserRating.user_id REFERENCES UserProfile(user_id)` | `WatchParty.host_user_id REFERENCES UserProfile(user_id)` |
| **UNIQUE** | 11 | `Movie.imdb_id UNIQUE` | `UserProfile.username UNIQUE` | `uq_movie_person_role_char (movie_id, person_id, role_type_id, character_name)` |
| **CHECK** | 18 | `rating BETWEEN 0.0 AND 10.0` | `runtime_minutes > 0` | `access_type IN ('subscription','rent','buy','free','theater')` |
| **NOT NULL** | 20+ | `Movie.title NOT NULL` | `Movie.imdb_id NOT NULL` | `UserRating.rating NOT NULL` |
| **DEFAULT** | 5 | `Movie.created_at DEFAULT CURRENT_TIMESTAMP` | `Movie.language DEFAULT 'English'` | `WatchlistItem.watched_status DEFAULT 'unwatched'` |
| **ON DELETE CASCADE** | 8 | `MovieGenre.movie_id ON DELETE CASCADE` | `UserRating.user_id ON DELETE CASCADE` | `WatchlistItem.watchlist_id ON DELETE CASCADE` |
| **ON DELETE SET NULL** | 2 | `MovieAward.person_id ON DELETE SET NULL` | `WatchPartySuggestion.suggested_by ON DELETE SET NULL` | -- |

---

## 3. Relational Mapping

### 3.1 Conceptual-to-Relational Transformation

The conceptual ER model was systematically transformed into a relational schema following standard mapping rules:

- **Strong entities** became tables with their own surrogate SERIAL primary key.
- **M:N relationships** were resolved into bridge tables with composite primary keys referencing both parent tables.
- **1:M relationships** were implemented by placing a foreign key in the "many" side table.
- **Ternary relationships** (MovieCredit) received a surrogate key with a multi-column UNIQUE constraint.
- **Attribute constraints** from the conceptual model (domain restrictions, optionality) were mapped to CHECK, NOT NULL, and DEFAULT constraints.

### 3.2 Entity-to-Table Mapping

| Concept | Table Name | Key Column(s) | Type |
|---|---|---|---|
| Film | Movie | movie_id (SERIAL PK) | Entity |
| Individual | Person | person_id (SERIAL PK) | Entity |
| Role Category | RoleType | role_type_id (SERIAL PK) | Lookup |
| Film Genre Category | Genre | genre_id (SERIAL PK) | Lookup |
| Distribution Company | Distributor | distributor_id (SERIAL PK) | Entity |
| Application User | UserProfile | user_id (SERIAL PK) | Entity |
| Mood/Theme Label | Tag | tag_id (SERIAL PK) | Lookup |
| Streaming Service | StreamingPlatform | platform_id (SERIAL PK) | Entity |
| Award Ceremony + Category | Award | award_id (SERIAL PK) | Entity |
| Studio | ProductionCompany | company_id (SERIAL PK) | Entity |
| User Watchlist | Watchlist | watchlist_id (SERIAL PK) | Entity |
| Group Event | WatchParty | party_id (SERIAL PK) | Entity |
| Recommendation Record | RecommendationLog | recommendation_id (SERIAL PK) | Entity |
| User Review | Review | review_id (SERIAL PK) | Entity |
| Film -- Person -- Role | MovieCredit | credit_id (SERIAL PK) + UNIQUE composite | Bridge (ternary) |
| Film -- Genre | MovieGenre | (movie_id, genre_id) | Bridge |
| Film -- Distributor | MovieDistributor | (movie_id, distributor_id, region) | Bridge |
| Film -- Platform | MovieAvailability | (movie_id, platform_id, region, access_type) | Bridge |
| Film -- Award | MovieAward | movie_award_id (SERIAL PK) + UNIQUE composite | Bridge |
| Film -- Studio | MovieProductionCompany | (movie_id, company_id) | Bridge |
| Film -- Tag | MovieTagRelevance | (movie_id, tag_id) | Bridge |
| User -- Film Rating | UserRating | (user_id, movie_id) | Bridge |
| Film -- External Source | ExternalRating | (movie_id, source_name) | Bridge |
| User -- Tag Preference | UserPreferenceTag | (user_id, tag_id) | Bridge |
| Watchlist -- Film | WatchlistItem | (watchlist_id, movie_id) | Bridge |
| Party -- User | WatchPartyMember | (party_id, user_id) | Bridge |
| Party -- Film Suggestion | WatchPartySuggestion | (party_id, movie_id) | Bridge |

### 3.3 Full SQL DDL for Key Tables

#### Movie -- Main Entity with the Most Constraints

```sql
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
```

**Constraints demonstrated:** SERIAL surrogate PK, UNIQUE (imdb_id), NOT NULL (imdb_id, title), five CHECK constraints (release_year lower bound, runtime positive, budget/revenue non-negative, rating domain), DEFAULT (language, created_at).

#### MovieCredit -- Ternary Bridge with UNIQUE Constraint

```sql
CREATE TABLE MovieCredit (
    credit_id      SERIAL PRIMARY KEY,
    movie_id       INTEGER NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    person_id      INTEGER NOT NULL REFERENCES Person(person_id) ON DELETE CASCADE,
    role_type_id   INTEGER NOT NULL REFERENCES RoleType(role_type_id),
    character_name VARCHAR(255),
    billing_order  INTEGER CHECK (billing_order > 0),
    CONSTRAINT uq_movie_person_role_char
        UNIQUE (movie_id, person_id, role_type_id, character_name)
);
```

**Constraints demonstrated:** Surrogate PK with separate multi-column UNIQUE, three NOT NULL foreign keys, ON DELETE CASCADE for movie/person deletion, CHECK on billing_order. The UNIQUE constraint prevents duplicate credit entries while allowing the same actor to play multiple characters.

#### UserRating -- Composite PK with CHECK

```sql
CREATE TABLE UserRating (
    user_id     INTEGER NOT NULL REFERENCES UserProfile(user_id) ON DELETE CASCADE,
    movie_id    INTEGER NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    rating      NUMERIC(3,1) NOT NULL CHECK (rating BETWEEN 0.0 AND 10.0),
    rating_date DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (user_id, movie_id)
);
```

**Constraints demonstrated:** Two-column composite PK enforcing one rating per user-movie pair, domain CHECK on rating (0.0--10.0), DEFAULT on rating_date, ON DELETE CASCADE on both FKs.

#### MovieAvailability -- 4-Column Composite PK with CHECK

```sql
CREATE TABLE MovieAvailability (
    movie_id    INTEGER NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    platform_id INTEGER NOT NULL REFERENCES StreamingPlatform(platform_id)
                ON DELETE CASCADE,
    region      VARCHAR(50) NOT NULL DEFAULT 'US',
    access_type VARCHAR(20) NOT NULL
                CHECK (access_type IN ('subscription','rent','buy','free','theater')),
    start_date  DATE,
    end_date    DATE,
    PRIMARY KEY (movie_id, platform_id, region, access_type)
);
```

**Constraints demonstrated:** Four-column composite PK (the widest PK in the schema), enumerated CHECK constraint on access_type, DEFAULT on region, ON DELETE CASCADE on both FKs.

#### MovieAward -- SET NULL, CHECK, and UNIQUE

```sql
CREATE TABLE MovieAward (
    movie_award_id SERIAL PRIMARY KEY,
    movie_id       INTEGER NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    award_id       INTEGER NOT NULL REFERENCES Award(award_id) ON DELETE CASCADE,
    person_id      INTEGER REFERENCES Person(person_id) ON DELETE SET NULL,
    award_year     INTEGER NOT NULL CHECK (award_year >= 1900),
    result         VARCHAR(20) NOT NULL CHECK (result IN ('won', 'nominated')),
    CONSTRAINT uq_movie_award_year UNIQUE (movie_id, award_id, award_year)
);
```

**Constraints demonstrated:** ON DELETE SET NULL (person_id becomes NULL when person is deleted, preserving the award record), ON DELETE CASCADE (movie/award deletion removes the row), two CHECK constraints, UNIQUE on the natural key (movie, award, year).

### 3.4 Normalization and Bridge Tables

The schema is in **Third Normal Form (3NF)**. Bridge tables are the primary mechanism for preventing data duplication:

- Without MovieGenre, genre data would need to be stored as a comma-separated string in Movie (violating 1NF) or duplicated across rows.
- Without MovieCredit, person attributes (name, birth_year) would be repeated for every film they appear in.
- Without MovieAvailability, streaming data would be embedded in Movie, making it impossible to represent the same movie on multiple platforms in multiple regions with different access types.

Each bridge table stores only foreign keys and relationship-specific attributes (e.g., relevance_score in MovieTagRelevance, billing_order in MovieCredit), ensuring zero redundancy.

---

## 4. SQL Queries

The following 10 queries demonstrate advanced SQL techniques across the CineVerse schema. Each query addresses a distinct analytical or operational need.

---

### Query 1: Top-Rated Movies by Genre

**Business Purpose:** Identify the highest-rated movies within each genre based on community ratings, enabling genre-specific "best of" lists while filtering out movies with insufficient rating counts to ensure statistical reliability.

**Tables Joined:** Movie, MovieGenre, Genre, UserRating

**SQL Techniques:** JOIN (3 inner joins), GROUP BY, HAVING (minimum vote threshold), Window Function (RANK with PARTITION BY), Aggregate (AVG, COUNT)

```sql
SELECT
    g.genre_name,
    m.title,
    m.release_year,
    ROUND(AVG(ur.rating), 2) AS avg_user_rating,
    COUNT(ur.user_id) AS num_ratings,
    RANK() OVER (PARTITION BY g.genre_name
                 ORDER BY AVG(ur.rating) DESC) AS genre_rank
FROM Movie m
JOIN MovieGenre mg ON mg.movie_id = m.movie_id
JOIN Genre g ON g.genre_id = mg.genre_id
JOIN UserRating ur ON ur.movie_id = m.movie_id
GROUP BY g.genre_name, m.movie_id, m.title, m.release_year
HAVING COUNT(ur.user_id) >= 5
ORDER BY g.genre_name, genre_rank
LIMIT 50;
```

---

### Query 2: Actor-Director Collaborations

**Business Purpose:** Discover recurring creative partnerships between actors and directors -- pairs who have worked together on two or more films. This reveals the industry's most prolific collaborations (e.g., DiCaprio-Scorsese, Hanks-Spielberg).

**Tables Joined:** MovieCredit (self-join: actor side + director side), RoleType (joined twice), Person (joined twice), Movie

**SQL Techniques:** Self-JOIN on MovieCredit, role-based filtering via RoleType, GROUP BY with HAVING, STRING_AGG for concatenated movie titles, COUNT DISTINCT

```sql
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
```

---

### Query 3: Audience vs. Critic Score Divergence

**Business Purpose:** Identify movies where community user ratings diverge significantly from IMDb critic scores, classifying each as an "Audience Favorite," "Critic Favorite," or "Consensus" film. This is valuable for understanding taste biases and finding underappreciated films.

**Tables Joined:** Movie, UserRating, ExternalRating

**SQL Techniques:** JOIN (2 inner joins), GROUP BY with HAVING, CASE expression for categorical labeling, Aggregate (AVG, COUNT), ABS for absolute divergence ordering, arithmetic expressions

```sql
SELECT
    m.title,
    m.release_year,
    ROUND(AVG(ur.rating), 2) AS avg_user_rating,
    er.score AS imdb_score,
    ROUND(AVG(ur.rating) - er.score, 2) AS user_vs_critic_gap,
    COUNT(ur.user_id) AS num_user_ratings,
    CASE
        WHEN AVG(ur.rating) - er.score > 1.0 THEN 'Audience Favorite'
        WHEN er.score - AVG(ur.rating) > 1.0 THEN 'Critic Favorite'
        ELSE 'Consensus'
    END AS gap_category
FROM Movie m
JOIN UserRating ur ON ur.movie_id = m.movie_id
JOIN ExternalRating er ON er.movie_id = m.movie_id
    AND er.source_name = 'IMDb'
GROUP BY m.movie_id, m.title, m.release_year, er.score
HAVING COUNT(ur.user_id) >= 3
ORDER BY ABS(AVG(ur.rating) - er.score) DESC
LIMIT 25;
```

---

### Query 4: Mood-Based Recommendations

**Business Purpose:** Generate personalized movie recommendations for a specific user by matching mood/theme tags from their highly-rated films to unrated films, producing an explainable recommendation with matching tags listed. This powers the Recommendation Lab screen.

**Tables Joined:** MovieTagRelevance, Tag, Movie, UserRating (LEFT JOIN for exclusion + correlated subquery)

**SQL Techniques:** Correlated Subquery (IN clause to derive user's preferred tags), LEFT JOIN + IS NULL anti-pattern (exclude already-rated movies), STRING_AGG for tag display, SUM aggregate for recommendation scoring, GROUP BY

```sql
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
  AND ur.user_id IS NULL
  AND t.tag_name IN (
      SELECT DISTINCT t2.tag_name
      FROM UserRating ur2
      JOIN MovieTagRelevance mtr2 ON mtr2.movie_id = ur2.movie_id
      JOIN Tag t2 ON t2.tag_id = mtr2.tag_id
      WHERE ur2.user_id = 1
        AND ur2.rating >= 8.0
        AND mtr2.relevance_score >= 0.6
  )
GROUP BY m.movie_id, m.title, m.release_year, m.imdb_rating
ORDER BY recommendation_score DESC
LIMIT 15;
```

---

### Query 5: Hidden Gems

**Business Purpose:** Surface high-quality movies that have received little mainstream attention -- films with high user ratings but below-median IMDb vote counts. These are the "hidden gems" that deserve more visibility.

**Tables Joined:** Movie, UserRating

**SQL Techniques:** Scalar Subquery with PERCENTILE_CONT (median calculation), GROUP BY with compound HAVING (minimum ratings AND minimum average), LOG function for weighted scoring, Aggregate (AVG, COUNT)

```sql
SELECT
    m.title,
    m.release_year,
    ROUND(AVG(ur.rating), 2) AS avg_user_rating,
    COUNT(ur.user_id) AS num_ratings,
    m.imdb_votes,
    m.imdb_rating,
    ROUND(AVG(ur.rating) * LOG(COUNT(ur.user_id) + 1), 2) AS weighted_score
FROM Movie m
JOIN UserRating ur ON ur.movie_id = m.movie_id
WHERE m.imdb_votes < (
    SELECT PERCENTILE_CONT(0.5)
    WITHIN GROUP (ORDER BY imdb_votes)
    FROM Movie
)
GROUP BY m.movie_id, m.title, m.release_year, m.imdb_votes, m.imdb_rating
HAVING COUNT(ur.user_id) >= 3 AND AVG(ur.rating) >= 7.5
ORDER BY avg_user_rating DESC, num_ratings DESC
LIMIT 20;
```

---

### Query 6: Most Versatile Actors

**Business Purpose:** Rank actors by the number of distinct genres they have appeared in, identifying the most versatile performers in the database. This rewards range over volume -- an actor in 5 genres across 6 films ranks higher than one in 2 genres across 20 films.

**Tables Joined:** Person, MovieCredit, RoleType, MovieGenre, Genre

**SQL Techniques:** JOIN (4 inner joins), GROUP BY with HAVING, Window Function (DENSE_RANK), STRING_AGG for genre list, COUNT DISTINCT (both genres and movies)

```sql
SELECT
    p.name AS actor_name,
    COUNT(DISTINCT g.genre_id) AS genre_count,
    STRING_AGG(DISTINCT g.genre_name, ', ' ORDER BY g.genre_name) AS genres,
    COUNT(DISTINCT mc.movie_id) AS total_movies,
    DENSE_RANK() OVER (
        ORDER BY COUNT(DISTINCT g.genre_id) DESC
    ) AS versatility_rank
FROM Person p
JOIN MovieCredit mc ON mc.person_id = p.person_id
JOIN RoleType rt ON rt.role_type_id = mc.role_type_id
    AND rt.role_name = 'Actor'
JOIN MovieGenre mg ON mg.movie_id = mc.movie_id
JOIN Genre g ON g.genre_id = mg.genre_id
GROUP BY p.person_id, p.name
HAVING COUNT(DISTINCT mc.movie_id) >= 3
ORDER BY genre_count DESC, total_movies DESC
LIMIT 20;
```

---

### Query 7: Most Profitable Directors

**Business Purpose:** Rank directors by the total profit and return on investment (ROI) generated by their films, providing a financial lens on directorial success. This is useful for studio decision-making and industry analytics.

**Tables Joined:** Person, MovieCredit, RoleType, Movie

**SQL Techniques:** JOIN (3 inner joins), GROUP BY with HAVING, CASE expression (for safe division), NULLIF to prevent division by zero, NUMERIC casting, ROUND, arithmetic expressions (profit = revenue - budget, ROI = profit/budget * 100)

```sql
SELECT
    p.name AS director_name,
    COUNT(DISTINCT m.movie_id) AS num_films,
    ROUND(SUM(m.revenue)::NUMERIC / 1000000, 1) AS total_revenue_millions,
    ROUND(SUM(m.budget)::NUMERIC / 1000000, 1) AS total_budget_millions,
    ROUND((SUM(m.revenue) - SUM(m.budget))::NUMERIC / 1000000, 1)
        AS total_profit_millions,
    ROUND(
        CASE
            WHEN SUM(m.budget) > 0
            THEN ((SUM(m.revenue) - SUM(m.budget))::NUMERIC
                  / NULLIF(SUM(m.budget), 0)) * 100
            ELSE NULL
        END, 1
    ) AS roi_percent
FROM Person p
JOIN MovieCredit mc ON mc.person_id = p.person_id
JOIN RoleType rt ON rt.role_type_id = mc.role_type_id
    AND rt.role_name = 'Director'
JOIN Movie m ON m.movie_id = mc.movie_id
WHERE m.budget > 0 AND m.revenue > 0
GROUP BY p.person_id, p.name
HAVING COUNT(DISTINCT m.movie_id) >= 2
ORDER BY total_profit_millions DESC NULLS LAST
LIMIT 20;
```

---

### Query 8: Streaming Platform Search

**Business Purpose:** Help users find movies of specific genres available via subscription on their preferred streaming platforms in a given region. This directly powers the search screen's platform filter functionality.

**Tables Joined:** Movie, MovieAvailability, StreamingPlatform, MovieGenre, Genre

**SQL Techniques:** JOIN (4 inner joins), Multi-value IN filters, WHERE clause with equality and IN predicates, DISTINCT (to deduplicate across access types), ORDER BY with NULLS LAST

```sql
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
```

---

### Query 9: Award Winners on Streaming

**Business Purpose:** Find award-winning movies that are currently available for subscription streaming in the US. This combines the Award subsystem with the Streaming subsystem, answering "what Oscar winners can I watch tonight?"

**Tables Joined:** Movie, MovieAward, Award, MovieAvailability, StreamingPlatform

**SQL Techniques:** JOIN (4 inner joins with filter on join: `ma2.result = 'won'`), GROUP BY with HAVING, STRING_AGG (two separate aggregations: awards and platforms), COUNT DISTINCT, date comparison (`end_date IS NULL OR end_date >= CURRENT_DATE`)

```sql
SELECT
    m.title,
    m.release_year,
    m.imdb_rating,
    STRING_AGG(DISTINCT a.award_name || ' - ' || a.category, '; ')
        AS awards_won,
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
```

---

### Query 10: Group Watch Suggestions

**Business Purpose:** Recommend movies for a specific watch party that no member has already seen, restricted to genres the group collectively rates highly. This powers the Group Watch screen and ensures every suggestion is fresh for the entire party.

**Tables Joined:** Movie, UserRating, MovieGenre, Genre, WatchPartyMember (via NOT EXISTS subquery and IN subquery)

**SQL Techniques:** NOT EXISTS correlated subquery (anti-join to exclude seen movies), IN subquery (filter to group-preferred genres), GROUP BY with HAVING, JOIN, Aggregate (AVG, COUNT DISTINCT), STRING_AGG

```sql
SELECT
    m.title,
    m.release_year,
    m.imdb_rating,
    ROUND(AVG(all_ratings.rating), 2) AS avg_community_rating,
    COUNT(DISTINCT all_ratings.user_id) AS times_rated,
    STRING_AGG(DISTINCT g.genre_name, ', ' ORDER BY g.genre_name) AS genres
FROM Movie m
JOIN UserRating all_ratings ON all_ratings.movie_id = m.movie_id
JOIN MovieGenre mg ON mg.movie_id = m.movie_id
JOIN Genre g ON g.genre_id = mg.genre_id
WHERE NOT EXISTS (
    SELECT 1
    FROM WatchPartyMember wpm
    JOIN UserRating ur_seen ON ur_seen.user_id = wpm.user_id
        AND ur_seen.movie_id = m.movie_id
    WHERE wpm.party_id = 1
)
AND m.movie_id IN (
    SELECT DISTINCT mg2.movie_id
    FROM WatchPartyMember wpm2
    JOIN UserRating ur2 ON ur2.user_id = wpm2.user_id AND ur2.rating >= 7.0
    JOIN MovieGenre mg2 ON mg2.movie_id = ur2.movie_id
    WHERE wpm2.party_id = 1
)
GROUP BY m.movie_id, m.title, m.release_year, m.imdb_rating
HAVING COUNT(DISTINCT all_ratings.user_id) >= 3
ORDER BY avg_community_rating DESC
LIMIT 10;
```

---

### Query Technique Summary

| Query | RANK/DENSE_RANK | STRING_AGG | CASE | NOT EXISTS | PERCENTILE_CONT | Subquery | HAVING | Multi-JOIN |
|---|---|---|---|---|---|---|---|---|
| Q01 Top Rated by Genre | X | | | | | | X | X |
| Q02 Collaborations | | X | | | | | X | X |
| Q03 Audience vs. Critic | | | X | | | | X | X |
| Q04 Mood Recommendations | | X | | | | X | | X |
| Q05 Hidden Gems | | | | | X | X | X | X |
| Q06 Versatile Actors | X | X | | | | | X | X |
| Q07 Profitable Directors | | | X | | | | X | X |
| Q08 Streaming Search | | | | | | | | X |
| Q09 Award Winners Streaming | | X | | | | | X | X |
| Q10 Group Watch | | X | | X | | X | X | X |

---

## 5. Data Sources, Retrieval, Cleaning, and Volume

### 5.1 Data Source Overview

CineVerse uses three public data sources that complement each other. IMDb provides the authoritative movie catalog and cast/crew data. MovieLens provides user rating behavior and discovery tags. TMDb fills in visual and financial metadata. By merging these, the database has both structural depth and realistic user interaction data.

| Source | Type | URL | License |
|---|---|---|---|
| **IMDb Non-Commercial Datasets** | Bulk TSV files (gzipped) | https://developer.imdb.com/non-commercial-datasets/ | Non-commercial use only |
| **MovieLens Latest Small** | CSV archive (zip) | https://grouplens.org/datasets/movielens/latest/ | Research use, no redistribution restrictions |
| **TMDb API** | REST API (JSON) | https://developer.themoviedb.org/ | Free API key, attribution required |

---

### 5.2 IMDb Non-Commercial Datasets — What Was Retrieved

Four TSV files were downloaded from IMDb's public dataset server (`datasets.imdbws.com`):

| File | Size (uncompressed) | Contents | Key Columns Used |
|---|---|---|---|
| `title.basics.tsv` | ~800 MB | Every title in IMDb (movies, TV shows, episodes, shorts) | `tconst` (IMDb ID), `titleType`, `primaryTitle`, `startYear`, `runtimeMinutes`, `genres` |
| `title.ratings.tsv` | ~22 MB | Average ratings and vote counts for all titles | `tconst`, `averageRating`, `numVotes` |
| `name.basics.tsv` | ~750 MB | Every person in IMDb's database | `nconst` (person ID), `primaryName`, `birthYear`, `deathYear`, `primaryProfession` |
| `title.principals.tsv` | ~2 GB | Cast and crew credits per title (top 10 billed) | `tconst`, `nconst`, `ordering`, `category`, `characters` |

**Filtering applied to IMDb data:**

1. **Title type filter:** Only rows with `titleType = 'movie'` were kept (excluded TV series, episodes, shorts, video games)
2. **Year filter:** Only movies with `startYear >= 1970` (modern era, relevant to streaming)
3. **Popularity filter:** Only movies with `numVotes >= 10,000` on IMDb (ensures well-known films with enough data)
4. **MovieLens cross-reference:** Only movies that also appear in MovieLens (via IMDb ID matching) were kept, so we have both metadata AND user ratings

This reduced ~11 million IMDb titles down to **500 movies** — the most popular, well-rated films from the last 55 years.

**Person filtering:** Only people who appear in the `title.principals` credits for the selected 500 movies were kept, yielding **5,166 people** and **10,021 credit records**.

---

### 5.3 MovieLens Latest Small — What Was Retrieved

A single ZIP archive was downloaded containing:

| File | Rows | Contents | How Used |
|---|---|---|---|
| `ratings.csv` | ~100,000 | User-movie rating pairs (userId, movieId, rating 0.5–5.0, timestamp) | Mapped to our movies via `links.csv`, scaled from 0.5–5.0 to 0.0–10.0, limited to 200 users / 20,000 ratings |
| `tags.csv` | ~3,600 | User-generated freetext tags (userId, movieId, tag, timestamp) | Top 200 tags by frequency became our Tag table; tag-movie co-occurrence became MovieTagRelevance scores |
| `links.csv` | ~9,700 | Bridge between MovieLens movieId, IMDb tconst, and TMDb tmdb_id | **Critical file** — this is the key that links all three data sources together |
| `movies.csv` | ~9,700 | Movie titles and genres per MovieLens ID | Used for cross-validation only |

**How MovieLens connects to IMDb:**

```
MovieLens links.csv
  movieId = 1    →  imdbId = 0114709  →  tconst = tt0114709  (Toy Story)
  movieId = 2    →  imdbId = 0113497  →  tconst = tt0113497  (Jumanji)
```

The `links.csv` file provides the `imdbId` for each MovieLens movie. We zero-padded these to 7 digits and prepended `tt` to match IMDb's `tconst` format. This allowed us to join MovieLens ratings with IMDb metadata on the same movie.

**Rating scale transformation:** MovieLens uses a 0.5–5.0 scale (half-star increments). We multiplied by 2 to convert to a 0.0–10.0 scale matching IMDb and our CHECK constraint (`rating BETWEEN 0.0 AND 10.0`).

**User selection:** The first 200 unique MovieLens userIds were selected and remapped to sequential `user_id` values (1–200) for our UserProfile table. Only ratings from these users on our 500 selected movies were kept, yielding **9,874 ratings**.

---

### 5.4 TMDb API — What Was Retrieved (Optional Enrichment)

TMDb provides richer visual and financial metadata not available in IMDb's bulk datasets. For each of the 500 movies, a GET request was made to:

```
GET https://api.themoviedb.org/3/movie/{tmdb_id}?api_key=KEY&language=en-US
```

**Fields extracted per movie:**

| TMDb Field | Maps To | Example |
|---|---|---|
| `overview` | `Movie.plot` | "A thief who steals corporate secrets through dream-sharing..." |
| `budget` | `Movie.budget` | 160000000 |
| `revenue` | `Movie.revenue` | 829895144 |
| `poster_path` | `Movie.poster_url` | Prepended with `https://image.tmdb.org/t/p/w500` |
| `original_language` | `Movie.language` | Mapped: `en→English`, `ja→Japanese`, `ko→Korean`, etc. |
| `production_countries[0].name` | `Movie.country` | "United States of America" |
| `release_date` | (stored for reference) | "2010-07-16" |

**Rate limiting:** TMDb allows ~40 requests per 10 seconds. The script pauses 0.26 seconds between requests to stay within limits, processing 500 movies in about 2.5 minutes.

**This step is optional** — the database loads and functions fully without TMDb enrichment. Movies simply have NULL values for plot, budget, revenue, and poster_url.

---

### 5.5 Data Cleaning and Transformation

Several cleaning steps were necessary to handle real-world data quality issues:

#### Issue 1: Float-formatted integers in CSVs
**Problem:** Pandas saves nullable integer columns as floats (e.g., `birth_year` becomes `1924.0` instead of `1924`). PostgreSQL's COPY command rejects `1924.0` for an INTEGER column.
**Fix:** `etl/fix_csv_types.py` converts all integer columns from `float64` to pandas `Int64` (nullable integer) dtype before saving CSVs.

#### Issue 2: Non-ASCII characters in person names
**Problem:** IMDb data contains accented characters (e.g., directors with French, Japanese, Korean names). PostgreSQL on Windows defaults to WIN1252 encoding, which cannot represent certain UTF-8 characters.
**Fix:** All string columns were cleaned by encoding to ASCII with `errors='ignore'`, stripping characters that can't round-trip through WIN1252. COPY commands include `ENCODING 'UTF8'`.

#### Issue 3: Historical anomalies (Homer, birth 850 BC)
**Problem:** IMDb lists the ancient Greek poet Homer as a writer credit with `birth_year=850, death_year=800`. Our CHECK constraint `death_year >= birth_year` rejects this.
**Fix:** `validate_and_fix_all.py` detects rows where `death_year < birth_year` and sets both to NULL.

#### Issue 4: Orphan foreign keys after filtering
**Problem:** After filtering to 500 movies, some MovieCredit rows referenced person IDs that weren't in our filtered Person table (because those people's other credits were cut).
**Fix:** The validation script checks every FK relationship across all CSVs and removes orphan rows before loading.

#### Issue 5: IMDb role category mapping
**Problem:** IMDb uses granular categories (`actor`, `actress`, `self`, `composer`, `cinematographer`, `editor`). Our schema uses 4 role types.
**Fix:** Mapped in `02_process_data.py`:

| IMDb Category | CineVerse RoleType |
|---|---|
| `actor`, `actress`, `self` | Actor |
| `director` | Director |
| `producer` | Producer |
| `writer`, `composer`, `cinematographer`, `editor` | Writer |

#### Issue 6: Character name parsing
**Problem:** IMDb stores character names as JSON arrays (e.g., `["Forrest Gump"]`). Some entries have malformed JSON or multiple characters.
**Fix:** Each `characters` field is parsed as JSON; the first element is extracted. Malformed entries fall back to the raw string, truncated to 255 characters.

#### Issue 7: Duplicate composite keys
**Problem:** After joining IMDb principals with our role mapping, some movies had duplicate `(movie_id, person_id, role_type_id, character_name)` tuples.
**Fix:** Duplicates are dropped keeping the first occurrence. Credit IDs are reassigned sequentially after deduplication.

---

### 5.6 Validation Pipeline

After all cleaning, `validate_and_fix_all.py` performs a comprehensive check against every PostgreSQL constraint:

| Validation | What It Checks | Action on Failure |
|---|---|---|
| Integer types | All PK/FK columns are true integers, not floats | Convert `float64` → `Int64` |
| NOT NULL | Required columns (title, name, rating, etc.) are not empty | Remove rows with NULL required fields |
| CHECK constraints | Rating 0–10, runtime > 0, budget >= 0, access_type IN (...), etc. | Set invalid values to NULL or remove row |
| UNIQUE constraints | No duplicate PKs, no duplicate (movie_id, genre_id), etc. | Drop duplicate rows |
| Foreign keys | Every FK value exists in the parent table | Remove orphan rows |
| Encoding | No non-ASCII characters that would fail WIN1252 | Strip to ASCII |
| Cross-table consistency | Person years (death >= birth), billing_order > 0 | Nullify invalid values |

The script reports all issues found and fixed:
```
Issues found: 3
Issues fixed: 3
All CSVs are clean. Ready to load.
```

---

### 5.7 Data Loading into PostgreSQL

Two loading methods are provided:

**Method A: COPY (fast, recommended)**
```bash
psql -U postgres -d cineverse -f sql/02_load_data.sql
```
Uses PostgreSQL's `\copy` command to bulk-load each CSV directly into its table. All 31,000+ rows load in under 5 seconds. The script resets SERIAL sequences to `MAX(id) + 1` after loading.

**Method B: INSERT (portable)**
```bash
psql -U postgres -d cineverse -f sql/02_insert_data.sql
```
Generated INSERT statements (1,228 KB file) as a fallback for environments where COPY is unavailable. Inserts are batched in groups of 50 rows.

---

### 5.8 Final Row Counts

| Table | Rows | Primary Source |
|---|---|---|
| Movie | 500 | IMDb title.basics (filtered) |
| Person | 5,166 | IMDb name.basics |
| MovieCredit | 10,021 | IMDb title.principals |
| RoleType | 4 | Manual |
| Genre | 20 | Extracted from IMDb genres |
| MovieGenre | 1,342 | IMDb genre strings (split + normalized) |
| Distributor | 20 | Curated list of major distributors |
| MovieDistributor | 500 | Random assignment with real distributor names |
| UserProfile | 200 | MovieLens user IDs (remapped) |
| UserRating | 9,874 | MovieLens ratings (scaled 0.5–5.0 → 0–10) |
| ExternalRating | 500 | IMDb averageRating + numVotes |
| Tag | 200 | MovieLens user tags (top 200 by frequency) |
| MovieTagRelevance | 754 | Tag-movie co-occurrence frequency scores |
| StreamingPlatform | 10 | Curated (Netflix, Prime, Disney+, Hulu, etc.) |
| MovieAvailability | 995 | Synthetic (1–3 random platforms per movie) |
| Award | 15 | Oscar, Golden Globe, BAFTA, Cannes categories |
| MovieAward | 158 | Top 80 movies assigned random wins/nominations |
| ProductionCompany | 25 | Major studios (Warner Bros, Disney, etc.) |
| MovieProductionCompany | 749 | 1–2 random studios per movie |
| Watchlist | 50 | One default watchlist per first 50 users |
| WatchlistItem | 219 | 2–7 random movies per watchlist |
| WatchParty | 15 | Synthetic group watch events |
| WatchPartyMember | 43 | 2–4 members per party |
| WatchPartySuggestion | 46 | 2–4 movie suggestions per party |
| **Total** | **31,426** | **Average: 1,309 rows per table** |

### 5.9 Data Source Integration Map

This diagram shows how the three sources connect through shared identifiers:

```
IMDb Datasets                   MovieLens                    TMDb API
─────────────                   ─────────                    ────────
title.basics.tsv ──┐
  tconst (tt0114709)│     links.csv
  primaryTitle      │       movieId ←→ imdbId ←→ tmdbId     GET /movie/{tmdb_id}
  startYear         ├──→  ratings.csv                   ──→   poster_path
  runtimeMinutes    │       userId, movieId, rating          overview
  genres            │     tags.csv                           budget, revenue
                    │       userId, movieId, tag              production_countries
title.ratings.tsv ──┤                                        original_language
  averageRating     │
  numVotes          │
                    │
name.basics.tsv ────┤
  nconst            │
  primaryName       │
  birthYear         │
                    │
title.principals ───┘
  tconst, nconst
  category, characters

        │                    │                         │
        ▼                    ▼                         ▼
   ┌─────────────────────────────────────────────────────┐
   │              CineVerse PostgreSQL Database           │
   │  Movie, Person, MovieCredit, UserRating, Tag, etc.  │
   │                  27 tables, 31K+ rows                │
   └─────────────────────────────────────────────────────┘
```

---

## 6. Application Interface

### 6.1 Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 18 + Vite + TailwindCSS | Single-page application with responsive UI |
| **Backend** | Python FastAPI | RESTful API server with automatic OpenAPI docs |
| **Database** | PostgreSQL 14+ | Relational data storage with full constraint enforcement |
| **ETL** | Python (pandas, requests, tqdm) | Data sourcing, cleaning, and loading pipeline |

### 6.2 Architecture

```
+-------------------+         +-------------------+         +-------------------+
|                   |  HTTP   |                   |   SQL   |                   |
|   React + Vite    | ------> |   FastAPI (Python) | ------> |   PostgreSQL      |
|   TailwindCSS     | <------ |   Port 8000        | <------ |   27 tables       |
|   Port 5173       |  JSON   |                   | Results |   31,000+ rows    |
|                   |         |                   |         |                   |
+-------------------+         +-------------------+         +-------------------+
      Browser                     Backend API                    Database
```

### 6.3 Application Screens

| # | Screen | Description | Key Tables/Queries Demonstrated |
|---|--------|-------------|---------------------------------|
| 1 | **Login** | Netflix-style profile selection from existing UserProfile records; stores selected user in localStorage for session persistence | UserProfile |
| 2 | **Dashboard** | Displays aggregate stats (total movies, users, ratings), Top Rated row, Trending row, and Recently Released row | Movie, Genre, UserRating (aggregates: COUNT, AVG) |
| 3 | **Search** | Multi-filter search with title, genre, year range, minimum rating, streaming platform, director, actor, and mood tag filters | Movie, Person, Genre, StreamingPlatform, MovieAvailability, MovieGenre, MovieCredit, Tag, MovieTagRelevance |
| 4 | **Movie Detail** | Complete movie profile: metadata, cast/crew, genres, user ratings, external ratings, streaming availability, awards, mood tags, reviews, similar movies | Movie, MovieCredit, Person, RoleType, Genre, MovieGenre, UserRating, ExternalRating, MovieAvailability, StreamingPlatform, MovieAward, Award, MovieTagRelevance, Tag, Review (8+ table joins) |
| 5 | **Watchlist** | Personal watchlist with transactional operations: add movie, mark as watching/watched, remove movie | Watchlist, WatchlistItem, Movie (INSERT, UPDATE, DELETE transactions) |
| 6 | **Recommendation Lab** | Mood-based explainable recommendations; user selects mood tags, optionally filters by platform and minimum rating; results show matching tags and recommendation scores | UserPreferenceTag, MovieTagRelevance, Tag, Movie, RecommendationLog (Q04 logic) |
| 7 | **Group Watch** | Select a watch party and receive group-optimized movie suggestions -- films no member has seen, in genres the group likes | WatchParty, WatchPartyMember, WatchPartySuggestion, UserRating, MovieGenre, Genre (Q10: NOT EXISTS pattern) |
| 8 | **Database Insights** | Interactive query runner exposing all 10 complex queries (Q01--Q10) from the UI; user selects a query, views description, and sees tabular results | All tables (runs Q01--Q10 on demand) |
| 9 | **Admin** | Administrative panel for data transactions: insert new movies, add streaming availability, submit ratings/reviews | Movie, MovieAvailability, UserRating, Review (INSERT with constraint validation) |

### 6.4 Key API Endpoints

| Method | Endpoint | Description | Pydantic Model |
|---|---|---|---|
| GET | `/api/users` | List all user profiles | -- |
| GET | `/api/stats` | Dashboard aggregate statistics | -- |
| GET | `/api/movies/top` | Top-rated movies | -- |
| GET | `/api/movies/trending` | Trending movies (recent high ratings) | -- |
| GET | `/api/movies/recent` | Recently released movies | -- |
| GET | `/api/movies/search` | Multi-filter search (title, genre, year, rating, platform, director, actor, tag) | -- |
| GET | `/api/movies/{movie_id}` | Full movie detail (8+ table join) | -- |
| GET | `/api/movies/{movie_id}/similar` | Similar movies by genre/tag overlap | -- |
| GET | `/api/genres` | All genres | -- |
| GET | `/api/platforms` | All streaming platforms | -- |
| GET | `/api/tags` | All mood/theme tags | -- |
| GET | `/api/recommendations/{user_id}` | Personalized mood-based recommendations | -- |
| GET | `/api/watchlist/{user_id}` | User's watchlist | -- |
| POST | `/api/watchlist` | Add movie to watchlist | WatchlistInput |
| PUT | `/api/watchlist/{watchlist_id}/{movie_id}` | Update watched status | WatchlistStatusInput |
| DELETE | `/api/watchlist/{watchlist_id}/{movie_id}` | Remove from watchlist | -- |
| POST | `/api/ratings` | Submit a movie rating | RatingInput |
| POST | `/api/reviews` | Submit a movie review | ReviewInput |
| GET | `/api/group-watch/parties` | List all watch parties | -- |
| GET | `/api/group-watch/{party_id}` | Group-optimized movie suggestions | -- |
| GET | `/api/insights` | List all 10 query descriptions | -- |
| GET | `/api/insights/{query_id}` | Execute a specific insight query | -- |
| POST | `/api/admin/movies` | Insert a new movie | MovieInput |
| POST | `/api/admin/availability` | Add streaming availability | AvailabilityInput |

### 6.5 Demo Flow: A 10-Step User Journey

The following walkthrough demonstrates the full breadth of the application:

| Step | Action | Screen | Database Concepts Demonstrated |
|---|---|---|---|
| 1 | User selects their profile from the login screen | Login | SELECT from UserProfile |
| 2 | Dashboard loads with stats (500 movies, 200 users, 9,874 ratings), top-rated row, trending row | Dashboard | COUNT, AVG aggregates across Movie, UserRating |
| 3 | User searches for "Sci-Fi" movies rated 7.0+ on Netflix | Search | Multi-table JOIN (Movie, MovieGenre, Genre, MovieAvailability, StreamingPlatform) with WHERE filters |
| 4 | User clicks a movie to view full details: cast, genres, ratings, platforms, awards, mood tags | Movie Detail | 8+ table JOIN; demonstrates the full relational model |
| 5 | User adds the movie to their watchlist | Watchlist | INSERT into WatchlistItem (transaction) |
| 6 | User visits the Recommendation Lab, selects "mind-bending" and "dark" mood tags | Recommendation Lab | Subquery-based tag matching (Q04 pattern); explainable results |
| 7 | User creates/views a watch party and gets group suggestions | Group Watch | NOT EXISTS anti-join, correlated subqueries (Q10 pattern) |
| 8 | User runs "Top Rated by Genre" from the Insights panel | Database Insights | Window function RANK, PARTITION BY, HAVING (Q01) |
| 9 | User marks a watchlist movie as "watched" | Watchlist | UPDATE WatchlistItem.watched_status (transaction) |
| 10 | Admin adds a new movie and its streaming availability | Admin | INSERT into Movie, INSERT into MovieAvailability (constraint validation) |

---

## 7. Deliverables Checklist

| Course Requirement | Deliverable | Location |
|---|---|---|
| Relational schema with constraints (PKs, FKs, CHECK, UNIQUE, NOT NULL) | 27 tables with 40+ FKs, 18 CHECKs, 11 UNIQUEs, composite PKs | `sql/01_create_tables.sql` |
| SQL to create tables | Full DDL with DROP IF EXISTS and CREATE TABLE | `sql/01_create_tables.sql` |
| SQL to populate tables | COPY from CSVs + portable INSERT alternative | `sql/02_load_data.sql`, `sql/02_insert_data.sql` |
| 10 complex queries with joins, subqueries, aggregation | 10 queries using JOIN, window functions, subqueries, NOT EXISTS, CASE, STRING_AGG, PERCENTILE_CONT | `sql/queries/q01_top_rated_by_genre.sql` through `sql/queries/q10_group_watch.sql` |
| 30+ records per table | 31,426 total rows, average 1,309 per populated table | `data_clean/` (CSVs) |
| ER diagram | Entity-Relationship diagram with all entities and relationships | `docs/database_design/er_diagram.png` |
| Relational mapping | Conceptual-to-relational transformation diagram | `docs/database_design/relational_mapping.png` |
| Constraints summary | Visual summary of all constraint types used | `docs/database_design/constraints_summary.png` |
| Database design document | Full design rationale, entity listing, relationship cardinalities | `docs/database_design/DATABASE_DESIGN.md` |
| Performance indexes | Indexes on frequently joined/filtered columns | `sql/04_indexes.sql` |
| *Optional:* Application UI | React SPA with 9 screens demonstrating all queries and transactions | `frontend/src/pages/` (9 page components) |
| *Optional:* REST API | FastAPI backend with 24 endpoints | `backend/main.py`, `backend/db.py` |
| *Optional:* ETL pipeline | Automated download, processing, enrichment, validation, and loading | `etl/01_download_data.py` through `etl/04_load_to_postgres.py` |
| Final project report | This document | `docs/FINAL_REPORT.md` |

---

## 8. References

1. **IMDb Non-Commercial Datasets.**
   IMDb Developer. https://developer.imdb.com/non-commercial-datasets/
   *Used for: movie metadata, person data, cast/crew credits, ratings.*

2. **MovieLens Latest Small Dataset.**
   GroupLens Research, University of Minnesota. https://grouplens.org/datasets/movielens/latest/
   *Used for: user ratings (scaled 0--10), user-generated mood/theme tags.*

3. **TMDb API Documentation.**
   The Movie Database. https://developer.themoviedb.org/docs
   *Used for: poster images, plot summaries, budget/revenue, production companies.*

4. **PostgreSQL 16 Documentation.**
   The PostgreSQL Global Development Group. https://www.postgresql.org/docs/
   *Used for: DDL syntax, CHECK constraints, window functions, STRING_AGG, PERCENTILE_CONT.*

5. **React Documentation.**
   Meta Open Source. https://react.dev/
   *Used for: frontend component architecture, state management, routing.*

6. **FastAPI Documentation.**
   Sebastian Ramirez. https://fastapi.tiangolo.com/
   *Used for: REST API design, Pydantic models, CORS middleware, path/query parameters.*

7. **Tailwind CSS Documentation.**
   Tailwind Labs. https://tailwindcss.com/docs
   *Used for: responsive UI styling, utility-first CSS approach.*

8. **Vite Documentation.**
   Evan You and Vite Contributors. https://vitejs.dev/
   *Used for: frontend build tooling, development server, hot module replacement.*

---

*This report was prepared as the final deliverable for ISE 503: Data Management, Spring 2026.*

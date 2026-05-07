# CineVerse -- An IMDb/Netflix-Inspired Movie Database System

## ISE 503: Data Management -- Submission Document

### Spring 2026

---

**Team Members:**

| Name | Role |
|------|------|
| Aditya Kamat | Schema Design, ER Modeling, Query Authoring |
| Suhas Gangireddy | ETL Pipeline, Data Sourcing, Data Cleaning |
| Manasa Kumari | Full-Stack Application Development |

**Project Summary:** 27 tables | 31,426 rows | 10 complex SQL queries | 9 application screens | 24 REST endpoints

**Repository Structure:**

```
movie_db/
  backend/          FastAPI REST API (main.py, db.py)
  frontend/         React + Vite + TailwindCSS SPA
  sql/              DDL, data loading, indexes, 10 queries
  etl/              Data sourcing, cleaning, validation scripts
  data_clean/       Production-ready CSVs for PostgreSQL loading
  docs/             Design documents, ER diagrams, this report
  schema/           ER diagram source definitions
```

---

## Table of Contents

1. [Problem Statement and Solution](#1-problem-statement-and-solution)
2. [Team Contributions](#2-team-contributions)
3. [Database Design -- Schema Overview](#3-database-design--schema-overview)
4. [Database Design -- Layer Architecture](#4-database-design--layer-architecture)
5. [Design Decisions and Constraints](#5-design-decisions-and-constraints)
6. [Relational Mapping](#6-relational-mapping)
7. [DDL in Action -- MovieCredit Table](#7-ddl-in-action--moviecredit-table)
8. [SQL Queries (Q1--Q10)](#8-sql-queries-q1q10)
9. [Data Sources and Volume](#9-data-sources-and-volume)
10. [Application Architecture](#10-application-architecture)
11. [Live Demo Guide](#11-live-demo-guide)
12. [Deliverables Summary](#12-deliverables-summary)
13. [References](#13-references)

---

## 1. Problem Statement and Solution

### 1.1 The Problem

The modern film landscape is deeply fragmented across dozens of platforms, review aggregators, and social sites. A viewer who wants to find a highly rated science-fiction thriller available on their streaming subscription, check whether friends have already seen it, and understand why the film is recommended to them must consult at least four separate services simultaneously:

- **IMDb** for authoritative metadata, cast and crew information, and critic ratings.
- **Rotten Tomatoes** for the audience-versus-critic score split and review consensus.
- **JustWatch** for streaming availability -- which platforms offer the movie, in which regions, and at what price point.
- **Letterboxd** for social features such as personal watchlists, friend activity, and community-driven discovery lists.

No single open-source, relational system unifies movie metadata, user preferences, streaming availability, award history, mood-based discovery, and group-watch planning into one coherent data model. The result is a frustrating, tab-heavy experience that discourages discovery and makes coordinated group viewing nearly impossible.

### 1.2 The CineVerse Solution

CineVerse addresses this gap directly. It is a full-stack relational database application that consolidates real-world data from IMDb and MovieLens into a normalized PostgreSQL schema, exposes it through a RESTful API built with Python FastAPI, and renders it in an interactive React single-page application. The system demonstrates the practical application of relational database principles -- normalization, referential integrity, complex multi-table joins, and transactional operations -- within a domain that is intuitive, data-rich, and immediately useful.

CineVerse goes beyond a basic movie-lookup database in four key ways:

| Feature | Description | Tables Involved |
|---------|-------------|-----------------|
| **Unified Catalog** | Movies, people, genres, ratings, reviews, awards, and production metadata in one normalized schema | Movie, Person, MovieCredit, Genre, MovieGenre, Award, MovieAward, ProductionCompany |
| **Explainable Recommendations** | Recommendations are generated via tag-matching between user preferences and movie mood tags; the system explains *why* each movie is recommended by listing the matching tags and their relevance scores | UserPreferenceTag, MovieTagRelevance, Tag, RecommendationLog |
| **Group Watch Planning** | Users create watch parties, invite members, and receive group-optimized suggestions -- movies no member has seen yet, filtered to genres the group collectively rates highly | WatchParty, WatchPartyMember, WatchPartySuggestion |
| **Streaming Availability** | Each movie is linked to streaming platforms with region and access type (subscription, rent, buy, free, theater), enabling "where can I watch this?" queries | StreamingPlatform, MovieAvailability |

### 1.3 Project Objectives

1. Design a normalized relational schema comprising 27 tables (14 entities and 13 bridge/junction tables) that captures movies, people, genres, ratings, reviews, tags, streaming availability, awards, production companies, watchlists, and group watch parties, enforced with primary keys, foreign keys, CHECK constraints, UNIQUE constraints, and cascading delete rules.

2. Source, clean, and load real-world data from IMDb Non-Commercial Datasets and MovieLens Latest Small, totaling over 31,000 rows across all tables, with a minimum of 30 rows in every populated table.

3. Implement 10 complex SQL queries that exercise advanced relational techniques including multi-table JOINs, window functions (RANK, DENSE_RANK), aggregate functions with HAVING filters, correlated subqueries, NOT EXISTS anti-join patterns, STRING_AGG for denormalized display, CASE expressions, and statistical functions (PERCENTILE_CONT).

4. Build a Python FastAPI backend that exposes a RESTful API with 24 endpoints for search, movie detail, recommendations, watchlist management, group watch, database insights, and administrative transactions (INSERT, UPDATE, DELETE).

5. Develop a React single-page application with 9 distinct screens that demonstrate the full breadth of the data model -- from Netflix-style browsing and multi-filter search to mood-based explainable recommendations and group watch party planning.

6. Document the entire system with an ER diagram, relational mapping, constraints summary, and this submission document, providing a complete academic deliverable for ISE 503.

---

## 2. Team Contributions

The work on CineVerse was divided among three team members, with each member taking ownership of a distinct vertical slice of the project. The contributions are detailed below.

### 2.1 Aditya Kamat -- Schema Design and Query Authoring

Aditya was responsible for the foundational data modeling work that defines the shape of the entire system. His contributions include:

- **Schema Design:** Designed the complete relational schema of 27 tables organized into six logical layers (Core, User, Discovery, Streaming, Industry, Social). Every table, column, data type, and constraint was specified in the DDL file `sql/01_create_tables.sql`.
- **ER Model:** Created the conceptual Entity-Relationship model identifying 14 primary entities, 13 bridge tables, and 16 relationships with their cardinalities (M:N, 1:M, 1:1 per pair).
- **Bridge Tables:** Designed all 13 bridge/junction tables that resolve many-to-many relationships, including the ternary MovieCredit bridge (Movie-Person-RoleType) and the 4-column composite primary key on MovieAvailability.
- **Constraint Definitions:** Defined all constraints across the schema: 15 surrogate primary keys, 11 composite primary keys, 40+ foreign keys, 11 UNIQUE constraints, 18 CHECK constraints, 20+ NOT NULL constraints, 8 ON DELETE CASCADE rules, and 2 ON DELETE SET NULL rules.
- **SQL Queries:** Authored queries Q1 (Top Rated by Genre), Q2 (Actor-Director Collaborations), Q5 (Hidden Gems), and Q8 (Streaming Platform Search).
- **Relational Mapping Documentation:** Documented the conceptual-to-relational transformation rules and the entity-to-table mapping.
- **DBML Schema:** Created the DBML (Database Markup Language) schema definition at `docs/database_design/cineverse.dbml` for visual schema tooling.

### 2.2 Suhas Gangireddy -- ETL Pipeline and Data Engineering

Suhas was responsible for sourcing, cleaning, transforming, and loading all real-world data into the PostgreSQL database. His contributions include:

- **Data Sourcing:** Identified and acquired data from two complementary public sources: IMDb Non-Commercial Datasets (4 TSV files totaling approximately 3.5 GB uncompressed) and MovieLens Latest Small (ratings, tags, and links CSVs).
- **ETL Pipeline:** Built the complete extract-transform-load pipeline in Python using pandas, requests, and tqdm. The pipeline downloads raw data, filters to 500 target movies, joins across data sources using the MovieLens links file as a bridge, transforms column types and scales, and produces clean CSV files ready for PostgreSQL COPY.
- **Data Cleaning:** Resolved seven categories of real-world data quality issues including float-formatted integers in CSVs, non-ASCII character encoding problems, historical anomalies (Homer's birth year in 850 BC), orphan foreign keys after filtering, IMDb role category mapping, malformed JSON in character names, and duplicate composite keys.
- **SQL Queries:** Authored queries Q3 (Audience vs. Critic Score Divergence), Q4 (Mood-Based Recommendations), Q7 (Top Directors by Rating), and Q10 (Group Watch Suggestions).
- **Indexes:** Defined 30 performance indexes in `sql/04_indexes.sql` targeting frequently joined and filtered columns across the schema.
- **Load Scripts:** Created both the COPY-based bulk loader (`sql/02_load_data.sql`) and the portable INSERT-based alternative (`sql/02_insert_data.sql`).

### 2.3 Manasa Kumari -- Full-Stack Application Development

Manasa was responsible for building the complete application layer that brings the database to life as an interactive system. Her contributions include:

- **FastAPI Backend:** Implemented the Python FastAPI backend with 24 REST endpoints covering user management, dashboard statistics, multi-filter search, movie detail (8+ table join), recommendations, watchlist CRUD operations, group watch suggestions, database insights, and administrative transactions. The backend includes Pydantic models for request validation and CORS middleware for frontend integration.
- **React Frontend:** Developed 9 React page components (Login, Dashboard, Search, MovieDetail, Watchlist, Recommendations, GroupWatch, Insights, Admin) using React 18, Vite for build tooling, and TailwindCSS for responsive styling. The frontend communicates with the backend exclusively through JSON API calls.
- **SQL Queries:** Authored queries Q6 (Most Versatile Actors) and Q9 (Award Winners on Streaming).
- **Deployment:** Configured the complete development environment with the React dev server on port 5173, FastAPI on port 8000, and PostgreSQL on port 5432.
- **Demo Flow:** Designed and implemented the 10-step user journey that demonstrates the full breadth of the data model through the application interface.

### 2.4 Contribution Summary

| Deliverable | Aditya Kamat | Suhas Gangireddy | Manasa Kumari |
|-------------|:---:|:---:|:---:|
| Schema design (27 tables) | Lead | -- | -- |
| ER model and diagrams | Lead | -- | -- |
| Constraint definitions | Lead | -- | -- |
| ETL pipeline | -- | Lead | -- |
| Data sourcing (IMDb/MovieLens) | -- | Lead | -- |
| Data cleaning and validation | -- | Lead | -- |
| Performance indexes | -- | Lead | -- |
| FastAPI backend (24 endpoints) | -- | -- | Lead |
| React frontend (9 pages) | -- | -- | Lead |
| Query Q1: Top Rated by Genre | Author | -- | -- |
| Query Q2: Actor-Director Collaborations | Author | -- | -- |
| Query Q3: Audience vs. Critic Gap | -- | Author | -- |
| Query Q4: Mood Recommendations | -- | Author | -- |
| Query Q5: Hidden Gems | Author | -- | -- |
| Query Q6: Versatile Actors | -- | -- | Author |
| Query Q7: Top Directors by Rating | -- | Author | -- |
| Query Q8: Streaming Platform Search | Author | -- | -- |
| Query Q9: Award Winners Streaming | -- | -- | Author |
| Query Q10: Group Watch Suggestions | -- | Author | -- |

---

## 3. Database Design -- Schema Overview

### 3.1 Schema at a Glance

The CineVerse schema contains **27 tables** organized into **14 primary entities** and **13 bridge/junction tables** that resolve many-to-many relationships. The schema stores **31,426 rows** of real-world data sourced from IMDb and MovieLens. Every table enforces referential integrity through foreign keys, domain integrity through CHECK constraints, and entity integrity through primary keys (both surrogate SERIAL keys and composite keys).

### 3.2 Entity Summary

The 14 primary entities represent distinct real-world concepts in the film domain:

| # | Entity | Description | Primary Key |
|---|--------|-------------|-------------|
| 1 | **Movie** | Central catalog of films with metadata (title, year, runtime, ratings, budget, revenue, poster) | `movie_id` (SERIAL) |
| 2 | **Person** | Unified table for actors, directors, producers, and writers | `person_id` (SERIAL) |
| 3 | **RoleType** | Lookup table for role categories (Actor, Director, Producer, Writer) | `role_type_id` (SERIAL) |
| 4 | **Genre** | Normalized genre list (Action, Drama, Comedy, Sci-Fi, etc.) | `genre_id` (SERIAL) |
| 5 | **Distributor** | Film distribution companies | `distributor_id` (SERIAL) |
| 6 | **UserProfile** | Application users who rate and review movies | `user_id` (SERIAL) |
| 7 | **Tag** | Mood and theme tags for the recommendation engine (dark, funny, mind-bending) | `tag_id` (SERIAL) |
| 8 | **StreamingPlatform** | Streaming services (Netflix, Prime, Disney+, Hulu, etc.) | `platform_id` (SERIAL) |
| 9 | **Award** | Award ceremonies and categories (Oscar, Golden Globe, BAFTA, Cannes) | `award_id` (SERIAL) |
| 10 | **ProductionCompany** | Studios behind each film (Warner Bros, Disney, Universal, etc.) | `company_id` (SERIAL) |
| 11 | **Watchlist** | User-created personal watchlists | `watchlist_id` (SERIAL) |
| 12 | **WatchParty** | Group watch events with host, members, and planned date | `party_id` (SERIAL) |
| 13 | **RecommendationLog** | Persisted recommendation results with explanations | `recommendation_id` (SERIAL) |
| 14 | **Review** | User-written movie reviews with sentiment classification | `review_id` (SERIAL) |

### 3.3 Bridge/Junction Tables

The 13 bridge tables resolve many-to-many relationships and composite-key associations:

| # | Bridge Table | Resolves Relationship | Primary Key |
|---|---|---|---|
| 1 | **MovieCredit** | Movie -- Person (via RoleType) | `credit_id` (surrogate) + UNIQUE composite |
| 2 | **MovieGenre** | Movie -- Genre | (movie_id, genre_id) |
| 3 | **MovieDistributor** | Movie -- Distributor | (movie_id, distributor_id, region) |
| 4 | **MovieAvailability** | Movie -- StreamingPlatform | (movie_id, platform_id, region, access_type) |
| 5 | **MovieAward** | Movie -- Award (optionally Person) | `movie_award_id` (surrogate) + UNIQUE composite |
| 6 | **MovieProductionCompany** | Movie -- ProductionCompany | (movie_id, company_id) |
| 7 | **MovieTagRelevance** | Movie -- Tag | (movie_id, tag_id) |
| 8 | **UserRating** | UserProfile -- Movie | (user_id, movie_id) |
| 9 | **ExternalRating** | Movie -- External Rating Source | (movie_id, source_name) |
| 10 | **UserPreferenceTag** | UserProfile -- Tag | (user_id, tag_id) |
| 11 | **WatchlistItem** | Watchlist -- Movie | (watchlist_id, movie_id) |
| 12 | **WatchPartyMember** | WatchParty -- UserProfile | (party_id, user_id) |
| 13 | **WatchPartySuggestion** | WatchParty -- Movie | (party_id, movie_id) |

### 3.4 Key Relationships and Cardinalities

| # | Relationship | Cardinality | Resolved By |
|---|---|---|---|
| 1 | Movie -- Person (cast/crew) | M : N | MovieCredit (ternary: includes RoleType) |
| 2 | Movie -- Genre | M : N | MovieGenre |
| 3 | Movie -- StreamingPlatform | M : N | MovieAvailability (with region + access_type) |
| 4 | Movie -- Award | M : N | MovieAward (with optional Person link) |
| 5 | Movie -- ProductionCompany | M : N | MovieProductionCompany |
| 6 | Movie -- Distributor | M : N | MovieDistributor (with region) |
| 7 | Movie -- Tag | M : N | MovieTagRelevance (with relevance_score) |
| 8 | UserProfile -- Movie (rating) | M : N | UserRating (one rating per user-movie pair) |
| 9 | UserProfile -- Movie (review) | 1 : 1 per pair | Review (UNIQUE on user_id, movie_id) |
| 10 | UserProfile -- Tag (preference) | M : N | UserPreferenceTag |
| 11 | UserProfile -- Watchlist | 1 : M | Watchlist.user_id FK |
| 12 | Watchlist -- Movie | M : N | WatchlistItem |
| 13 | UserProfile -- WatchParty (host) | 1 : M | WatchParty.host_user_id FK |
| 14 | WatchParty -- UserProfile (members) | M : N | WatchPartyMember |
| 15 | WatchParty -- Movie (suggestions) | M : N | WatchPartySuggestion |
| 16 | UserProfile -- Movie (recommendation) | 1 : M | RecommendationLog |

### 3.5 ER Diagram

The full entity-relationship diagram is provided as a high-resolution image:

![ER Diagram -- Overview](database_design/overview_high_level.png)

---

## 4. Database Design -- Layer Architecture

The 27 tables are organized into six logical layers, each representing a cohesive domain within the movie database system. This layered organization was chosen to make the schema comprehensible at scale: each layer can be understood independently, and the inter-layer dependencies follow a clear top-down pattern where upper layers reference lower ones.

### 4.1 Layer 1: Core (6 tables)

The Core layer contains the foundational entities that every other layer depends upon. Movie is the central hub of the entire schema. Person stores all individuals in a unified table (actors, directors, producers, writers). RoleType is a lookup that categorizes the role a person plays on a film. MovieCredit is the ternary bridge that links movies to people via roles. Genre and MovieGenre provide normalized genre classification.

**Tables:** Movie, Person, RoleType, MovieCredit, Genre, MovieGenre

![Layer 1 -- Core Tables](database_design/layer1_core.png)

The Movie table is the most heavily referenced table in the schema, with foreign keys pointing to it from 12 other tables. It stores both IMDb-sourced metadata (title, year, runtime, rating, votes) and TMDb-enriched data (plot, budget, revenue, poster URL). The Person table deliberately avoids role-specific subtypes; a single Christopher Nolan row captures his work as director, producer, and writer, with the MovieCredit bridge tracking which role he fills on each specific film.

### 4.2 Layer 2: Users (4 tables)

The User layer models application users and their direct interactions with movies. UserProfile stores user accounts with demographics. UserRating captures the many-to-many rating relationship between users and movies, with a composite primary key ensuring one rating per user-movie pair. Review allows one textual review per user-movie pair, with sentiment classification. ExternalRating stores ratings from external aggregator sources (IMDb, Rotten Tomatoes, Metacritic) with source-specific scales.

**Tables:** UserProfile, UserRating, Review, ExternalRating

![Layer 2 -- User Tables](database_design/layer2_users.png)

The separation of UserRating (numeric score) from Review (textual commentary) is deliberate. Users frequently rate movies without writing reviews, and the two have different cardinality constraints: a user may update their numeric rating over time (via UPSERT), but each user-movie pair has at most one review, enforced by a UNIQUE constraint.

### 4.3 Layer 3: Discovery (4 tables)

The Discovery layer powers the mood-based recommendation engine that differentiates CineVerse from standard movie databases. Tag stores mood and theme labels (e.g., "mind-bending," "dark," "visually stunning"). MovieTagRelevance assigns a relevance score (0.0 to 1.0) between each tag and each movie. UserPreferenceTag records each user's affinity for specific tags. RecommendationLog persists recommendation results with explainable text.

**Tables:** Tag, MovieTagRelevance, UserPreferenceTag, RecommendationLog

![Layer 3 -- Discovery Tables](database_design/layer3_discovery.png)

The recommendation algorithm works by matching tags from a user's highly-rated movies to tags on unrated movies, producing a cumulative relevance score. The RecommendationLog table preserves these results so that the explanation can be displayed on demand without recomputing.

### 4.4 Layer 4: Streaming (2 tables)

The Streaming layer models where movies can be watched. StreamingPlatform stores platform metadata (name, country, website). MovieAvailability is the bridge table with a 4-column composite primary key (movie_id, platform_id, region, access_type) that captures the real-world fact that a single movie can appear on the same platform in the same region with different access types (e.g., included with Netflix subscription AND available to rent on Netflix).

**Tables:** StreamingPlatform, MovieAvailability

### 4.5 Layer 5: Industry (6 tables)

The Industry layer captures professional and commercial aspects of filmmaking. Award and MovieAward track ceremonies, categories, and results (won vs. nominated), with an optional person link that uses ON DELETE SET NULL. ProductionCompany and MovieProductionCompany store studio information. Distributor and MovieDistributor track distribution relationships with regional granularity.

**Tables:** Award, MovieAward, ProductionCompany, MovieProductionCompany, Distributor, MovieDistributor

### 4.6 Layer 6: Social (5 tables)

The Social layer enables collaborative features. Watchlist and WatchlistItem provide personal movie tracking with three status levels (unwatched, watching, watched). WatchParty, WatchPartyMember, and WatchPartySuggestion support group watch planning, where the system recommends movies that no party member has seen.

**Tables:** Watchlist, WatchlistItem, WatchParty, WatchPartyMember, WatchPartySuggestion

![Layer 4 -- Social Tables](database_design/layer4_social.png)

---

## 5. Design Decisions and Constraints

### 5.1 Three Key Design Decisions

The CineVerse schema reflects several deliberate design choices that balance normalization, real-world fidelity, and query performance. Three decisions stand out as particularly consequential.

#### Decision 1: Unified Person Table

In the film industry, a single individual frequently serves in multiple capacities. Christopher Nolan directs, produces, and writes. Clint Eastwood acts and directs. Creating separate Actor, Director, and Producer tables would either duplicate personal data (name, birth_year, death_year) across tables or require a fragile cross-table identity system with shared surrogate keys.

The unified Person table stores each individual exactly once, while the MovieCredit bridge table paired with the RoleType lookup captures the specific role a person played on each specific film. This design eliminates data redundancy for multi-role individuals, simplifies queries that need to find "all work by a person regardless of role," and follows the generalization/specialization pattern recommended for overlapping subtypes in relational modeling.

#### Decision 2: 4-Column Composite Primary Key on MovieAvailability

A single movie can appear on the same streaming platform in the same region with different access types. For example, a film might be available on Amazon Prime Video in the US both via subscription (included with Prime) and for rent ($3.99). The four-column composite primary key `(movie_id, platform_id, region, access_type)` captures this real-world reality. Reducing the key to fewer columns would either lose information (collapsing subscription and rental into one row) or require artificial constraints that do not reflect how streaming platforms actually operate.

This is the widest composite primary key in the schema and demonstrates that composite keys are not limited to two columns when the domain demands finer granularity.

#### Decision 3: ON DELETE SET NULL on MovieAward.person_id

Awards are sometimes given to individuals (Best Actor, Best Director) and sometimes to films as a whole (Best Picture). The `person_id` column in MovieAward is therefore nullable. When an award is associated with a person and that person's record is deleted from the database, the award history for the film should be preserved -- only the person linkage should be nullified. ON DELETE SET NULL achieves exactly this: the MovieAward row survives, recording that the film won the award, but the person reference becomes NULL. This is semantically distinct from ON DELETE CASCADE, which would destroy the entire award record, and from RESTRICT, which would prevent deleting the person entirely.

### 5.2 Constraint Strategy Summary

CineVerse employs a defense-in-depth constraint strategy. Every constraint type supported by PostgreSQL is utilized to ensure data integrity at the database level, independent of any application logic. The following table summarizes the constraint counts across the schema:

| Constraint Type | Count | Representative Examples |
|-----------------|-------|------------------------|
| **PRIMARY KEY (surrogate)** | 15 | `Movie.movie_id SERIAL PRIMARY KEY`, `Person.person_id SERIAL PRIMARY KEY`, `Award.award_id SERIAL PRIMARY KEY` |
| **PRIMARY KEY (composite)** | 11 | `UserRating(user_id, movie_id)`, `MovieGenre(movie_id, genre_id)`, `MovieAvailability(movie_id, platform_id, region, access_type)` |
| **FOREIGN KEY** | 40+ | `MovieCredit.movie_id REFERENCES Movie(movie_id)`, `UserRating.user_id REFERENCES UserProfile(user_id)`, `WatchParty.host_user_id REFERENCES UserProfile(user_id)` |
| **UNIQUE** | 11 | `Movie.imdb_id`, `UserProfile.username`, `uq_movie_person_role_char(movie_id, person_id, role_type_id, character_name)` |
| **CHECK** | 18 | `rating BETWEEN 0.0 AND 10.0`, `runtime_minutes > 0`, `access_type IN ('subscription','rent','buy','free','theater')` |
| **NOT NULL** | 20+ | `Movie.title NOT NULL`, `Movie.imdb_id NOT NULL`, `UserRating.rating NOT NULL`, `Review.review_text NOT NULL` |
| **ON DELETE CASCADE** | 8 | `MovieGenre.movie_id`, `UserRating.user_id`, `WatchlistItem.watchlist_id`, `WatchPartyMember.party_id` |
| **ON DELETE SET NULL** | 2 | `MovieAward.person_id`, `WatchPartySuggestion.suggested_by` |
| **DEFAULT** | 5 | `CURRENT_TIMESTAMP`, `CURRENT_DATE`, `'English'`, `'unwatched'`, `'US'` |

![Constraints Summary](database_design/constraints_summary.png)

---

## 6. Relational Mapping

### 6.1 Mapping Rules Applied

The conceptual ER model was systematically transformed into a relational schema following four standard mapping rules. Each rule is documented below with its application to CineVerse tables.

#### Rule 1: Strong Entity to Table

Every strong entity in the conceptual model became a table with its own surrogate SERIAL primary key. Attributes of the entity became columns, with domain restrictions mapped to CHECK constraints and optionality mapped to NOT NULL (or its absence). This rule produced 14 entity tables: Movie, Person, RoleType, Genre, Distributor, UserProfile, Tag, StreamingPlatform, Award, ProductionCompany, Watchlist, WatchParty, RecommendationLog, and Review.

#### Rule 2: M:N Relationship to Bridge Table

Every many-to-many relationship was resolved into a bridge table with a composite primary key referencing both parent tables. The bridge table stores only foreign keys and relationship-specific attributes (e.g., `relevance_score` in MovieTagRelevance, `billing_order` in MovieCredit). This rule produced 11 pure bridge tables: MovieGenre, MovieDistributor, MovieAvailability, MovieProductionCompany, MovieTagRelevance, UserRating, ExternalRating, UserPreferenceTag, WatchlistItem, WatchPartyMember, and WatchPartySuggestion.

#### Rule 3: 1:M Relationship to Foreign Key

Every one-to-many relationship was implemented by placing a foreign key in the "many" side table. For example, `Watchlist.user_id` references `UserProfile(user_id)` because one user can have many watchlists, but each watchlist belongs to exactly one user. Similarly, `WatchParty.host_user_id` references `UserProfile(user_id)`.

#### Rule 4: Ternary Relationship to Surrogate Key with UNIQUE Constraint

The ternary relationship MovieCredit (linking Movie, Person, and RoleType) was given a surrogate `credit_id` primary key because the natural composite key would include a nullable column (`character_name`). A multi-column UNIQUE constraint `(movie_id, person_id, role_type_id, character_name)` prevents duplicate entries while allowing the same actor to play multiple characters in the same film. The same pattern was applied to MovieAward, which has a ternary relationship between Movie, Award, and optionally Person.

### 6.2 Result: 27 Tables in 3NF

The mapping process produced 27 tables, all in Third Normal Form (3NF). Bridge tables are the primary mechanism for preventing data duplication:

- Without MovieGenre, genre data would be stored as a comma-separated string in Movie (violating 1NF) or duplicated across rows.
- Without MovieCredit, person attributes (name, birth_year) would be repeated for every film the person appears in.
- Without MovieAvailability, streaming data would be embedded in Movie, making it impossible to represent the same movie on multiple platforms in multiple regions with different access types.

Each bridge table stores only foreign keys and relationship-specific attributes, ensuring zero redundancy.

### 6.3 Entity-to-Table Mapping Reference

| Conceptual Entity | Table Name | Key Column(s) | Table Type |
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

![Relational Mapping Diagram](database_design/relational_mapping.png)

---

## 7. DDL in Action -- MovieCredit Table

The MovieCredit table is the single best illustration of the CineVerse schema's constraint strategy because it demonstrates every major constraint type within a single CREATE TABLE statement. This ternary bridge table links three entities (Movie, Person, RoleType) and showcases:

- **Surrogate Primary Key** (`credit_id SERIAL PRIMARY KEY`)
- **Three Foreign Keys** with NOT NULL enforcement
- **ON DELETE CASCADE** on movie_id and person_id (deleting a movie or person removes their credits)
- **CHECK constraint** on billing_order (must be positive)
- **Multi-column UNIQUE constraint** preventing duplicate credits while allowing the same actor to play multiple characters
- **Nullable column** (character_name) within a UNIQUE constraint

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

**Why a surrogate PK instead of a composite PK?** The natural candidate for a primary key would be `(movie_id, person_id, role_type_id, character_name)`. However, `character_name` is nullable (directors and producers do not have character names), and PostgreSQL does not allow NULL values in primary key columns. The surrogate `credit_id` sidesteps this limitation, while the UNIQUE constraint enforces the same no-duplicates guarantee on the natural key columns.

**Why ON DELETE CASCADE on both movie_id and person_id?** If a movie is removed from the catalog, its credits have no meaning and should be removed. Similarly, if a person is deleted, their credit records should not remain as orphaned rows. CASCADE on both foreign keys ensures referential integrity is maintained automatically.

**Why CHECK (billing_order > 0)?** Billing order represents the position of a cast or crew member in the credits sequence (1 for top-billed, 2 for second-billed, etc.). Zero and negative values are semantically meaningless, so the CHECK constraint enforces a positive integer domain.

---

## 8. SQL Queries (Q1--Q10)

The following 10 queries demonstrate advanced SQL techniques across the CineVerse schema. Each query addresses a distinct analytical or operational need and is designed to exercise specific relational concepts. The queries are presented in order with their business purpose, tables involved, SQL techniques used, and the complete SQL code.

---

### Query 1: Top-Rated Movies by Genre

**Business Purpose:** Identify the highest-rated movies within each genre based on community ratings, enabling genre-specific "best of" lists while filtering out movies with insufficient rating counts to ensure statistical reliability.

**Tables Joined:** Movie, MovieGenre, Genre, UserRating (4 tables)

**SQL Techniques:** RANK window function with PARTITION BY, AVG/COUNT aggregates, HAVING (minimum vote threshold), subquery in FROM clause

```sql
-- top 3 rated movies per genre, requires at least 5 user ratings to qualify
SELECT genre_name, title, release_year, avg_user_rating, num_ratings, genre_rank
FROM (
    SELECT
        g.genre_name,
        m.title,
        m.release_year,
        ROUND(AVG(ur.rating)::numeric, 2) AS avg_user_rating,
        COUNT(ur.user_id) AS num_ratings,
        RANK() OVER (PARTITION BY g.genre_name ORDER BY AVG(ur.rating) DESC) AS genre_rank
    FROM Movie m
    JOIN MovieGenre mg ON mg.movie_id = m.movie_id
    JOIN Genre g ON g.genre_id = mg.genre_id
    JOIN UserRating ur ON ur.movie_id = m.movie_id
    GROUP BY g.genre_name, m.movie_id, m.title, m.release_year
    HAVING COUNT(ur.user_id) >= 5
) ranked
WHERE genre_rank <= 3
ORDER BY genre_name, genre_rank;
```

**How it works:** The inner subquery computes the average user rating per movie per genre, filters to movies with at least 5 ratings (HAVING), and assigns a rank within each genre partition using the RANK window function. The outer query filters to only the top 3 per genre. RANK (not ROW_NUMBER) is used so that ties receive the same rank, which is appropriate for rating-based rankings.

---

### Query 2: Actor-Director Collaborations

**Business Purpose:** Discover recurring creative partnerships between actors and directors -- pairs who have worked together on two or more films. This reveals the industry's most prolific collaborations (e.g., DiCaprio-Scorsese, Hanks-Spielberg).

**Tables Joined:** MovieCredit (self-joined twice), RoleType (joined twice), Person (joined twice), Movie (7 table references)

**SQL Techniques:** Self-JOIN on MovieCredit, role-based filtering via RoleType, STRING_AGG for concatenated movie titles, COUNT DISTINCT, GROUP BY with HAVING

```sql
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
```

**How it works:** The query performs a self-join on MovieCredit: one alias (`mc_actor`) filters for Actor roles and another alias (`mc_director`) filters for Director roles on the same movie (`mc_director.movie_id = mc_actor.movie_id`). This produces all actor-director pairs per film. Grouping by actor and director names, then filtering with HAVING for 2+ shared films, reveals recurring collaborations. STRING_AGG concatenates the shared movie titles into a semicolon-separated list.

---

### Query 3: Audience vs. Critic Score Divergence

**Business Purpose:** Identify movies where community user ratings diverge significantly from IMDb critic scores, classifying each as an "Audience Favorite," "Critic Favorite," or "Consensus" film. This is valuable for understanding taste biases and finding underappreciated films.

**Tables Joined:** Movie, UserRating, ExternalRating (3 tables)

**SQL Techniques:** CASE expression for categorical labeling, AVG/COUNT aggregates, ABS for absolute divergence ordering, HAVING (minimum rating count), arithmetic expressions

```sql
-- movies where user ratings diverge significantly from IMDb critic scores
SELECT
    m.title,
    m.release_year,
    ROUND(AVG(ur.rating)::numeric, 2) AS avg_user_rating,
    er.score AS imdb_score,
    ROUND((AVG(ur.rating) - er.score)::numeric, 2) AS user_vs_critic_gap,
    COUNT(ur.user_id) AS num_user_ratings,
    CASE
        WHEN AVG(ur.rating) - er.score > 1.0 THEN 'Audience Favorite'
        WHEN er.score - AVG(ur.rating) > 1.0 THEN 'Critic Favorite'
        ELSE 'Consensus'
    END AS gap_category
FROM Movie m
JOIN UserRating ur ON ur.movie_id = m.movie_id
JOIN ExternalRating er ON er.movie_id = m.movie_id AND er.source_name = 'IMDb'
GROUP BY m.movie_id, m.title, m.release_year, er.score
HAVING COUNT(ur.user_id) >= 3
ORDER BY ABS(AVG(ur.rating) - er.score) DESC
LIMIT 25;
```

**How it works:** The query joins user ratings with the IMDb external rating for each movie, computes the average user rating, and calculates the gap between audience and critic scores. A CASE expression classifies the gap: positive gaps greater than 1.0 indicate audience favorites (users rate higher than critics), negative gaps greater than 1.0 indicate critic favorites, and everything else is consensus. Results are ordered by the absolute gap to surface the most divisive films first.

---

### Query 4: Mood-Based Recommendations

**Business Purpose:** Generate personalized movie recommendations for a specific user by matching mood/theme tags from their highly-rated films to unrated films, producing an explainable recommendation with matching tags listed. This powers the Recommendation Lab screen.

**Tables Joined:** MovieTagRelevance, Tag, Movie, UserRating (4 tables, with correlated subquery referencing UserRating, MovieTagRelevance, Tag)

**SQL Techniques:** Correlated subquery (IN clause to derive user's preferred tags), LEFT JOIN with IS NULL anti-pattern (exclude already-rated movies), STRING_AGG, SUM aggregate for recommendation scoring

```sql
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
```

**How it works:** The subquery extracts mood tags that are strongly associated (relevance >= 0.6) with movies the user has rated highly (>= 8.0). The main query then finds unrated movies that share those tags (LEFT JOIN + IS NULL pattern to exclude already-rated films) and computes a recommendation score by summing the relevance scores of all matching tags. The result includes the list of matching tags (via STRING_AGG), making the recommendation *explainable* -- the user can see exactly which mood tags drove each suggestion.

---

### Query 5: Hidden Gems

**Business Purpose:** Surface high-quality movies that have received little mainstream attention -- films with high user ratings but below-median IMDb vote counts. These are the "hidden gems" that deserve more visibility.

**Tables Joined:** Movie, UserRating (2 tables)

**SQL Techniques:** Scalar subquery with PERCENTILE_CONT (median calculation), LOG function for weighted scoring, compound HAVING (minimum ratings AND minimum average), AVG/COUNT aggregates

```sql
-- high-rated movies with below-median vote counts (hidden gems)
SELECT
    m.title,
    m.release_year,
    ROUND(AVG(ur.rating)::numeric, 2) AS avg_user_rating,
    COUNT(ur.user_id) AS num_ratings,
    m.imdb_votes,
    m.imdb_rating,
    ROUND((AVG(ur.rating) * LOG(COUNT(ur.user_id) + 1))::numeric, 2) AS weighted_score
FROM Movie m
JOIN UserRating ur ON ur.movie_id = m.movie_id
WHERE m.imdb_votes < (SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY imdb_votes) FROM Movie)
GROUP BY m.movie_id, m.title, m.release_year, m.imdb_votes, m.imdb_rating
HAVING COUNT(ur.user_id) >= 3 AND AVG(ur.rating) >= 7.5
ORDER BY avg_user_rating DESC, num_ratings DESC
LIMIT 20;
```

**How it works:** The WHERE clause uses a scalar subquery with PERCENTILE_CONT(0.5) to compute the median IMDb vote count across all movies, filtering to only those below the median (i.e., less popular). The HAVING clause then requires at least 3 user ratings and an average of 7.5 or higher. A weighted score multiplies the average rating by the log of the rating count, balancing quality with confidence. This surfaces genuinely good films that flew under the radar.

---

### Query 6: Most Versatile Actors

**Business Purpose:** Rank actors by the number of distinct genres they have appeared in, identifying the most versatile performers in the database. This rewards range over volume -- an actor in 5 genres across 6 films ranks higher than one in 2 genres across 20 films.

**Tables Joined:** Person, MovieCredit, RoleType, MovieGenre, Genre (5 tables)

**SQL Techniques:** DENSE_RANK window function, COUNT DISTINCT (both genres and movies), STRING_AGG for genre list, HAVING (minimum film count), 4 inner JOINs

```sql
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
```

**How it works:** The query joins Person through MovieCredit (filtered to Actor role) to MovieGenre and Genre, then counts the distinct genres per actor. DENSE_RANK assigns a versatility rank without gaps (if two actors tie at 8 genres, both get rank 1, and the next gets rank 2). The HAVING clause requires at least 3 films to exclude actors with only one or two appearances. STRING_AGG produces a comma-separated genre list for display.

---

### Query 7: Top Directors by Rating

**Business Purpose:** Rank directors by their average IMDb rating and total audience reach, providing a quality-and-popularity assessment of directorial careers.

**Tables Joined:** Person, MovieCredit, RoleType, Movie, UserRating (5 tables)

**SQL Techniques:** LEFT JOIN (to include directors whose films have no user ratings), AVG/SUM/COUNT aggregates, STRING_AGG for filmography, HAVING (minimum film count), NULLS handling

```sql
-- directors ranked by average IMDb rating and total audience reach
SELECT
    p.name AS director_name,
    COUNT(DISTINCT m.movie_id) AS num_films,
    ROUND(AVG(m.imdb_rating)::numeric, 2) AS avg_imdb_rating,
    SUM(m.imdb_votes) AS total_votes,
    ROUND(AVG(ur.rating)::numeric, 2) AS avg_user_rating,
    COUNT(DISTINCT ur.user_id) AS unique_raters,
    STRING_AGG(DISTINCT m.title, '; ' ORDER BY m.title) AS films
FROM Person p
JOIN MovieCredit mc ON mc.person_id = p.person_id
JOIN RoleType rt ON rt.role_type_id = mc.role_type_id AND rt.role_name = 'Director'
JOIN Movie m ON m.movie_id = mc.movie_id
LEFT JOIN UserRating ur ON ur.movie_id = m.movie_id
WHERE m.imdb_rating IS NOT NULL
GROUP BY p.person_id, p.name
HAVING COUNT(DISTINCT m.movie_id) >= 3
ORDER BY avg_imdb_rating DESC, total_votes DESC
LIMIT 20;
```

**How it works:** The query traverses from Person through MovieCredit (filtered to Director role) to Movie, then optionally joins UserRating to capture community rating data. The LEFT JOIN ensures directors whose films lack user ratings are still included with NULL community metrics. The HAVING clause requires at least 3 films to provide a meaningful average. STRING_AGG produces a semicolon-separated filmography list.

---

### Query 8: Streaming Platform Search

**Business Purpose:** Help users find movies of specific genres available via subscription on their preferred streaming platforms in a given region. This directly powers the search screen's platform filter functionality.

**Tables Joined:** Movie, MovieAvailability, StreamingPlatform, MovieGenre, Genre (5 tables)

**SQL Techniques:** DISTINCT (deduplication across access types), multi-value IN filters, WHERE with equality and IN predicates, ORDER BY with NULLS LAST, 4 inner JOINs

```sql
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
```

**How it works:** This query is a straightforward multi-filter search that demonstrates the power of the normalized schema. Because genres, platforms, and availability are stored in separate normalized tables connected by bridge tables, the query can filter on any combination of genre names, platform names, regions, and access types using simple WHERE predicates. DISTINCT eliminates duplicates that arise when a movie has multiple qualifying genres. NULLS LAST ensures movies without IMDb ratings sort to the bottom.

---

### Query 9: Award Winners on Streaming

**Business Purpose:** Find award-winning movies that are currently available for subscription streaming in the US. This combines the Award subsystem with the Streaming subsystem, answering the question: "What Oscar winners can I watch tonight?"

**Tables Joined:** Movie, MovieAward, Award, MovieAvailability, StreamingPlatform (5 tables)

**SQL Techniques:** 5-table JOIN with filter on join condition (`ma2.result = 'won'`), STRING_AGG (two separate aggregations: awards and platforms), COUNT DISTINCT, date comparison with CURRENT_DATE, HAVING, GROUP BY

```sql
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
```

**How it works:** The query joins the Award subsystem (MovieAward filtered to `result = 'won'`, Award for names and categories) with the Streaming subsystem (MovieAvailability filtered to US subscriptions, StreamingPlatform for platform names). The date check `(ma.end_date IS NULL OR ma.end_date >= CURRENT_DATE)` ensures only currently available titles are shown. Two separate STRING_AGG calls produce the award list and the platform list, while COUNT DISTINCT tallies the number of distinct awards won.

---

### Query 10: Group Watch Suggestions

**Business Purpose:** Recommend movies for a specific watch party that no member has already seen, ranked by community rating. This powers the Group Watch screen and ensures every suggestion is fresh for the entire party.

**Tables Joined:** Movie, UserRating, MovieGenre, Genre, WatchPartyMember (5 tables, with NOT EXISTS correlated subquery)

**SQL Techniques:** NOT EXISTS correlated subquery (anti-join to exclude movies any member has seen), GROUP BY with HAVING, AVG/COUNT aggregates, STRING_AGG for genre list

```sql
-- movies no watch party member has seen, ranked by community rating
SELECT
    m.title,
    m.release_year,
    m.imdb_rating,
    ROUND(AVG(ur.rating)::numeric, 2) AS avg_user_rating,
    COUNT(DISTINCT ur.user_id) AS times_rated,
    STRING_AGG(DISTINCT g.genre_name, ', ' ORDER BY g.genre_name) AS genres
FROM Movie m
JOIN UserRating ur ON ur.movie_id = m.movie_id
JOIN MovieGenre mg ON mg.movie_id = m.movie_id
JOIN Genre g ON g.genre_id = mg.genre_id
WHERE NOT EXISTS (
    SELECT 1 FROM WatchPartyMember wpm
    JOIN UserRating seen ON seen.user_id = wpm.user_id AND seen.movie_id = m.movie_id
    WHERE wpm.party_id = 1
)
GROUP BY m.movie_id, m.title, m.release_year, m.imdb_rating
HAVING COUNT(DISTINCT ur.user_id) >= 3
ORDER BY avg_user_rating DESC
LIMIT 10;
```

**How it works:** The NOT EXISTS subquery is the core of this query. For each candidate movie in the outer query, the subquery checks whether any member of watch party 1 has rated that movie (a rating implies they have seen it). If even one member has rated the movie, NOT EXISTS returns FALSE and the movie is excluded. This anti-join pattern is more efficient than LEFT JOIN + IS NULL for correlated existence checks because PostgreSQL can short-circuit the subquery as soon as the first matching row is found. The remaining movies are ranked by community average rating.

---

### 8.11 Query Technique Summary Matrix

| Query | Window Function | STRING_AGG | CASE | NOT EXISTS | PERCENTILE_CONT | Subquery | HAVING | Multi-JOIN |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Q01 Top Rated by Genre | RANK | -- | -- | -- | -- | Derived table | Yes | 4 tables |
| Q02 Collaborations | -- | Yes | -- | -- | -- | -- | Yes | 7 references |
| Q03 Audience vs. Critic | -- | -- | Yes | -- | -- | -- | Yes | 3 tables |
| Q04 Mood Recommendations | -- | Yes | -- | -- | -- | IN subquery | -- | 4 tables |
| Q05 Hidden Gems | -- | -- | -- | -- | Yes | Scalar subquery | Yes | 2 tables |
| Q06 Versatile Actors | DENSE_RANK | Yes | -- | -- | -- | -- | Yes | 5 tables |
| Q07 Top Directors | -- | Yes | -- | -- | -- | -- | Yes | 5 tables |
| Q08 Streaming Search | -- | -- | -- | -- | -- | -- | -- | 5 tables |
| Q09 Award Winners Streaming | -- | Yes | -- | -- | -- | -- | Yes | 5 tables |
| Q10 Group Watch | -- | Yes | -- | Yes | -- | Correlated | Yes | 5 tables |

---

## 9. Data Sources and Volume

### 9.1 Data Source Overview

CineVerse uses three public data sources that complement each other. IMDb provides the authoritative movie catalog and cast/crew data. MovieLens provides user rating behavior and discovery tags. TMDb fills in visual and financial metadata. By merging these through shared identifiers, the database achieves both structural depth and realistic user interaction data.

| Source | Type | URL | Data Used |
|--------|------|-----|-----------|
| **IMDb Non-Commercial Datasets** | Bulk TSV files (gzipped) | https://developer.imdb.com/non-commercial-datasets/ | Movie metadata, person data, cast/crew credits, IMDb ratings |
| **MovieLens Latest Small** | CSV archive (zip) | https://grouplens.org/datasets/movielens/latest/ | User ratings (scaled 0--10), user-generated mood/theme tags, cross-reference links |
| **TMDb API** | REST API (JSON) | https://developer.themoviedb.org/ | Poster images, plot summaries, budget/revenue, production countries |

### 9.2 IMDb Non-Commercial Datasets

Four TSV files were downloaded from IMDb's public dataset server, totaling approximately 3.5 GB uncompressed:

| File | Size (approx.) | Contents | Key Columns Used |
|------|----------------|----------|-----------------|
| `title.basics.tsv` | 800 MB | Every title in IMDb (movies, TV, shorts) | tconst, titleType, primaryTitle, startYear, runtimeMinutes, genres |
| `title.ratings.tsv` | 22 MB | Average ratings and vote counts | tconst, averageRating, numVotes |
| `name.basics.tsv` | 750 MB | Every person in IMDb | nconst, primaryName, birthYear, deathYear, primaryProfession |
| `title.principals.tsv` | 2 GB | Cast and crew credits per title | tconst, nconst, ordering, category, characters |

**Filtering applied:** Only movies (titleType = 'movie') from 1970 onward with 10,000+ IMDb votes that also appear in MovieLens were retained. This reduced approximately 11 million IMDb titles to **500 movies**. Person records were filtered to only those who appear in the title.principals credits for the selected 500 movies, yielding **5,166 people** and **10,021 credit records**.

### 9.3 MovieLens Latest Small

| File | Contents | How Used |
|------|----------|----------|
| `ratings.csv` | User-movie rating pairs (0.5--5.0 scale) | Mapped via links.csv, scaled to 0.0--10.0, limited to 200 users |
| `tags.csv` | User-generated freetext tags | Top 200 tags by frequency became Tag table; tag-movie co-occurrence became MovieTagRelevance |
| `links.csv` | Bridge: MovieLens movieId to IMDb tconst to TMDb tmdb_id | Critical cross-reference linking all three data sources |
| `movies.csv` | Movie titles and genres | Cross-validation only |

The links.csv file is the linchpin of the entire data integration strategy. It provides the IMDb ID for each MovieLens movie, allowing user ratings from MovieLens to be joined with metadata from IMDb and enrichment from TMDb on the same movie.

### 9.4 TMDb API

For each of the 500 movies, a GET request to the TMDb API retrieved poster images, plot summaries, budget, revenue, production countries, and original language. This enrichment step is optional -- the database loads and functions fully without it, with NULL values in the enriched columns.

### 9.5 Data Cleaning Challenges

Seven categories of real-world data quality issues required systematic cleaning:

| # | Issue | Problem | Fix |
|---|-------|---------|-----|
| 1 | Float-formatted integers | Pandas saves nullable integers as floats (1924.0 instead of 1924); PostgreSQL COPY rejects these | Converted float64 to pandas Int64 (nullable integer) dtype |
| 2 | Non-ASCII encoding | IMDb contains accented characters; PostgreSQL on Windows defaults to WIN1252 | Stripped non-ASCII characters; COPY commands use ENCODING 'UTF8' |
| 3 | Historical anomalies | Homer listed with birth_year=850, death_year=800; fails CHECK (death_year >= birth_year) | Detected and set both years to NULL |
| 4 | Orphan foreign keys | After filtering to 500 movies, some credits referenced people not in filtered Person table | Validation script checks all FK relationships and removes orphan rows |
| 5 | IMDb role mapping | IMDb uses granular categories (actor, actress, self, composer); schema uses 4 roles | Mapped: actor/actress/self to Actor, director to Director, producer to Producer, others to Writer |
| 6 | Character name parsing | IMDb stores character names as JSON arrays; some entries malformed | Parse JSON, extract first element, fall back to raw string truncated to 255 chars |
| 7 | Duplicate composite keys | After joining and mapping, some duplicate (movie_id, person_id, role_type_id, character_name) tuples | Dropped duplicates keeping first occurrence; reassigned sequential credit IDs |

### 9.6 Data Volume -- Complete Row Counts

| Table | Rows | Primary Source |
|-------|------|----------------|
| Movie | 500 | IMDb title.basics (filtered) |
| Person | 5,166 | IMDb name.basics |
| MovieCredit | 10,021 | IMDb title.principals |
| RoleType | 4 | Manual (Actor, Director, Producer, Writer) |
| Genre | 20 | Extracted from IMDb genres |
| MovieGenre | 1,342 | IMDb genre strings (split and normalized) |
| Distributor | 20 | Curated list of major distributors |
| MovieDistributor | 500 | Assigned with real distributor names |
| UserProfile | 200 | MovieLens user IDs (remapped 1--200) |
| UserRating | 9,874 | MovieLens ratings (scaled 0.5--5.0 to 0.0--10.0) |
| ExternalRating | 500 | IMDb averageRating + numVotes |
| Tag | 200 | MovieLens user tags (top 200 by frequency) |
| MovieTagRelevance | 754 | Tag-movie co-occurrence frequency scores |
| UserPreferenceTag | -- | Derived from user rating patterns |
| StreamingPlatform | 10 | Curated (Netflix, Prime, Disney+, Hulu, Max, etc.) |
| MovieAvailability | 995 | 1--3 random platforms per movie |
| Award | 15 | Oscar, Golden Globe, BAFTA, Cannes categories |
| MovieAward | 158 | Wins and nominations for top 80 movies |
| ProductionCompany | 25 | Major studios (Warner Bros, Disney, Universal, etc.) |
| MovieProductionCompany | 749 | 1--2 studios per movie |
| Review | -- | User-submitted reviews |
| RecommendationLog | -- | Generated recommendation records |
| Watchlist | 50 | One default watchlist per first 50 users |
| WatchlistItem | 219 | 2--7 random movies per watchlist |
| WatchParty | 15 | Group watch events |
| WatchPartyMember | 43 | 2--4 members per party |
| WatchPartySuggestion | 46 | 2--4 movie suggestions per party |
| **Total** | **31,426** | **Average: ~1,309 rows per table** |

### 9.7 Key Data Counts

| Metric | Count |
|--------|-------|
| Total Movies | 500 |
| Total People (actors, directors, etc.) | 5,166 |
| Total Credits (movie-person-role links) | 10,021 |
| Total User Ratings | 9,874 |
| Total Tables | 27 |
| Total Rows | 31,426 |

---

## 10. Application Architecture

### 10.1 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend** | React + Vite + TailwindCSS | React 18, Vite 5 | Single-page application with responsive UI and utility-first styling |
| **Backend** | Python FastAPI | FastAPI 0.100+ | RESTful API server with automatic OpenAPI documentation and Pydantic validation |
| **Database** | PostgreSQL | 14+ | Relational data storage with full constraint enforcement |
| **ETL** | Python (pandas, requests, tqdm) | -- | Data sourcing, cleaning, transformation, and loading pipeline |

### 10.2 Architecture Diagram

```
+---------------------------+       +---------------------------+       +---------------------------+
|                           |       |                           |       |                           |
|     FRONTEND              |       |     BACKEND               |       |     DATABASE              |
|                           |       |                           |       |                           |
|   React 18 + Vite         |       |   Python FastAPI          |       |   PostgreSQL              |
|   TailwindCSS             |       |                           |       |                           |
|                           |       |   24 REST Endpoints       |       |   27 Tables               |
|   9 Page Components:      | HTTP  |                           |  SQL  |   31,426 Rows             |
|   - Login                 |------>|   /api/users              |------>|                           |
|   - Dashboard             |       |   /api/movies/search      |       |   15 Surrogate PKs        |
|   - Search                | JSON  |   /api/movies/{id}        |Results|   11 Composite PKs        |
|   - Movie Detail          |<------|   /api/recommendations    |<------|   40+ Foreign Keys        |
|   - Watchlist             |       |   /api/watchlist           |       |   18 CHECK Constraints    |
|   - Recommendations       |       |   /api/group-watch        |       |   11 UNIQUE Constraints   |
|   - Group Watch           |       |   /api/insights           |       |   30 Performance Indexes  |
|   - Insights              |       |   /api/admin              |       |                           |
|   - Admin                 |       |                           |       |   Database: cineverse     |
|                           |       |                           |       |                           |
|   Port: 5173              |       |   Port: 8000              |       |   Port: 5432              |
|                           |       |                           |       |                           |
+---------------------------+       +---------------------------+       +---------------------------+
        Browser                          Backend API                         PostgreSQL Server
```

### 10.3 Application Screens

The application provides 9 distinct screens, each designed to demonstrate specific database concepts and query patterns:

| # | Screen | Description | Key Database Concepts |
|---|--------|-------------|----------------------|
| 1 | **Login** | Netflix-style profile selection from existing UserProfile records | SELECT from UserProfile |
| 2 | **Dashboard** | Aggregate stats (total movies, users, ratings), Top Rated row, Trending row, Recently Released row | COUNT, AVG aggregates across Movie, UserRating |
| 3 | **Search** | Multi-filter search: title, genre, year range, minimum rating, streaming platform, director, actor, mood tag | Multi-table JOIN with dynamic WHERE filters (Movie, Person, Genre, StreamingPlatform, MovieAvailability, MovieGenre, MovieCredit, Tag, MovieTagRelevance) |
| 4 | **Movie Detail** | Complete movie profile: metadata, cast/crew, genres, user ratings, external ratings, streaming availability, awards, mood tags, reviews, similar movies | 8+ table JOIN demonstrating the full relational model |
| 5 | **Watchlist** | Personal watchlist with add, mark as watching/watched, remove | INSERT, UPDATE, DELETE transactions on Watchlist, WatchlistItem |
| 6 | **Recommendation Lab** | Mood-based explainable recommendations: select tags, filter by platform and minimum rating, view matching tags and scores | Q04 pattern: subquery-based tag matching, LEFT JOIN exclusion |
| 7 | **Group Watch** | Select a watch party, receive group-optimized suggestions (movies no member has seen) | Q10 pattern: NOT EXISTS anti-join, correlated subqueries |
| 8 | **Database Insights** | Interactive query runner exposing all 10 complex queries from the UI | Executes Q01--Q10 on demand with tabular results |
| 9 | **Admin** | Administrative panel: insert movies, add streaming availability, submit ratings/reviews | INSERT with constraint validation, ON CONFLICT handling |

### 10.4 API Endpoints

The FastAPI backend exposes 24 REST endpoints organized by functional area:

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 1 | GET | `/api/users` | List all user profiles |
| 2 | GET | `/api/stats` | Dashboard aggregate statistics |
| 3 | GET | `/api/movies/top` | Top-rated movies |
| 4 | GET | `/api/movies/trending` | Trending movies (recent high ratings) |
| 5 | GET | `/api/movies/recent` | Recently released movies |
| 6 | GET | `/api/movies/search` | Multi-filter search (title, genre, year, rating, platform, director, actor, tag) |
| 7 | GET | `/api/movies/{movie_id}` | Full movie detail (8+ table join) |
| 8 | GET | `/api/movies/{movie_id}/similar` | Similar movies by genre/tag overlap |
| 9 | GET | `/api/genres` | All genres |
| 10 | GET | `/api/platforms` | All streaming platforms |
| 11 | GET | `/api/tags` | All mood/theme tags |
| 12 | GET | `/api/recommendations/{user_id}` | Personalized mood-based recommendations |
| 13 | GET | `/api/watchlist/{user_id}` | User's watchlist items |
| 14 | POST | `/api/watchlist` | Add movie to watchlist |
| 15 | PUT | `/api/watchlist/{watchlist_id}/{movie_id}` | Update watched status |
| 16 | DELETE | `/api/watchlist/{watchlist_id}/{movie_id}` | Remove from watchlist |
| 17 | POST | `/api/ratings` | Submit a movie rating |
| 18 | POST | `/api/reviews` | Submit a movie review |
| 19 | GET | `/api/group-watch/parties` | List all watch parties |
| 20 | GET | `/api/group-watch/{party_id}` | Group-optimized movie suggestions |
| 21 | GET | `/api/insights` | List all 10 query descriptions |
| 22 | GET | `/api/insights/{query_id}` | Execute a specific insight query |
| 23 | POST | `/api/admin/movies` | Insert a new movie |
| 24 | POST | `/api/admin/availability` | Add streaming availability |

### 10.5 Transaction Types Demonstrated

The application demonstrates all four SQL DML operations:

| Operation | Endpoint(s) | Example |
|-----------|-------------|---------|
| **SELECT** | All GET endpoints | `/api/movies/search?genre=Sci-Fi&min_rating=7.0` |
| **INSERT** | POST `/api/ratings`, `/api/reviews`, `/api/watchlist`, `/api/admin/movies`, `/api/admin/availability` | Submit a new rating: `{user_id: 1, movie_id: 42, rating: 8.5}` |
| **UPDATE** | PUT `/api/watchlist/{id}/{movie_id}` | Mark movie as watched: `{status: "watched"}` |
| **DELETE** | DELETE `/api/watchlist/{id}/{movie_id}` | Remove a movie from watchlist |

---

## 11. Live Demo Guide

### 11.1 Running the Application

The CineVerse application runs locally on three ports:

| Component | URL | Purpose |
|-----------|-----|---------|
| **Frontend** | `http://localhost:5173` | React SPA (user-facing interface) |
| **Backend API** | `http://localhost:8000/docs` | FastAPI auto-generated Swagger UI for testing endpoints |
| **Database** | `localhost:5432` (database: `cineverse`) | PostgreSQL server |

### 11.2 Demo Flow: 10-Step User Journey

The following walkthrough demonstrates the full breadth of the application, touching every screen and exercising the key database concepts:

| Step | Action | Screen | Database Concepts |
|------|--------|--------|-------------------|
| 1 | User selects their profile from the login screen | Login | SELECT from UserProfile |
| 2 | Dashboard loads with stats (500 movies, 200 users, 9,874 ratings), top-rated row, trending row | Dashboard | COUNT, AVG aggregates across Movie, UserRating |
| 3 | User searches for "Sci-Fi" movies rated 7.0+ on Netflix | Search | Multi-table JOIN with WHERE filters (Q08 pattern) |
| 4 | User clicks a movie to view full details: cast, genres, ratings, platforms, awards, mood tags | Movie Detail | 8+ table JOIN across the full relational model |
| 5 | User adds the movie to their watchlist | Watchlist | INSERT into WatchlistItem |
| 6 | User visits the Recommendation Lab, selects "mind-bending" and "dark" mood tags | Recommendations | Subquery-based tag matching (Q04 pattern) |
| 7 | User views a watch party and gets group suggestions | Group Watch | NOT EXISTS anti-join (Q10 pattern) |
| 8 | User runs "Top Rated by Genre" from the Insights panel | Insights | Window function RANK, PARTITION BY, HAVING (Q01) |
| 9 | User marks a watchlist movie as "watched" | Watchlist | UPDATE WatchlistItem.watched_status |
| 10 | Admin adds a new movie and its streaming availability | Admin | INSERT into Movie, INSERT into MovieAvailability |

---

## 12. Deliverables Summary

| Course Requirement | CineVerse Deliverable | Location |
|--------------------|-----------------------|----------|
| Relational schema with constraints | 27 tables with 40+ FKs, 18 CHECKs, 11 UNIQUEs, composite PKs | `sql/01_create_tables.sql` |
| SQL to create tables | Full DDL with DROP IF EXISTS and CREATE TABLE | `sql/01_create_tables.sql` |
| SQL to populate tables | COPY from CSVs + portable INSERT alternative | `sql/02_load_data.sql`, `sql/02_insert_data.sql` |
| 10 complex queries | JOINs, window functions, subqueries, NOT EXISTS, CASE, STRING_AGG, PERCENTILE_CONT | `sql/queries/q01_*.sql` through `sql/queries/q10_*.sql` |
| 30+ records per table | 31,426 total rows across 27 tables | `data_clean/` (CSVs) |
| ER diagram | Entity-Relationship diagram with all entities and relationships | `docs/database_design/er_diagram.png` |
| Relational mapping | Conceptual-to-relational transformation diagram | `docs/database_design/relational_mapping.png` |
| Constraints summary | Visual summary of all constraint types | `docs/database_design/constraints_summary.png` |
| Design document | Full design rationale, entity listing, cardinalities | `docs/database_design/DATABASE_DESIGN.md` |
| Performance indexes | 30 indexes on frequently joined/filtered columns | `sql/04_indexes.sql` |
| Application UI | React SPA with 9 screens | `frontend/src/pages/` |
| REST API | FastAPI backend with 24 endpoints | `backend/main.py`, `backend/db.py` |
| ETL pipeline | Automated download, cleaning, validation, loading | `etl/` |
| Final report | Comprehensive project documentation | `docs/FINAL_REPORT.md` |
| Submission document | This document (accompanies 21-slide PPT) | `docs/SUBMISSION_DOCUMENT.md` |
| PowerPoint presentation | 21-slide presentation | `docs/CineVerse_Movie_Database.pptx` |

### 12.1 Final Statistics

| Metric | Value |
|--------|-------|
| Total Tables | 27 |
| Total Rows | 31,426 |
| Complex SQL Queries | 10 |
| Application Screens | 9 |
| REST API Endpoints | 24 |
| Primary Keys (surrogate) | 15 |
| Primary Keys (composite) | 11 |
| Foreign Keys | 40+ |
| CHECK Constraints | 18 |
| UNIQUE Constraints | 11 |
| Performance Indexes | 30 |
| Data Sources | 3 (IMDb, MovieLens, TMDb) |

---

## 13. References

1. **IMDb Non-Commercial Datasets.**
   IMDb Developer. https://developer.imdb.com/non-commercial-datasets/
   *Used for: movie metadata, person data, cast/crew credits, IMDb ratings. Four TSV files totaling approximately 3.5 GB.*

2. **MovieLens Latest Small Dataset.**
   F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets: History and Context. ACM Transactions on Interactive Intelligent Systems (TiiS) 5, 4, Article 19.
   GroupLens Research, University of Minnesota. https://grouplens.org/datasets/movielens/latest/
   *Used for: user ratings (scaled 0--10), user-generated mood/theme tags, cross-reference links to IMDb and TMDb.*

3. **TMDb API Documentation.**
   The Movie Database. https://developer.themoviedb.org/docs
   *Used for: poster images, plot summaries, budget/revenue data, production countries, original language mapping.*

4. **PostgreSQL 16 Documentation.**
   The PostgreSQL Global Development Group. https://www.postgresql.org/docs/16/
   *Reference for: DDL syntax (CREATE TABLE, constraints), window functions (RANK, DENSE_RANK), aggregate functions (STRING_AGG, PERCENTILE_CONT), CHECK constraints, ON DELETE CASCADE/SET NULL.*

5. **React Documentation.**
   Meta Open Source. https://react.dev/
   *Used for: frontend component architecture, state management with hooks, client-side routing.*

6. **FastAPI Documentation.**
   Sebastian Ramirez. https://fastapi.tiangolo.com/
   *Used for: REST API design patterns, Pydantic request/response models, CORS middleware, path and query parameter handling.*

7. **Tailwind CSS Documentation.**
   Tailwind Labs. https://tailwindcss.com/docs
   *Used for: responsive UI styling with utility-first CSS classes.*

8. **Vite Documentation.**
   Evan You and Vite Contributors. https://vitejs.dev/
   *Used for: frontend build tooling, development server with hot module replacement.*

9. **Elmasri, R. and Navathe, S.B. (2016).** *Fundamentals of Database Systems.* 7th Edition, Pearson.
   *Reference for: ER modeling methodology, relational mapping rules, normalization theory (1NF through 3NF), constraint classification.*

---

*This submission document was prepared as part of the final deliverable for ISE 503: Data Management, Spring 2026. It accompanies the 21-slide PowerPoint presentation and provides the detailed written exposition of all project components.*

*Team: Aditya Kamat, Suhas Gangireddy, Manasa Kumari*

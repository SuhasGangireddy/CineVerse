# CineVerse — Movie Database System

An IMDb/Netflix-inspired relational movie database system built for ISE 503: Data Management (Spring 2026).

CineVerse supports movie metadata, cast/crew relationships, genres, user ratings, reviews, watchlists, streaming availability, and personalized recommendations with explainable mood-based discovery, group-watch planning, and industry analytics.

## Tech Stack

- **Database:** PostgreSQL
- **Backend:** Python FastAPI
- **Frontend:** React + Vite + TailwindCSS
- **ETL:** Python (IMDb + MovieLens + TMDb datasets)

## Quick Start

### Prerequisites

- PostgreSQL 14+
- Python 3.10+
- Node.js 18+

### 1. Set Up the Database

```bash
# Create database
createdb -U postgres cineverse

# Create tables
psql -U postgres -d cineverse -f sql/01_create_tables.sql

# Load data (run from project root)
psql -U postgres -d cineverse -f sql/02_load_data.sql

# Create indexes
psql -U postgres -d cineverse -f sql/04_indexes.sql
```

### 2. Start the Backend

```bash
python -m venv venv
source venv/Scripts/activate    # Windows
# source venv/bin/activate      # Mac/Linux

pip install -r backend/requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

### 4. (Optional) Run ETL from Scratch

If you want to re-download and process the datasets:

```bash
pip install pandas requests tqdm
python etl/01_download_data.py
python etl/02_process_data.py
python etl/03_enrich_tmdb.py --api-key YOUR_TMDB_KEY  # optional
python etl/validate_and_fix_all.py
python etl/04_load_to_postgres.py
```

## Project Structure

```
cineverse/
├── sql/                          # SQL deliverables
│   ├── 01_create_tables.sql      # Schema DDL (27 tables)
│   ├── 02_load_data.sql          # COPY from CSVs
│   ├── 02_insert_data.sql        # INSERT alternative
│   ├── 03_complex_queries.sql    # 10 complex join queries
│   └── 04_indexes.sql            # Performance indexes
├── backend/                      # FastAPI REST API
│   ├── main.py
│   ├── db.py
│   └── requirements.txt
├── frontend/                     # React UI
│   ├── src/
│   │   ├── pages/                # 9 pages
│   │   └── components/           # Shared components
│   ├── package.json
│   └── vite.config.js
├── etl/                          # Data pipeline
│   ├── 01_download_data.py
│   ├── 02_process_data.py
│   ├── 03_enrich_tmdb.py
│   ├── 04_load_to_postgres.py
│   └── validate_and_fix_all.py
├── data_clean/                   # Processed CSVs (committed)
├── schema/
│   └── er_diagram.txt
└── docs/
```

## Database

- **27 tables** covering movies, people, credits, genres, ratings, reviews, tags, streaming platforms, awards, production companies, watchlists, and group watch parties
- **31,000+ rows** from real IMDb and MovieLens datasets
- **10 complex SQL queries** with joins, window functions, subqueries, and aggregations

## App Screens

1. **Login** — Profile selection (Netflix-style)
2. **Dashboard** — Stats + Top Rated / Trending / Recent rows
3. **Search** — Filter by title, genre, year, rating, platform
4. **Movie Detail** — Cast, ratings, platforms, awards, mood tags, reviews
5. **Watchlist** — Track unwatched/watching/watched movies
6. **Recommendation Lab** — Mood-based explainable recommendations
7. **Group Watch** — Group movie suggestions
8. **Insights** — Run all 10 complex queries from the UI
9. **Admin** — Add movies, ratings, streaming availability

## Data Sources

- [IMDb Non-Commercial Datasets](https://developer.imdb.com/non-commercial-datasets/)
- [MovieLens Latest Small](https://grouplens.org/datasets/movielens/latest/)
- [TMDb API](https://developer.themoviedb.org/) (optional enrichment)

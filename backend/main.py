from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import db

app = FastAPI(title="CineVerse API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RatingInput(BaseModel):
    user_id: int
    movie_id: int
    rating: float

class ReviewInput(BaseModel):
    user_id: int
    movie_id: int
    text: str
    sentiment: str = "positive"

class WatchlistInput(BaseModel):
    user_id: int
    movie_id: int

class WatchlistStatusInput(BaseModel):
    status: str

class MovieInput(BaseModel):
    imdb_id: str
    title: str
    release_year: int = 2024
    runtime_minutes: int = 120
    language: str = "English"
    plot: str = ""

class AvailabilityInput(BaseModel):
    movie_id: int
    platform_id: int
    region: str = "US"
    access_type: str = "subscription"


# users

@app.get("/api/users")
def list_users():
    return db.get_users()


# dashboard

@app.get("/api/stats")
def dashboard_stats():
    return db.get_dashboard_stats()

@app.get("/api/movies/top")
def top_movies(limit: int = 15):
    return db.get_top_movies(limit)

@app.get("/api/movies/trending")
def trending_movies(limit: int = 15):
    return db.get_trending_movies(limit)

@app.get("/api/movies/recent")
def recent_movies(limit: int = 15):
    return db.get_recently_released(limit)


# search

@app.get("/api/movies/search")
def search_movies(
    title: Optional[str] = None,
    genre: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    min_rating: Optional[float] = None,
    platform: Optional[str] = None,
    director: Optional[str] = None,
    actor: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 50,
):
    return db.search_movies(
        title=title, genre=genre, year_from=year_from, year_to=year_to,
        min_rating=min_rating, platform=platform, director=director,
        actor=actor, tag=tag, limit=limit,
    )


# movie detail

@app.get("/api/movies/{movie_id}")
def movie_details(movie_id: int):
    movie = db.get_movie_details(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.get("/api/movies/{movie_id}/similar")
def similar_movies(movie_id: int, limit: int = 8):
    return db.get_similar_movies(movie_id, limit)


# genres, platforms, tags

@app.get("/api/genres")
def list_genres():
    return db.get_genres()

@app.get("/api/platforms")
def list_platforms():
    return db.get_platforms()

@app.get("/api/tags")
def list_tags():
    return db.get_tags()


# recommendations

@app.get("/api/recommendations/{user_id}")
def recommendations(
    user_id: int,
    tags: Optional[str] = None,
    platform: Optional[str] = None,
    min_rating: Optional[float] = None,
    limit: int = 15,
):
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    return db.get_recommendations(user_id, tags=tag_list, platform=platform,
                                   min_rating=min_rating, limit=limit)


# watchlist

@app.get("/api/watchlist/{user_id}")
def user_watchlist(user_id: int):
    return db.get_user_watchlist(user_id)

@app.post("/api/watchlist")
def add_watchlist(data: WatchlistInput):
    db.add_to_watchlist(data.user_id, data.movie_id)
    return {"status": "added"}

@app.put("/api/watchlist/{watchlist_id}/{movie_id}")
def update_watchlist(watchlist_id: int, movie_id: int, data: WatchlistStatusInput):
    db.update_watchlist_status(watchlist_id, movie_id, data.status)
    return {"status": "updated"}

@app.delete("/api/watchlist/{watchlist_id}/{movie_id}")
def remove_watchlist(watchlist_id: int, movie_id: int):
    db.remove_from_watchlist(watchlist_id, movie_id)
    return {"status": "removed"}


# ratings & reviews

@app.post("/api/ratings")
def rate_movie(data: RatingInput):
    db.submit_rating(data.user_id, data.movie_id, data.rating)
    return {"status": "rated"}

@app.post("/api/reviews")
def review_movie(data: ReviewInput):
    db.submit_review(data.user_id, data.movie_id, data.text, data.sentiment)
    return {"status": "reviewed"}


# group watch

@app.get("/api/group-watch/parties")
def watch_parties():
    return db.get_group_watch_parties()

@app.get("/api/group-watch/{party_id}")
def group_recommendation(party_id: int, limit: int = 10):
    return db.get_group_recommendation(party_id, limit)


# insights

@app.get("/api/insights")
def list_insights():
    return [
        {"id": k, "title": v["title"], "description": v["description"]}
        for k, v in db.INSIGHT_QUERIES.items()
    ]

@app.get("/api/insights/{query_id}")
def run_insight(query_id: int):
    result = db.get_insight(query_id)
    if not result:
        raise HTTPException(status_code=404, detail="Query not found")
    return result


# admin

@app.post("/api/admin/movies")
def add_movie(data: MovieInput):
    db.execute("""
        INSERT INTO Movie (imdb_id, title, release_year, runtime_minutes, language, plot)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, [data.imdb_id, data.title, data.release_year, data.runtime_minutes,
          data.language, data.plot])
    return {"status": "created"}

@app.post("/api/admin/availability")
def add_availability(data: AvailabilityInput):
    db.execute("""
        INSERT INTO MovieAvailability (movie_id, platform_id, region, access_type, start_date)
        VALUES (%s, %s, %s, %s, CURRENT_DATE)
        ON CONFLICT DO NOTHING
    """, [data.movie_id, data.platform_id, data.region, data.access_type])
    return {"status": "created"}

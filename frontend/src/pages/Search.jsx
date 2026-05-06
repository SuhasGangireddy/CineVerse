import { useState, useEffect, useCallback } from "react";
import MovieCard from "../components/MovieCard";

export default function Search() {
  // Search / filter state
  const [query, setQuery] = useState("");
  const [genre, setGenre] = useState("");
  const [yearFrom, setYearFrom] = useState("");
  const [yearTo, setYearTo] = useState("");
  const [minRating, setMinRating] = useState(0);
  const [platform, setPlatform] = useState("");

  // Options for dropdowns
  const [genres, setGenres] = useState([]);
  const [platforms, setPlatforms] = useState([]);

  // Results
  const [results, setResults] = useState([]);
  const [resultCount, setResultCount] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  // Fetch filter options on mount
  useEffect(() => {
    fetch("/api/genres")
      .then((r) => (r.ok ? r.json() : []))
      .then(setGenres)
      .catch(() => {});

    fetch("/api/platforms")
      .then((r) => (r.ok ? r.json() : []))
      .then(setPlatforms)
      .catch(() => {});
  }, []);

  const doSearch = useCallback(async () => {
    setLoading(true);
    setSearched(true);

    const params = new URLSearchParams();
    if (query.trim()) params.set("title", query.trim());
    if (genre) params.set("genre", genre);
    if (yearFrom) params.set("year_from", yearFrom);
    if (yearTo) params.set("year_to", yearTo);
    if (minRating > 0) params.set("min_rating", minRating);
    if (platform) params.set("platform", platform);

    try {
      const res = await fetch(`/api/movies/search?${params.toString()}`);
      if (!res.ok) throw new Error("Search failed");
      const data = await res.json();
      const movies = Array.isArray(data) ? data : data.results ?? [];
      setResults(movies);
      setResultCount(
        typeof data.count === "number" ? data.count : movies.length
      );
    } catch (err) {
      console.error(err);
      setResults([]);
      setResultCount(0);
    } finally {
      setLoading(false);
    }
  }, [query, genre, yearFrom, yearTo, minRating, platform]);

  const handleSubmit = (e) => {
    e.preventDefault();
    doSearch();
  };

  const handleReset = () => {
    setQuery("");
    setGenre("");
    setYearFrom("");
    setYearTo("");
    setMinRating(0);
    setPlatform("");
    setResults([]);
    setResultCount(null);
    setSearched(false);
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* Search Bar */}
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex gap-3">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search movies by title, cast, plot..."
            className="flex-1 rounded-lg border border-gray-600 bg-[#1f1f1f] px-5 py-3 text-white placeholder-gray-500 outline-none transition focus:border-[#e50914] focus:ring-1 focus:ring-[#e50914]"
          />
          <button
            type="submit"
            className="rounded-lg bg-[#e50914] px-6 py-3 font-semibold text-white transition hover:bg-[#f6121d]"
          >
            Search
          </button>
        </div>
      </form>

      {/* Filters Row */}
      <div className="mb-8 flex flex-wrap items-end gap-4 rounded-xl bg-[#1f1f1f] p-5">
        {/* Genre */}
        <div className="min-w-[160px] flex-1">
          <label className="mb-1 block text-xs font-medium text-gray-400">
            Genre
          </label>
          <select
            value={genre}
            onChange={(e) => setGenre(e.target.value)}
            className="w-full cursor-pointer rounded-lg border border-gray-600 bg-[#2b2b2b] px-3 py-2 text-sm text-white outline-none focus:border-[#e50914]"
          >
            <option value="">All Genres</option>
            {genres.map((g) => (
              <option key={g.genre_id} value={g.genre_name}>
                {g.genre_name}
              </option>
            ))}
          </select>
        </div>

        {/* Year Range */}
        <div className="flex items-end gap-2">
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-400">
              Year From
            </label>
            <input
              type="number"
              min="1900"
              max="2099"
              value={yearFrom}
              onChange={(e) => setYearFrom(e.target.value)}
              placeholder="1900"
              className="w-24 rounded-lg border border-gray-600 bg-[#2b2b2b] px-3 py-2 text-sm text-white outline-none focus:border-[#e50914]"
            />
          </div>
          <span className="pb-2 text-gray-500">-</span>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-400">
              Year To
            </label>
            <input
              type="number"
              min="1900"
              max="2099"
              value={yearTo}
              onChange={(e) => setYearTo(e.target.value)}
              placeholder="2026"
              className="w-24 rounded-lg border border-gray-600 bg-[#2b2b2b] px-3 py-2 text-sm text-white outline-none focus:border-[#e50914]"
            />
          </div>
        </div>

        {/* Min Rating */}
        <div className="min-w-[160px]">
          <label className="mb-1 block text-xs font-medium text-gray-400">
            Min Rating: {minRating > 0 ? minRating.toFixed(1) : "Any"}
          </label>
          <input
            type="range"
            min="0"
            max="10"
            step="0.5"
            value={minRating}
            onChange={(e) => setMinRating(parseFloat(e.target.value))}
            className="w-full accent-[#e50914]"
          />
        </div>

        {/* Platform */}
        <div className="min-w-[160px] flex-1">
          <label className="mb-1 block text-xs font-medium text-gray-400">
            Platform
          </label>
          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
            className="w-full cursor-pointer rounded-lg border border-gray-600 bg-[#2b2b2b] px-3 py-2 text-sm text-white outline-none focus:border-[#e50914]"
          >
            <option value="">All Platforms</option>
            {platforms.map((p) => (
              <option
                key={p.platform_id ?? p.name ?? p}
                value={p.name ?? p}
              >
                {p.name ?? p}
              </option>
            ))}
          </select>
        </div>

        {/* Reset */}
        <button
          onClick={handleReset}
          type="button"
          className="rounded-lg border border-gray-600 px-4 py-2 text-sm text-gray-300 transition hover:border-gray-400 hover:text-white"
        >
          Reset
        </button>
      </div>

      {/* Result count */}
      {searched && resultCount !== null && (
        <p className="mb-4 text-sm text-gray-400">
          {resultCount} {resultCount === 1 ? "result" : "results"} found
        </p>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex justify-center py-16">
          <div className="h-10 w-10 animate-spin rounded-full border-2 border-gray-600 border-t-[#e50914]" />
        </div>
      )}

      {/* Results Grid */}
      {!loading && results.length > 0 && (
        <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
          {results.map((movie) => (
            <MovieCard key={movie.movie_id} movie={movie} />
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && searched && results.length === 0 && (
        <div className="py-20 text-center">
          <p className="text-lg text-gray-500">
            No movies found. Try adjusting your search or filters.
          </p>
        </div>
      )}
    </div>
  );
}

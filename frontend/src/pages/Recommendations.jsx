import { useState, useEffect } from "react";
import TagChip from "../components/TagChip";
import MovieCard from "../components/MovieCard";

function getUser() {
  try {
    const raw = localStorage.getItem("cineverse_user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export default function Recommendations() {
  const user = getUser();

  const [tags, setTags] = useState([]);
  const [selectedTags, setSelectedTags] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [selectedPlatform, setSelectedPlatform] = useState("");
  const [minRating, setMinRating] = useState(0);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [generated, setGenerated] = useState(false);

  useEffect(() => {
    fetch("/api/tags")
      .then((res) => res.json())
      .then((data) => setTags(Array.isArray(data) ? data : []))
      .catch(() => {});

    fetch("/api/platforms")
      .then((res) => res.json())
      .then((data) => setPlatforms(Array.isArray(data) ? data : []))
      .catch(() => {});
  }, []);

  const toggleTag = (tagName) => {
    setSelectedTags((prev) =>
      prev.includes(tagName)
        ? prev.filter((t) => t !== tagName)
        : [...prev, tagName]
    );
  };

  const handleGenerate = async () => {
    if (!user) {
      setError("Please log in to get recommendations.");
      return;
    }
    setLoading(true);
    setError(null);
    setResults([]);
    setGenerated(false);

    try {
      const params = new URLSearchParams();
      if (selectedTags.length > 0) params.set("tags", selectedTags.join(","));
      if (selectedPlatform) params.set("platform", selectedPlatform);
      if (minRating > 0) params.set("min_rating", minRating);

      const res = await fetch(
        `/api/recommendations/${user.user_id}?${params.toString()}`
      );
      if (!res.ok)
        throw new Error(`Failed to fetch recommendations (${res.status})`);
      const data = await res.json();
      setResults(Array.isArray(data) ? data : []);
      setGenerated(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen px-6 py-10 max-w-6xl mx-auto" style={{ background: "#141414" }}>
      <h1 className="text-4xl font-bold text-white mb-1">Recommendation Lab</h1>
      <p className="text-gray-400 text-lg mb-8">What are you in the mood for?</p>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-white mb-3">Select Mood Tags</h2>
        <div className="flex flex-wrap gap-2">
          {tags.length === 0 && (
            <p className="text-gray-500 text-sm">Loading tags...</p>
          )}
          {tags.map((tag) => {
            const tagName = typeof tag === "string" ? tag : tag.tag_name || tag.name;
            const isSelected = selectedTags.includes(tagName);
            return (
              <TagChip
                key={tagName}
                name={tagName}
                selected={isSelected}
                onClick={() => toggleTag(tagName)}
              />
            );
          })}
        </div>
      </section>

      <section className="mb-8 flex flex-wrap gap-6 items-end">
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-gray-300">
            Min Rating: <span className="text-white font-bold">{minRating}</span>
          </label>
          <input
            type="range"
            min={0}
            max={10}
            step={0.5}
            value={minRating}
            onChange={(e) => setMinRating(parseFloat(e.target.value))}
            className="w-48 accent-[#e50914]"
          />
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-gray-300">Platform</label>
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            className="px-3 py-2 rounded text-sm text-white border border-gray-700 focus:outline-none focus:border-[#e50914] cursor-pointer"
            style={{ background: "#1f1f1f" }}
          >
            <option value="">All Platforms</option>
            {platforms.map((p) => {
              const name = typeof p === "string" ? p : p.platform_name || p.name;
              const id = typeof p === "string" ? p : p.platform_id || p.name;
              return (
                <option key={id} value={name}>
                  {name}
                </option>
              );
            })}
          </select>
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="px-6 py-2.5 rounded-lg text-white font-semibold text-sm transition-colors cursor-pointer disabled:opacity-50"
          style={{ background: "#e50914" }}
          onMouseEnter={(e) => { if (!loading) e.currentTarget.style.background = "#b8070f"; }}
          onMouseLeave={(e) => { e.currentTarget.style.background = "#e50914"; }}
        >
          {loading ? "Generating..." : "Generate Recommendations"}
        </button>
      </section>

      {error && (
        <div className="mb-6 px-4 py-3 rounded-lg text-sm font-medium" style={{ background: "#2a2a2a", color: "#e50914" }}>
          {error}
        </div>
      )}

      {generated && results.length === 0 && !loading && (
        <p className="text-gray-500">No recommendations found. Try adjusting your filters.</p>
      )}

      {results.length > 0 && (
        <section>
          <h2 className="text-2xl font-semibold text-white mb-5">
            Your Recommendations ({results.length})
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {results.map((movie) => (
              <div key={movie.movie_id || movie.title} className="flex flex-col">
                <MovieCard movie={movie} />
                <div
                  className="mt-2 p-3 rounded-b-lg text-sm"
                  style={{ background: "#2a2a2a", borderLeft: "3px solid #e50914" }}
                >
                  <p className="text-gray-300 font-medium mb-1">Why this movie?</p>
                  <p className="text-gray-400">
                    Matches tags:{" "}
                    <span className="text-white">
                      {movie.matching_tags
                        ? Array.isArray(movie.matching_tags)
                          ? movie.matching_tags.join(", ")
                          : movie.matching_tags
                        : selectedTags.join(", ")}
                    </span>
                  </p>
                  {movie.tag_match_count != null && (
                    <p className="text-gray-500 text-xs mt-1">
                      Tag match count: {movie.tag_match_count}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

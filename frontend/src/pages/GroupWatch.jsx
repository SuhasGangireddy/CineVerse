import { useState, useEffect } from "react";

function getUser() {
  try {
    const raw = localStorage.getItem("cineverse_user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export default function GroupWatch() {
  const user = getUser();

  const [parties, setParties] = useState([]);
  const [selectedParty, setSelectedParty] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingParties, setLoadingParties] = useState(true);
  const [error, setError] = useState(null);
  const [searched, setSearched] = useState(false);

  useEffect(() => {
    fetch("/api/group-watch/parties")
      .then((res) => res.json())
      .then((data) => {
        setParties(Array.isArray(data) ? data : []);
        setLoadingParties(false);
      })
      .catch(() => setLoadingParties(false));
  }, []);

  const handleFindMovie = async () => {
    if (!selectedParty) {
      setError("Please select a party first.");
      return;
    }
    setLoading(true);
    setError(null);
    setResults([]);
    setSearched(false);

    try {
      const res = await fetch(`/api/group-watch/${selectedParty}`);
      if (!res.ok) throw new Error(`Failed to fetch group recommendations (${res.status})`);
      const data = await res.json();
      setResults(Array.isArray(data) ? data : []);
      setSearched(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "#141414" }}>
        <div className="text-center p-10 rounded-xl" style={{ background: "#1f1f1f" }}>
          <h2 className="text-2xl font-bold text-white mb-3">Not Logged In</h2>
          <p className="text-gray-400">Please log in to use Group Watch Planner.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen px-6 py-10 max-w-6xl mx-auto" style={{ background: "#141414" }}>
      <h1 className="text-4xl font-bold text-white mb-2">Group Watch Planner</h1>
      <p className="text-gray-400 text-lg mb-8">
        Find the perfect movie everyone in your group will enjoy.
      </p>

      <section className="mb-8 flex flex-wrap gap-4 items-end">
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-gray-300">Select Party</label>
          <select
            value={selectedParty}
            onChange={(e) => setSelectedParty(e.target.value)}
            className="px-4 py-2.5 rounded text-sm text-white border border-gray-700 focus:outline-none focus:border-[#e50914] cursor-pointer min-w-[240px]"
            style={{ background: "#1f1f1f" }}
            disabled={loadingParties}
          >
            <option value="">
              {loadingParties ? "Loading parties..." : "-- Choose a party --"}
            </option>
            {parties.map((party) => {
              const id = party.party_id || party.id;
              const name = party.party_name || party.name || `Party ${id}`;
              return (
                <option key={id} value={id}>
                  {name}
                </option>
              );
            })}
          </select>
        </div>

        <button
          onClick={handleFindMovie}
          disabled={loading || !selectedParty}
          className="px-6 py-2.5 rounded-lg text-white font-semibold text-sm transition-colors cursor-pointer disabled:opacity-50"
          style={{ background: "#e50914" }}
          onMouseEnter={(e) => { if (!loading) e.currentTarget.style.background = "#b8070f"; }}
          onMouseLeave={(e) => { e.currentTarget.style.background = "#e50914"; }}
        >
          {loading ? "Finding..." : "Find Best Group Movie"}
        </button>
      </section>

      {error && (
        <div className="mb-6 px-4 py-3 rounded-lg text-sm font-medium" style={{ background: "#2a2a2a", color: "#e50914" }}>
          {error}
        </div>
      )}

      {searched && results.length === 0 && !loading && (
        <p className="text-gray-500">No group recommendations found for this party.</p>
      )}

      {results.length > 0 && (
        <section>
          <h2 className="text-2xl font-semibold text-white mb-5">
            Recommended for Your Group ({results.length})
          </h2>
          <div className="flex flex-col gap-4">
            {results.map((movie) => (
              <div
                key={movie.movie_id || movie.title}
                className="p-5 rounded-lg"
                style={{ background: "#1f1f1f" }}
              >
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-xl font-bold text-white mb-2">{movie.title}</h3>
                    <div className="flex flex-wrap items-center gap-3 text-sm text-gray-400">
                      {movie.year && <span>{movie.year}</span>}
                      {movie.rating != null && (
                        <span className="flex items-center gap-1">
                          <span style={{ color: "#e50914" }}>&#9733;</span> {movie.rating}
                        </span>
                      )}
                      {movie.genres && <span>{movie.genres}</span>}
                    </div>

                    <div className="flex flex-wrap gap-4 mt-3 text-sm">
                      {movie.avg_community_rating != null && (
                        <span className="text-gray-300">
                          Community Rating:{" "}
                          <span className="text-white font-semibold">
                            {Number(movie.avg_community_rating).toFixed(1)}
                          </span>
                        </span>
                      )}
                      {movie.times_rated != null && (
                        <span className="text-gray-300">
                          Times Rated:{" "}
                          <span className="text-white font-semibold">{movie.times_rated}</span>
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div
                  className="mt-4 p-3 rounded text-sm"
                  style={{ background: "#2a2a2a", borderLeft: "3px solid #e50914" }}
                >
                  <p className="text-gray-300">
                    Not yet watched by any group member. High community rating.
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

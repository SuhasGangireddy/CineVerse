import { useState, useEffect, useCallback } from "react";

const STATUS_GROUPS = ["unwatched", "watching", "watched"];
const STATUS_LABELS = {
  unwatched: "Unwatched",
  watching: "Watching",
  watched: "Watched",
};

function getUser() {
  try {
    const raw = localStorage.getItem("cineverse_user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export default function Watchlist() {
  const user = getUser();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionMsg, setActionMsg] = useState(null);

  const fetchWatchlist = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/watchlist/${user.user_id}`);
      if (!res.ok) throw new Error(`Failed to fetch watchlist (${res.status})`);
      const data = await res.json();
      setItems(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [user?.user_id]);

  useEffect(() => {
    fetchWatchlist();
  }, [fetchWatchlist]);

  const handleMarkWatched = async (watchlist_id, movie_id) => {
    try {
      const res = await fetch(`/api/watchlist/${watchlist_id}/${movie_id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "watched" }),
      });
      if (!res.ok) throw new Error("Failed to update status");
      setActionMsg("Marked as watched!");
      fetchWatchlist();
    } catch (err) {
      setActionMsg(err.message);
    } finally {
      setTimeout(() => setActionMsg(null), 3000);
    }
  };

  const handleRemove = async (watchlist_id, movie_id) => {
    try {
      const res = await fetch(`/api/watchlist/${watchlist_id}/${movie_id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to remove from watchlist");
      setActionMsg("Removed from watchlist.");
      fetchWatchlist();
    } catch (err) {
      setActionMsg(err.message);
    } finally {
      setTimeout(() => setActionMsg(null), 3000);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "#141414" }}>
        <div className="text-center p-10 rounded-xl" style={{ background: "#1f1f1f" }}>
          <h2 className="text-2xl font-bold text-white mb-3">Not Logged In</h2>
          <p className="text-gray-400">Please log in to view your watchlist.</p>
        </div>
      </div>
    );
  }

  const grouped = STATUS_GROUPS.reduce((acc, status) => {
    acc[status] = items.filter(
      (item) => (item.watched_status || "unwatched").toLowerCase() === status
    );
    return acc;
  }, {});

  return (
    <div className="min-h-screen px-6 py-10 max-w-6xl mx-auto" style={{ background: "#141414" }}>
      <h1 className="text-4xl font-bold text-white mb-2">My Watchlist</h1>
      <p className="text-gray-400 mb-8">
        Logged in as <span className="text-white font-medium">{user.username}</span>
      </p>

      {actionMsg && (
        <div className="mb-6 px-4 py-3 rounded-lg text-sm font-medium" style={{ background: "#2a2a2a", color: "#e50914" }}>
          {actionMsg}
        </div>
      )}

      {loading && <p className="text-gray-500">Loading watchlist...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {!loading && !error && items.length === 0 && (
        <p className="text-gray-500">Your watchlist is empty.</p>
      )}

      {!loading &&
        !error &&
        STATUS_GROUPS.map((status) => {
          const group = grouped[status];
          if (group.length === 0) return null;
          return (
            <section key={status} className="mb-10">
              <h2
                className="text-2xl font-semibold mb-4 pb-2 border-b"
                style={{ color: status === "watched" ? "#4ade80" : status === "watching" ? "#facc15" : "#e5e5e5", borderColor: "#333" }}
              >
                {STATUS_LABELS[status]} ({group.length})
              </h2>
              <div className="flex flex-col gap-3">
                {group.map((item) => (
                  <div
                    key={`${item.watchlist_id}-${item.movie_id}`}
                    className="flex items-center gap-4 p-4 rounded-lg transition-colors hover:brightness-110"
                    style={{ background: "#1f1f1f" }}
                  >
                    <div
                      className="shrink-0 w-14 h-20 rounded flex items-center justify-center text-xs text-gray-500"
                      style={{ background: "#2a2a2a" }}
                    >
                      <svg className="w-6 h-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15.75 10.5l4.72-4.72a.75.75 0 011.28.53v11.38a.75.75 0 01-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 002.25-2.25v-9A2.25 2.25 0 0013.5 5.25h-9A2.25 2.25 0 002.25 7.5v9A2.25 2.25 0 004.5 18.75z" />
                      </svg>
                    </div>

                    <div className="flex-1 min-w-0">
                      <h3 className="text-white font-semibold text-lg truncate">{item.title}</h3>
                      <div className="flex flex-wrap items-center gap-3 mt-1 text-sm text-gray-400">
                        {item.year && <span>{item.year}</span>}
                        {item.rating != null && (
                          <span className="flex items-center gap-1">
                            <span style={{ color: "#e50914" }}>&#9733;</span> {item.rating}
                          </span>
                        )}
                        {item.genres && <span className="truncate">{item.genres}</span>}
                      </div>
                    </div>

                    <div className="flex gap-2 shrink-0">
                      {status !== "watched" && (
                        <button
                          onClick={() => handleMarkWatched(item.watchlist_id, item.movie_id)}
                          className="px-3 py-1.5 rounded text-sm font-medium transition-colors cursor-pointer"
                          style={{ background: "#e50914", color: "#fff" }}
                          onMouseEnter={(e) => (e.currentTarget.style.background = "#b8070f")}
                          onMouseLeave={(e) => (e.currentTarget.style.background = "#e50914")}
                        >
                          Mark as Watched
                        </button>
                      )}
                      <button
                        onClick={() => handleRemove(item.watchlist_id, item.movie_id)}
                        className="px-3 py-1.5 rounded text-sm font-medium transition-colors cursor-pointer"
                        style={{ background: "#333", color: "#e5e5e5" }}
                        onMouseEnter={(e) => (e.currentTarget.style.background = "#444")}
                        onMouseLeave={(e) => (e.currentTarget.style.background = "#333")}
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          );
        })}
    </div>
  );
}

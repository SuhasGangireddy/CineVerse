import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import MovieCard from "../components/MovieCard";
import PlatformBadge from "../components/PlatformBadge";
import TagChip from "../components/TagChip";

const STORAGE_KEY = "cineverse_user";

function getUser() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

/* ---------- Small helper components ---------- */

function GenreChip({ name }) {
  return (
    <span className="rounded-full border border-gray-600 px-3 py-1 text-xs text-gray-300">
      {name}
    </span>
  );
}

function ImdbBadge({ rating }) {
  if (rating == null) return null;
  return (
    <span className="inline-flex items-center gap-1 rounded bg-yellow-500/20 px-2 py-1 text-sm font-semibold text-yellow-400">
      <svg
        className="h-4 w-4"
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.957a1 1 0 00.95.69h4.162c.969 0 1.371 1.24.588 1.81l-3.37 2.448a1 1 0 00-.364 1.118l1.287 3.957c.3.921-.755 1.688-1.54 1.118l-3.37-2.448a1 1 0 00-1.176 0l-3.37 2.448c-.784.57-1.838-.197-1.539-1.118l1.287-3.957a1 1 0 00-.364-1.118L2.063 9.384c-.783-.57-.38-1.81.588-1.81h4.162a1 1 0 00.95-.69l1.286-3.957z" />
      </svg>
      {Number(rating).toFixed(1)}
    </span>
  );
}

function SectionTitle({ children }) {
  return (
    <h2 className="mb-4 text-xl font-semibold text-white">{children}</h2>
  );
}

/* ---------- Main Component ---------- */

export default function MovieDetail() {
  const { id } = useParams();

  const [movie, setMovie] = useState(null);
  const [similar, setSimilar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Rating form
  const [showRatingForm, setShowRatingForm] = useState(false);
  const [ratingScore, setRatingScore] = useState(5);
  const [reviewText, setReviewText] = useState("");
  const [ratingSubmitting, setRatingSubmitting] = useState(false);
  const [ratingMsg, setRatingMsg] = useState(null);

  // Watchlist
  const [watchlistMsg, setWatchlistMsg] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    Promise.all([
      fetch(`/api/movies/${id}`).then((r) => {
        if (!r.ok) throw new Error("Movie not found");
        return r.json();
      }),
      fetch(`/api/movies/${id}/similar`)
        .then((r) => (r.ok ? r.json() : []))
        .catch(() => []),
    ])
      .then(([movieData, similarData]) => {
        setMovie(movieData);
        setSimilar(Array.isArray(similarData) ? similarData : []);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  /* ---- Actions ---- */

  const handleAddWatchlist = async () => {
    const user = getUser();
    if (!user?.user_id) {
      setWatchlistMsg("Please log in to add to watchlist.");
      return;
    }
    try {
      const res = await fetch("/api/watchlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: user.user_id,
          movie_id: Number(id),
        }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail ?? "Failed to add");
      }
      setWatchlistMsg("Added to watchlist!");
    } catch (err) {
      setWatchlistMsg(err.message);
    }
  };

  const handleSubmitRating = async (e) => {
    e.preventDefault();
    const user = getUser();
    if (!user?.user_id) {
      setRatingMsg("Please log in to rate.");
      return;
    }
    setRatingSubmitting(true);
    try {
      const res = await fetch("/api/ratings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: user.user_id,
          movie_id: Number(id),
          rating: ratingScore,
          review_text: reviewText || undefined,
        }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail ?? "Failed to submit rating");
      }
      setRatingMsg("Rating submitted!");
      setShowRatingForm(false);
      // Refresh movie data to show new review
      const updated = await fetch(`/api/movies/${id}`);
      if (updated.ok) setMovie(await updated.json());
    } catch (err) {
      setRatingMsg(err.message);
    } finally {
      setRatingSubmitting(false);
    }
  };

  /* ---- Render states ---- */

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-gray-600 border-t-[#e50914]" />
      </div>
    );
  }

  if (error || !movie) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-gray-400">
        <p className="text-lg">{error ?? "Movie not found"}</p>
        <Link
          to="/home"
          className="text-sm text-[#e50914] underline hover:text-[#f6121d]"
        >
          Back to Home
        </Link>
      </div>
    );
  }

  /* Group cast/crew by role */
  const crewByRole = {};
  (movie.cast_crew ?? movie.castCrew ?? []).forEach((person) => {
    const role = person.role ?? "Other";
    if (!crewByRole[role]) crewByRole[role] = [];
    crewByRole[role].push(person);
  });
  const roleOrder = ["Director", "Actor", "Producer", "Writer"];
  const sortedRoles = [
    ...roleOrder.filter((r) => crewByRole[r]),
    ...Object.keys(crewByRole).filter((r) => !roleOrder.includes(r)),
  ];

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      {/* ========== HERO ========== */}
      <section className="mb-10 flex flex-col gap-8 md:flex-row">
        {/* Poster placeholder */}
        <div className="flex h-80 w-56 flex-shrink-0 items-center justify-center self-start rounded-xl bg-[#2b2b2b] shadow-lg">
          {movie.poster_url ? (
            <img
              src={movie.poster_url}
              alt={movie.title}
              className="h-full w-full rounded-xl object-cover"
            />
          ) : (
            <svg
              className="h-16 w-16 text-gray-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"
              />
            </svg>
          )}
        </div>

        {/* Info */}
        <div className="flex-1">
          <h1 className="mb-2 text-4xl font-bold text-white">{movie.title}</h1>

          <div className="mb-4 flex flex-wrap items-center gap-3 text-sm text-gray-400">
            {movie.release_year && <span>{movie.release_year}</span>}
            {movie.runtime && <span>{movie.runtime} min</span>}
            {movie.language && <span>{movie.language}</span>}
            <ImdbBadge rating={movie.imdb_rating} />
          </div>

          {/* Genres */}
          {(movie.genres ?? []).length > 0 && (
            <div className="mb-6 flex flex-wrap gap-2">
              {movie.genres.map((g) => (
                <GenreChip key={g.genre_id ?? g.genre_name} name={g.genre_name ?? g} />
              ))}
            </div>
          )}

          {/* Action buttons */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleAddWatchlist}
              className="rounded-lg bg-[#1f1f1f] px-5 py-2.5 text-sm font-medium text-white transition hover:bg-[#2b2b2b]"
            >
              + Add to Watchlist
            </button>
            <button
              onClick={() => {
                setShowRatingForm((prev) => !prev);
                setRatingMsg(null);
              }}
              className="rounded-lg bg-[#e50914] px-5 py-2.5 text-sm font-medium text-white transition hover:bg-[#f6121d]"
            >
              Rate Movie
            </button>
          </div>

          {watchlistMsg && (
            <p className="mt-2 text-sm text-gray-400">{watchlistMsg}</p>
          )}
          {ratingMsg && !showRatingForm && (
            <p className="mt-2 text-sm text-gray-400">{ratingMsg}</p>
          )}

          {/* Inline rating form */}
          {showRatingForm && (
            <form
              onSubmit={handleSubmitRating}
              className="mt-4 max-w-md rounded-xl bg-[#1f1f1f] p-5"
            >
              <label className="mb-1 block text-sm text-gray-300">
                Score: {ratingScore}
              </label>
              <input
                type="range"
                min="1"
                max="10"
                step="0.5"
                value={ratingScore}
                onChange={(e) => setRatingScore(parseFloat(e.target.value))}
                className="mb-4 w-full accent-[#e50914]"
              />
              <label className="mb-1 block text-sm text-gray-300">
                Review (optional)
              </label>
              <textarea
                value={reviewText}
                onChange={(e) => setReviewText(e.target.value)}
                rows={3}
                className="mb-4 w-full rounded-lg border border-gray-600 bg-[#2b2b2b] px-3 py-2 text-sm text-white outline-none focus:border-[#e50914]"
              />
              <div className="flex items-center gap-3">
                <button
                  type="submit"
                  disabled={ratingSubmitting}
                  className="rounded-lg bg-[#e50914] px-5 py-2 text-sm font-semibold text-white transition hover:bg-[#f6121d] disabled:opacity-50"
                >
                  {ratingSubmitting ? "Submitting..." : "Submit"}
                </button>
                <button
                  type="button"
                  onClick={() => setShowRatingForm(false)}
                  className="text-sm text-gray-400 hover:text-white"
                >
                  Cancel
                </button>
              </div>
              {ratingMsg && (
                <p className="mt-2 text-sm text-gray-400">{ratingMsg}</p>
              )}
            </form>
          )}
        </div>
      </section>

      {/* ========== PLOT ========== */}
      {movie.plot && (
        <section className="mb-10">
          <SectionTitle>Plot</SectionTitle>
          <p className="leading-relaxed text-gray-300">{movie.plot}</p>
        </section>
      )}

      {/* ========== CAST & CREW ========== */}
      {sortedRoles.length > 0 && (
        <section className="mb-10">
          <SectionTitle>Cast &amp; Crew</SectionTitle>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {sortedRoles.map((role) => (
              <div key={role}>
                <h3 className="mb-2 text-sm font-semibold uppercase tracking-wider text-[#e50914]">
                  {role}s
                </h3>
                <ul className="space-y-1">
                  {crewByRole[role].map((p, i) => (
                    <li key={i} className="text-sm text-gray-300">
                      {p.name}
                      {p.character && (
                        <span className="ml-1 text-gray-500">
                          as {p.character}
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ========== STREAMING AVAILABILITY ========== */}
      {(movie.streaming ?? movie.platforms ?? []).length > 0 && (
        <section className="mb-10">
          <SectionTitle>Streaming Availability</SectionTitle>
          <div className="overflow-x-auto rounded-xl bg-[#1f1f1f]">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-gray-700 text-xs uppercase tracking-wider text-gray-400">
                  <th className="px-4 py-3">Platform</th>
                  <th className="px-4 py-3">Access Type</th>
                  <th className="px-4 py-3">Region</th>
                </tr>
              </thead>
              <tbody>
                {(movie.streaming ?? movie.platforms).map((s, i) => (
                  <tr
                    key={i}
                    className="border-b border-gray-800 last:border-0"
                  >
                    <td className="px-4 py-3">
                      <PlatformBadge name={s.platform_name ?? s.platform ?? s.name} />
                    </td>
                    <td className="px-4 py-3 capitalize text-gray-300">
                      {s.access_type ?? s.type ?? "--"}
                    </td>
                    <td className="px-4 py-3 text-gray-300">
                      {s.region ?? "--"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* ========== AWARDS ========== */}
      {(movie.awards ?? []).length > 0 && (
        <section className="mb-10">
          <SectionTitle>Awards</SectionTitle>
          <div className="overflow-x-auto rounded-xl bg-[#1f1f1f]">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-gray-700 text-xs uppercase tracking-wider text-gray-400">
                  <th className="px-4 py-3">Award</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Result</th>
                  <th className="px-4 py-3">Year</th>
                </tr>
              </thead>
              <tbody>
                {movie.awards.map((a, i) => (
                  <tr
                    key={i}
                    className="border-b border-gray-800 last:border-0"
                  >
                    <td className="px-4 py-3 text-gray-300">
                      {a.award_name ?? a.name}
                    </td>
                    <td className="px-4 py-3 text-gray-300">
                      {a.category ?? "--"}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`rounded px-2 py-0.5 text-xs font-medium ${
                          (a.result ?? "").toLowerCase() === "won"
                            ? "bg-green-900/50 text-green-400"
                            : "bg-gray-700 text-gray-300"
                        }`}
                      >
                        {a.result ?? "--"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-400">{a.year ?? "--"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* ========== MOOD TAGS ========== */}
      {(movie.mood_tags ?? movie.tags ?? []).length > 0 && (
        <section className="mb-10">
          <SectionTitle>Mood Tags</SectionTitle>
          <div className="flex flex-wrap gap-2">
            {(movie.mood_tags ?? movie.tags).map((tag, i) => (
              <TagChip key={i} tag={tag.tag_name ?? tag.name ?? tag} />
            ))}
          </div>
        </section>
      )}

      {/* ========== REVIEWS ========== */}
      {(movie.reviews ?? []).length > 0 && (
        <section className="mb-10">
          <SectionTitle>Reviews</SectionTitle>
          <div className="grid gap-4 md:grid-cols-2">
            {movie.reviews.map((r, i) => (
              <div
                key={i}
                className="rounded-xl bg-[#1f1f1f] p-5"
              >
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-sm font-medium text-white">
                    {r.username ?? "Anonymous"}
                  </span>
                  <div className="flex items-center gap-2">
                    {r.sentiment && (
                      <span
                        className={`rounded px-2 py-0.5 text-xs font-medium ${
                          r.sentiment === "positive"
                            ? "bg-green-900/50 text-green-400"
                            : r.sentiment === "negative"
                              ? "bg-red-900/50 text-red-400"
                              : "bg-gray-700 text-gray-300"
                        }`}
                      >
                        {r.sentiment}
                      </span>
                    )}
                    {r.date && (
                      <span className="text-xs text-gray-500">
                        {new Date(r.date).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
                {r.review_text && (
                  <p className="text-sm leading-relaxed text-gray-300">
                    {r.review_text}
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ========== SIMILAR MOVIES ========== */}
      {similar.length > 0 && (
        <section className="mb-10">
          <SectionTitle>Similar Movies</SectionTitle>
          <div className="flex gap-4 overflow-x-auto pb-2" style={{ scrollbarWidth: "none" }}>
            {similar.map((m) => (
              <div key={m.movie_id} className="w-48 flex-shrink-0">
                <MovieCard movie={m} />
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

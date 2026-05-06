import { useState, useEffect, useRef } from "react";
import MovieCard from "../components/MovieCard";

function StatCard({ label, value }) {
  return (
    <div className="flex-1 rounded-xl bg-[#1f1f1f] px-6 py-5 text-center shadow-lg">
      <p className="text-3xl font-bold text-white">{value ?? "--"}</p>
      <p className="mt-1 text-sm text-gray-400">{label}</p>
    </div>
  );
}

function ScrollRow({ title, movies }) {
  const scrollRef = useRef(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  const checkScroll = () => {
    const el = scrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 1);
    setCanScrollRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 1);
  };

  useEffect(() => {
    checkScroll();
    const el = scrollRef.current;
    if (el) {
      el.addEventListener("scroll", checkScroll, { passive: true });
      const ro = new ResizeObserver(checkScroll);
      ro.observe(el);
      return () => {
        el.removeEventListener("scroll", checkScroll);
        ro.disconnect();
      };
    }
  }, [movies]);

  const scroll = (direction) => {
    if (!scrollRef.current) return;
    const amount = 320;
    scrollRef.current.scrollBy({
      left: direction === "left" ? -amount : amount,
      behavior: "smooth",
    });
  };

  if (!movies || movies.length === 0) return null;

  return (
    <section className="mb-10">
      <h2 className="mb-4 text-xl font-semibold text-white">{title}</h2>
      <div className="group/row relative">
        {canScrollLeft && (
          <button
            onClick={() => scroll("left")}
            className="absolute -left-1 top-1/2 z-10 -translate-y-1/2 rounded-full bg-black/70 p-2 text-white opacity-0 transition hover:bg-[#e50914] group-hover/row:opacity-100"
            aria-label="Scroll left"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        )}

        <div
          ref={scrollRef}
          className="flex gap-4 overflow-x-auto scroll-smooth pb-2"
          style={{ scrollbarWidth: "none" }}
        >
          {movies.map((movie) => (
            <div key={movie.movie_id} className="w-48 flex-shrink-0">
              <MovieCard movie={movie} />
            </div>
          ))}
        </div>

        {canScrollRight && (
          <button
            onClick={() => scroll("right")}
            className="absolute -right-1 top-1/2 z-10 -translate-y-1/2 rounded-full bg-black/70 p-2 text-white opacity-0 transition hover:bg-[#e50914] group-hover/row:opacity-100"
            aria-label="Scroll right"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        )}
      </div>
    </section>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [topRated, setTopRated] = useState([]);
  const [trending, setTrending] = useState([]);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsRes, topRes, trendingRes, recentRes] = await Promise.all([
          fetch("/api/stats"),
          fetch("/api/movies/top"),
          fetch("/api/movies/trending"),
          fetch("/api/movies/recent"),
        ]);

        if (statsRes.ok) setStats(await statsRes.json());
        if (topRes.ok) setTopRated(await topRes.json());
        if (trendingRes.ok) setTrending(await trendingRes.json());
        if (recentRes.ok) setRecent(await recentRes.json());
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-gray-600 border-t-[#e50914]" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <div className="mb-10 flex flex-wrap gap-4">
        <StatCard
          label="Total Movies"
          value={stats?.total_movies?.toLocaleString()}
        />
        <StatCard
          label="People"
          value={stats?.total_people?.toLocaleString()}
        />
        <StatCard
          label="Users"
          value={stats?.total_users?.toLocaleString()}
        />
        <StatCard
          label="Ratings"
          value={stats?.total_ratings?.toLocaleString()}
        />
      </div>

      <ScrollRow title="Top Rated" movies={topRated} />
      <ScrollRow title="Trending" movies={trending} />
      <ScrollRow title="Recently Released" movies={recent} />
    </div>
  );
}

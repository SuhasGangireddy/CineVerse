import { useState, useEffect } from "react";

const TABS = ["Add Movie", "Submit Rating", "Update Availability"];
const ACCESS_TYPES = ["subscription", "rent", "buy", "free"];

function FormField({ label, children }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-sm font-medium text-gray-300">{label}</label>
      {children}
    </div>
  );
}

const inputClass =
  "w-full px-3 py-2 rounded text-sm text-white border border-gray-700 focus:outline-none focus:border-[#e50914] placeholder-gray-600";
const inputStyle = { background: "#1f1f1f" };

export default function Admin() {
  const [activeTab, setActiveTab] = useState(0);
  const [message, setMessage] = useState(null);

  const [movieForm, setMovieForm] = useState({
    title: "",
    imdb_id: "",
    year: "",
    runtime: "",
    language: "",
    plot: "",
  });

  const [users, setUsers] = useState([]);
  const [ratingForm, setRatingForm] = useState({
    user_id: "",
    movie_id: "",
    rating: 5,
  });

  const [platforms, setPlatforms] = useState([]);
  const [availForm, setAvailForm] = useState({
    movie_id: "",
    platform: "",
    region: "",
    access_type: "",
  });

  useEffect(() => {
    fetch("/api/users")
      .then((res) => res.json())
      .then((data) => setUsers(Array.isArray(data) ? data : []))
      .catch(() => {});

    fetch("/api/platforms")
      .then((res) => res.json())
      .then((data) => setPlatforms(Array.isArray(data) ? data : []))
      .catch(() => {});
  }, []);

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 4000);
  };

  const handleAddMovie = async (e) => {
    e.preventDefault();
    try {
      const body = {
        ...movieForm,
        year: movieForm.year ? Number(movieForm.year) : undefined,
        runtime: movieForm.runtime ? Number(movieForm.runtime) : undefined,
      };
      const res = await fetch("/api/admin/movies", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || err.message || `Error ${res.status}`);
      }
      showMessage("success", "Movie added successfully!");
      setMovieForm({ title: "", imdb_id: "", year: "", runtime: "", language: "", plot: "" });
    } catch (err) {
      showMessage("error", err.message);
    }
  };

  const handleSubmitRating = async (e) => {
    e.preventDefault();
    try {
      const body = {
        user_id: Number(ratingForm.user_id),
        movie_id: Number(ratingForm.movie_id),
        rating: Number(ratingForm.rating),
      };
      const res = await fetch("/api/ratings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || err.message || `Error ${res.status}`);
      }
      showMessage("success", "Rating submitted successfully!");
      setRatingForm({ user_id: "", movie_id: "", rating: 5 });
    } catch (err) {
      showMessage("error", err.message);
    }
  };

  const handleUpdateAvailability = async (e) => {
    e.preventDefault();
    try {
      const body = {
        movie_id: Number(availForm.movie_id),
        platform: availForm.platform,
        region: availForm.region,
        access_type: availForm.access_type,
      };
      const res = await fetch("/api/admin/availability", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || err.message || `Error ${res.status}`);
      }
      showMessage("success", "Availability updated successfully!");
      setAvailForm({ movie_id: "", platform: "", region: "", access_type: "" });
    } catch (err) {
      showMessage("error", err.message);
    }
  };

  return (
    <div className="min-h-screen px-6 py-10 max-w-4xl mx-auto" style={{ background: "#141414" }}>
      <h1 className="text-4xl font-bold text-white mb-8">Admin Panel</h1>

      <div className="flex gap-1 mb-8 border-b" style={{ borderColor: "#333" }}>
        {TABS.map((tab, idx) => (
          <button
            key={tab}
            onClick={() => { setActiveTab(idx); setMessage(null); }}
            className="px-5 py-3 text-sm font-semibold transition-colors cursor-pointer rounded-t-lg"
            style={{
              background: activeTab === idx ? "#1f1f1f" : "transparent",
              color: activeTab === idx ? "#fff" : "#888",
              borderBottom: activeTab === idx ? "2px solid #e50914" : "2px solid transparent",
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {message && (
        <div
          className="mb-6 px-4 py-3 rounded-lg text-sm font-medium"
          style={{
            background: "#2a2a2a",
            color: message.type === "success" ? "#4ade80" : "#e50914",
          }}
        >
          {message.text}
        </div>
      )}

      {activeTab === 0 && (
        <form onSubmit={handleAddMovie} className="p-6 rounded-lg grid grid-cols-1 sm:grid-cols-2 gap-5" style={{ background: "#1f1f1f" }}>
          <FormField label="Title *">
            <input
              type="text"
              required
              value={movieForm.title}
              onChange={(e) => setMovieForm({ ...movieForm, title: e.target.value })}
              placeholder="Movie title"
              className={inputClass}
              style={inputStyle}
            />
          </FormField>

          <FormField label="IMDb ID">
            <input
              type="text"
              value={movieForm.imdb_id}
              onChange={(e) => setMovieForm({ ...movieForm, imdb_id: e.target.value })}
              placeholder="tt1234567"
              className={inputClass}
              style={inputStyle}
            />
          </FormField>

          <FormField label="Year">
            <input
              type="number"
              value={movieForm.year}
              onChange={(e) => setMovieForm({ ...movieForm, year: e.target.value })}
              placeholder="2024"
              min={1888}
              max={2100}
              className={inputClass}
              style={inputStyle}
            />
          </FormField>

          <FormField label="Runtime (min)">
            <input
              type="number"
              value={movieForm.runtime}
              onChange={(e) => setMovieForm({ ...movieForm, runtime: e.target.value })}
              placeholder="120"
              min={1}
              className={inputClass}
              style={inputStyle}
            />
          </FormField>

          <FormField label="Language">
            <input
              type="text"
              value={movieForm.language}
              onChange={(e) => setMovieForm({ ...movieForm, language: e.target.value })}
              placeholder="English"
              className={inputClass}
              style={inputStyle}
            />
          </FormField>

          <div className="sm:col-span-2">
            <FormField label="Plot">
              <textarea
                value={movieForm.plot}
                onChange={(e) => setMovieForm({ ...movieForm, plot: e.target.value })}
                placeholder="Brief plot summary..."
                rows={3}
                className={inputClass + " resize-y"}
                style={inputStyle}
              />
            </FormField>
          </div>

          <div className="sm:col-span-2 pt-2">
            <button
              type="submit"
              className="px-6 py-2.5 rounded-lg text-white font-semibold text-sm transition-colors cursor-pointer"
              style={{ background: "#e50914" }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "#b8070f")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "#e50914")}
            >
              Add Movie
            </button>
          </div>
        </form>
      )}

      {activeTab === 1 && (
        <form onSubmit={handleSubmitRating} className="p-6 rounded-lg grid grid-cols-1 sm:grid-cols-2 gap-5" style={{ background: "#1f1f1f" }}>
          <FormField label="User *">
            <select
              required
              value={ratingForm.user_id}
              onChange={(e) => setRatingForm({ ...ratingForm, user_id: e.target.value })}
              className={inputClass + " cursor-pointer"}
              style={inputStyle}
            >
              <option value="">-- Select User --</option>
              {users.map((u) => {
                const id = u.user_id || u.id;
                const name = u.username || u.name || `User ${id}`;
                return (
                  <option key={id} value={id}>
                    {name}
                  </option>
                );
              })}
            </select>
          </FormField>

          <FormField label="Movie ID *">
            <input
              type="number"
              required
              value={ratingForm.movie_id}
              onChange={(e) => setRatingForm({ ...ratingForm, movie_id: e.target.value })}
              placeholder="Movie ID"
              min={1}
              className={inputClass}
              style={inputStyle}
            />
          </FormField>

          <div className="sm:col-span-2">
            <FormField label={`Rating: ${ratingForm.rating}`}>
              <input
                type="range"
                min={0}
                max={10}
                step={0.5}
                value={ratingForm.rating}
                onChange={(e) => setRatingForm({ ...ratingForm, rating: parseFloat(e.target.value) })}
                className="w-full accent-[#e50914]"
              />
              <div className="flex justify-between text-xs text-gray-600 mt-1">
                <span>0</span>
                <span>5</span>
                <span>10</span>
              </div>
            </FormField>
          </div>

          <div className="sm:col-span-2 pt-2">
            <button
              type="submit"
              className="px-6 py-2.5 rounded-lg text-white font-semibold text-sm transition-colors cursor-pointer"
              style={{ background: "#e50914" }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "#b8070f")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "#e50914")}
            >
              Submit Rating
            </button>
          </div>
        </form>
      )}

      {activeTab === 2 && (
        <form onSubmit={handleUpdateAvailability} className="p-6 rounded-lg grid grid-cols-1 sm:grid-cols-2 gap-5" style={{ background: "#1f1f1f" }}>
          <FormField label="Movie ID *">
            <input
              type="number"
              required
              value={availForm.movie_id}
              onChange={(e) => setAvailForm({ ...availForm, movie_id: e.target.value })}
              placeholder="Movie ID"
              min={1}
              className={inputClass}
              style={inputStyle}
            />
          </FormField>

          <FormField label="Platform *">
            <select
              required
              value={availForm.platform}
              onChange={(e) => setAvailForm({ ...availForm, platform: e.target.value })}
              className={inputClass + " cursor-pointer"}
              style={inputStyle}
            >
              <option value="">-- Select Platform --</option>
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
          </FormField>

          <FormField label="Region">
            <input
              type="text"
              value={availForm.region}
              onChange={(e) => setAvailForm({ ...availForm, region: e.target.value })}
              placeholder="US"
              className={inputClass}
              style={inputStyle}
            />
          </FormField>

          <FormField label="Access Type *">
            <select
              required
              value={availForm.access_type}
              onChange={(e) => setAvailForm({ ...availForm, access_type: e.target.value })}
              className={inputClass + " cursor-pointer"}
              style={inputStyle}
            >
              <option value="">-- Select Type --</option>
              {ACCESS_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </option>
              ))}
            </select>
          </FormField>

          <div className="sm:col-span-2 pt-2">
            <button
              type="submit"
              className="px-6 py-2.5 rounded-lg text-white font-semibold text-sm transition-colors cursor-pointer"
              style={{ background: "#e50914" }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "#b8070f")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "#e50914")}
            >
              Update Availability
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

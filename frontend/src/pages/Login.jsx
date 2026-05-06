import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const STORAGE_KEY = "cineverse_user";

const DEMO_PROFILES = [
  { icon: "🎬", label: "Alex", desc: "Loves dramas & thrillers" },
  { icon: "🍿", label: "Priya", desc: "Anime & world cinema fan" },
  { icon: "🎭", label: "Jordan", desc: "Action & sci-fi buff" },
  { icon: "🌟", label: "Sam", desc: "Award-winning film enthusiast" },
  { icon: "🎵", label: "Riley", desc: "Comedy & feel-good vibes" },
];

export default function Login() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      navigate("/home", { replace: true });
      return;
    }

    fetch("/api/users")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch users");
        return res.json();
      })
      .then((data) => {
        setUsers(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [navigate]);

  const handleLogin = (profileIndex) => {
    if (!users.length) return;
    const dbUser = users[profileIndex];
    if (!dbUser) return;
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        user_id: dbUser.user_id,
        username: DEMO_PROFILES[profileIndex].label,
      })
    );
    navigate("/home");
  };

  const handleGuest = () => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ user_id: null, username: "Guest" })
    );
    navigate("/home");
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#141414] px-4">
      <div className="w-full max-w-lg rounded-xl bg-[#1f1f1f] p-10 shadow-2xl">
        <div className="mb-8 text-center">
          <h1 className="text-5xl font-extrabold tracking-tight text-[#e50914]">
            CineVerse
          </h1>
          <p className="mt-3 text-gray-400">
            Discover, rate, and watch movies intelligently.
          </p>
        </div>

        <div className="mb-6 h-px bg-gray-700" />

        {loading && (
          <div className="flex justify-center py-8">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-gray-600 border-t-[#e50914]" />
          </div>
        )}

        {error && (
          <div className="mb-4 rounded-lg bg-red-900/40 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        {!loading && !error && (
          <>
            <p className="mb-4 text-sm font-medium text-gray-300">
              Who's watching?
            </p>

            <div className="grid grid-cols-3 gap-4 sm:grid-cols-5 mb-6">
              {DEMO_PROFILES.map((profile, i) => (
                <button
                  key={profile.label}
                  onClick={() => setSelected(i)}
                  disabled={!users[i]}
                  className={`flex flex-col items-center gap-2 rounded-lg p-3 transition cursor-pointer
                    ${selected === i
                      ? "bg-[#e50914]/20 ring-2 ring-[#e50914]"
                      : "bg-[#2b2b2b] hover:bg-[#333] hover:ring-1 hover:ring-gray-500"
                    }
                    disabled:opacity-30 disabled:cursor-not-allowed`}
                >
                  <div className="text-3xl">{profile.icon}</div>
                  <span className="text-sm font-semibold text-white">
                    {profile.label}
                  </span>
                  <span className="text-[10px] text-gray-500 leading-tight text-center">
                    {profile.desc}
                  </span>
                </button>
              ))}
            </div>

            <button
              onClick={() => selected !== null && handleLogin(selected)}
              disabled={selected === null}
              className="mb-3 w-full rounded-lg bg-[#e50914] px-4 py-3 font-semibold text-white transition hover:bg-[#f6121d] disabled:cursor-not-allowed disabled:opacity-40"
            >
              Sign In{selected !== null ? ` as ${DEMO_PROFILES[selected].label}` : ""}
            </button>

            <div className="my-4 flex items-center gap-3">
              <span className="h-px flex-1 bg-gray-700" />
              <span className="text-xs uppercase tracking-wider text-gray-500">or</span>
              <span className="h-px flex-1 bg-gray-700" />
            </div>

            <button
              onClick={handleGuest}
              className="w-full rounded-lg border border-gray-600 px-4 py-3 font-semibold text-gray-300 transition hover:border-gray-400 hover:text-white"
            >
              Continue as Guest
            </button>
          </>
        )}
      </div>
    </div>
  );
}

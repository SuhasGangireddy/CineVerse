import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'

const navLinks = [
  { to: '/home', label: 'Home' },
  { to: '/search', label: 'Search' },
  { to: '/recommendations', label: 'Recommendations' },
  { to: '/watchlist', label: 'Watchlist' },
  { to: '/group-watch', label: 'Group Watch' },
  { to: '/insights', label: 'Insights' },
  { to: '/admin', label: 'Admin' },
]

export default function Navbar() {
  const location = useLocation()
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [menuOpen, setMenuOpen] = useState(false)

  const handleLogout = () => {
    localStorage.removeItem('cineverse_user')
    setUser(null)
    navigate('/')
  }

  useEffect(() => {
    try {
      const stored = localStorage.getItem('cineverse_user')
      if (stored) {
        setUser(JSON.parse(stored))
      }
    } catch {
      setUser(null)
    }
  }, [location.pathname])

  // Hide navbar on login page
  if (location.pathname === '/') return null

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#141414]/95 backdrop-blur-sm border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link to="/home" className="text-2xl font-bold tracking-wide text-[#e50914] shrink-0">
          CineVerse
        </Link>

        {/* Desktop nav links */}
        <div className="hidden lg:flex items-center gap-1 ml-8">
          {navLinks.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                location.pathname === to
                  ? 'text-white bg-white/10'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              {label}
            </Link>
          ))}
        </div>

        {/* Right side: user display */}
        <div className="flex items-center gap-4 ml-auto pl-4">
          {user ? (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-[#e50914] flex items-center justify-center text-white text-sm font-bold">
                  {user.username?.charAt(0)?.toUpperCase() || 'U'}
                </div>
                <span className="hidden sm:inline text-sm text-gray-300">
                  {user.username}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="px-3 py-1.5 rounded text-xs font-medium text-gray-400 border border-gray-600 hover:text-white hover:border-gray-400 transition-colors"
              >
                Logout
              </button>
            </div>
          ) : (
            <Link
              to="/"
              className="px-4 py-1.5 rounded bg-[#e50914] text-white text-sm font-medium hover:bg-[#f40612] transition-colors"
            >
              Login
            </Link>
          )}

          {/* Mobile menu button */}
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="lg:hidden text-gray-400 hover:text-white p-1"
            aria-label="Toggle menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {menuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="lg:hidden bg-[#1a1a1a] border-t border-white/10 px-4 py-2">
          {navLinks.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              onClick={() => setMenuOpen(false)}
              className={`block px-3 py-2 rounded text-sm font-medium transition-colors ${
                location.pathname === to
                  ? 'text-white bg-white/10'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              {label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  )
}

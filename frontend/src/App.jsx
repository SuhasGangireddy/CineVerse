import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import Navbar from './components/Navbar'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Search from './pages/Search'
import MovieDetail from './pages/MovieDetail'
import Watchlist from './pages/Watchlist'
import Recommendations from './pages/Recommendations'
import GroupWatch from './pages/GroupWatch'
import Insights from './pages/Insights'
import Admin from './pages/Admin'

function AppContent() {
  const location = useLocation()
  const isLogin = location.pathname === '/'

  return (
    <div className="min-h-screen bg-[#141414]">
      <Navbar />
      <main className={isLogin ? '' : 'pt-16'}>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/home" element={<Dashboard />} />
          <Route path="/search" element={<Search />} />
          <Route path="/movie/:id" element={<MovieDetail />} />
          <Route path="/watchlist" element={<Watchlist />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/group-watch" element={<GroupWatch />} />
          <Route path="/insights" element={<Insights />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

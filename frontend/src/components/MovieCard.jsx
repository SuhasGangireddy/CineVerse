import { useNavigate } from 'react-router-dom'

function RatingBadge({ rating }) {
  if (rating == null) return null

  const num = Number(rating)
  let color = 'bg-red-600'
  if (num >= 8) color = 'bg-green-600'
  else if (num >= 6) color = 'bg-yellow-600'

  return (
    <span className={`${color} text-white text-xs font-bold px-1.5 py-0.5 rounded`}>
      {num.toFixed(1)}
    </span>
  )
}

function PosterPlaceholder() {
  return (
    <div className="w-full aspect-[2/3] bg-[#2a2a2a] flex items-center justify-center">
      <svg className="w-12 h-12 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M7 4v16M17 4v16M3 8h4M17 8h4M3 12h18M3 16h4M17 16h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"
        />
      </svg>
    </div>
  )
}

export default function MovieCard({ movie }) {
  const navigate = useNavigate()

  const {
    movie_id,
    title,
    release_year,
    imdb_rating,
    genres_raw,
    poster_url,
    runtime_minutes,
  } = movie

  const genres = genres_raw
    ? genres_raw.split(',').map((g) => g.trim()).filter(Boolean)
    : []

  return (
    <div
      onClick={() => navigate(`/movie/${movie_id}`)}
      className="bg-[#1f1f1f] rounded-lg overflow-hidden cursor-pointer transition-transform duration-200 hover:scale-105 hover:shadow-xl hover:shadow-black/40 group/card"
    >
      {/* Poster */}
      {poster_url ? (
        <img
          src={poster_url}
          alt={title}
          className="w-full aspect-[2/3] object-cover"
          loading="lazy"
        />
      ) : (
        <PosterPlaceholder />
      )}

      {/* Info */}
      <div className="p-3">
        <h3 className="text-white font-semibold text-sm leading-tight truncate group-hover/card:text-[#e50914] transition-colors">
          {title}
        </h3>

        <div className="flex items-center gap-2 mt-1.5">
          {release_year && (
            <span className="text-gray-400 text-xs">{release_year}</span>
          )}
          {runtime_minutes && (
            <span className="text-gray-500 text-xs">{runtime_minutes} min</span>
          )}
          <RatingBadge rating={imdb_rating} />
        </div>

        {/* Genre chips */}
        {genres.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {genres.slice(0, 3).map((genre) => (
              <span
                key={genre}
                className="text-[10px] px-1.5 py-0.5 rounded-full bg-white/10 text-gray-300"
              >
                {genre}
              </span>
            ))}
            {genres.length > 3 && (
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-white/10 text-gray-500">
                +{genres.length - 3}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

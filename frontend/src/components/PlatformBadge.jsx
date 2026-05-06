export default function PlatformBadge({ name, access_type }) {
  const colors = {
    subscription: 'bg-green-900/50 text-green-300 border-green-700',
    rent: 'bg-yellow-900/50 text-yellow-300 border-yellow-700',
    buy: 'bg-blue-900/50 text-blue-300 border-blue-700',
    free: 'bg-gray-800 text-gray-300 border-gray-600',
    theater: 'bg-purple-900/50 text-purple-300 border-purple-700',
  }

  const colorClass = colors[access_type] || colors.free

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${colorClass}`}>
      <span>{name}</span>
      {access_type && (
        <span className="opacity-70 capitalize">{access_type}</span>
      )}
    </span>
  )
}

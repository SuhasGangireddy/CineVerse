export default function TagChip({ name, selected = false, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1 rounded-full text-xs font-medium transition-colors cursor-pointer ${
        selected
          ? 'bg-[#e50914] text-white'
          : 'bg-white/10 text-gray-300 hover:bg-white/20'
      }`}
    >
      {name}
    </button>
  )
}

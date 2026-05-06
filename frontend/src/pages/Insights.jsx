import { useState, useEffect } from "react";

export default function Insights() {
  const [queries, setQueries] = useState([]);
  const [activeQuery, setActiveQuery] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingQueries, setLoadingQueries] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/insights")
      .then((res) => res.json())
      .then((data) => {
        setQueries(Array.isArray(data) ? data : []);
        setLoadingQueries(false);
      })
      .catch(() => setLoadingQueries(false));
  }, []);

  const handleQueryClick = async (query) => {
    const queryId = query.query_id || query.id;

    // toggle off if clicking the same one
    if (activeQuery === queryId) {
      setActiveQuery(null);
      setResult(null);
      return;
    }

    setActiveQuery(queryId);
    setResult(null);
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`/api/insights/${queryId}`);
      if (!res.ok) throw new Error(`Failed to fetch query result (${res.status})`);
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const resultRows = result
    ? Array.isArray(result)
      ? result
      : result.rows || result.data || result.results || []
    : [];

  const columns =
    resultRows.length > 0 ? Object.keys(resultRows[0]) : [];

  return (
    <div className="min-h-screen px-6 py-10 max-w-7xl mx-auto" style={{ background: "#141414" }}>
      <h1 className="text-4xl font-bold text-white mb-1">Database Insights</h1>
      <p className="text-gray-400 text-lg mb-8">10 Complex SQL Queries</p>

      {loadingQueries && <p className="text-gray-500">Loading queries...</p>}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-8">
        {queries.map((query, index) => {
          const queryId = query.query_id || query.id;
          const isActive = activeQuery === queryId;
          return (
            <button
              key={queryId || index}
              onClick={() => handleQueryClick(query)}
              className="text-left p-4 rounded-lg transition-all cursor-pointer border"
              style={{
                background: isActive ? "#2a2a2a" : "#1f1f1f",
                borderColor: isActive ? "#e50914" : "transparent",
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.borderColor = "#444";
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.borderColor = "transparent";
              }}
            >
              <div
                className="text-xs font-bold mb-2 inline-block px-2 py-0.5 rounded"
                style={{ background: isActive ? "#e50914" : "#333", color: "#fff" }}
              >
                #{index + 1}
              </div>
              <h3 className="text-white font-semibold text-sm mb-1 leading-snug">
                {query.title || query.name || `Query ${index + 1}`}
              </h3>
              {query.description && (
                <p className="text-gray-500 text-xs leading-relaxed line-clamp-3">
                  {query.description}
                </p>
              )}
            </button>
          );
        })}
      </div>

      {activeQuery != null && (
        <section className="rounded-lg overflow-hidden" style={{ background: "#1f1f1f" }}>
          <div className="px-5 py-4 border-b" style={{ borderColor: "#333" }}>
            <h2 className="text-lg font-semibold text-white">
              Query #{queries.findIndex((q) => (q.query_id || q.id) === activeQuery) + 1} Results
            </h2>
          </div>

          {loading && (
            <div className="p-6 text-gray-400">Loading results...</div>
          )}

          {error && (
            <div className="p-6 text-sm" style={{ color: "#e50914" }}>
              {error}
            </div>
          )}

          {!loading && !error && resultRows.length === 0 && result != null && (
            <div className="p-6 text-gray-500">No results returned.</div>
          )}

          {!loading && !error && resultRows.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead>
                  <tr style={{ background: "#2a2a2a" }}>
                    {columns.map((col) => (
                      <th
                        key={col}
                        className="px-4 py-3 font-semibold text-gray-300 whitespace-nowrap"
                        style={{ borderBottom: "2px solid #e50914" }}
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {resultRows.map((row, rowIdx) => (
                    <tr
                      key={rowIdx}
                      style={{
                        background: rowIdx % 2 === 0 ? "#1f1f1f" : "#262626",
                      }}
                      className="hover:brightness-125 transition-all"
                    >
                      {columns.map((col) => (
                        <td
                          key={col}
                          className="px-4 py-3 text-gray-300 whitespace-nowrap"
                          style={{ borderBottom: "1px solid #333" }}
                        >
                          {row[col] != null ? String(row[col]) : ""}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </div>
  );
}

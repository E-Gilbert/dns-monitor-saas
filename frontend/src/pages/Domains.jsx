import { useEffect, useState } from "react"
import api from "../api/api"

function Domains() {
  const [domains, setDomains] = useState([])
  const [historyByDomainId, setHistoryByDomainId] = useState({})
  const [historyLoadingByDomainId, setHistoryLoadingByDomainId] = useState({})
  const [historyErrorByDomainId, setHistoryErrorByDomainId] = useState({})
  const [domainsError, setDomainsError] = useState(null)

  useEffect(() => {
    let cancelled = false

    async function loadDomainsAndHistory() {
      setDomainsError(null)

      try {
        const res = await api.get("/domains")
        if (cancelled) return

        const nextDomains = Array.isArray(res.data) ? res.data : []
        setDomains(nextDomains)

        // Load history per domain so the dashboard can show AI Insight blocks.
        // If any domain history call fails, we show an error just for that card.
        const loadingMap = {}
        nextDomains.forEach((d) => {
          loadingMap[d.id] = true
        })
        setHistoryLoadingByDomainId(loadingMap)

        await Promise.all(
          nextDomains.map(async (d) => {
            try {
              const historyRes = await api.get(`/domains/${d.id}/history`)
              if (cancelled) return

              const history = Array.isArray(historyRes.data)
                ? historyRes.data
                : []
              setHistoryByDomainId((prev) => ({ ...prev, [d.id]: history }))
              setHistoryErrorByDomainId((prev) => ({ ...prev, [d.id]: null }))
            } catch (error) {
              // Keep UI resilient while still logging the real error for debugging.
              console.error(`Failed to load history for domain ${d.id}:`, error)
              if (cancelled) return
              setHistoryErrorByDomainId((prev) => ({
                ...prev,
                [d.id]: "Error loading DNS history.",
              }))
              setHistoryByDomainId((prev) => ({ ...prev, [d.id]: [] }))
            } finally {
              if (!cancelled) {
                setHistoryLoadingByDomainId((prev) => ({
                  ...prev,
                  [d.id]: false,
                }))
              }
            }
          })
        )
      } catch (error) {
        // Log actual request error (status/network) instead of only generic UI text.
        console.error("Error fetching domains:", error)
        if (cancelled) return
        setDomains([])
        const serverMessage = error?.response?.data?.detail
        const status = error?.response?.status
        const networkMessage = error?.message
        setDomainsError(
          serverMessage
            ? `Error fetching domains: ${serverMessage}`
            : status
              ? `Error fetching domains (HTTP ${status}).`
              : `Error fetching domains: ${networkMessage || "Network error"}`
        )
      }
    }

    loadDomainsAndHistory()

    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="p-10">
      <h1 className="text-2xl font-bold mb-6">Domains</h1>

      {domainsError ? (
        <p className="text-red-600 mb-4">{domainsError}</p>
      ) : null}

      {domains.length === 0 ? (
        <p>{domainsError ? " " : "No domains found"}</p>
      ) : (
        <div className="space-y-4">
          {domains.map((d) => (
            <div
              key={d.id}
              className="bg-white p-4 rounded shadow"
            >
              {d.name}

              <div className="mt-4">
                {historyLoadingByDomainId?.[d.id] ? (
                  <p className="text-sm text-gray-600">Loading DNS changes...</p>
                ) : null}

                {historyErrorByDomainId?.[d.id] ? (
                  <p className="text-sm text-red-600">
                    {historyErrorByDomainId[d.id]}
                  </p>
                ) : null}

                {historyLoadingByDomainId?.[d.id] ? null : (
                  (() => {
                    const history = historyByDomainId?.[d.id] || []
                    const changedEvents = (history || []).filter(
                      (h) => Boolean(h?.changed)
                    )
                    const recentChanges = changedEvents.slice(0, 10)

                    if (recentChanges.length === 0) {
                      return (
                        <p className="text-sm text-gray-600 mt-2">
                          No DNS changes yet
                        </p>
                      )
                    }

                    return (
                      <div className="space-y-3 mt-2">
                        {recentChanges.map((h) => (
                          <div
                            key={h.id}
                            className="bg-gray-50 p-3 rounded"
                          >
                            <div className="text-sm text-gray-700">
                              <span className="font-semibold">
                                {h?.record_type || "DNS"}
                              </span>
                              :{" "}
                              {h?.change ||
                                (h?.previous_value &&
                                h?.resolved_value
                                  ? `${h.previous_value} -> ${h.resolved_value}`
                                  : "Change detected")}
                            </div>

                            {/* Frontend display: show AI Insight under each DNS change. */}
                            <div className="mt-2 text-sm">
                              <div className="font-semibold">AI Insight</div>
                              <div className="text-gray-800">
                                {h?.insight ? h.insight : "No insight available"}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )
                  })()
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Domains
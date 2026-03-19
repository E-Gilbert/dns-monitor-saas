import { useEffect, useState } from "react"
import api from "../api/api"

function Domains() {
  const [domains, setDomains] = useState([])

  useEffect(() => {
    api.get("/domains")
      .then((res) => {
        console.log("Domains from API:", res.data)
        setDomains(res.data)
      })
      .catch((err) => {
        console.error("Error fetching domains:", err)
      })
  }, [])

  return (
    <div className="p-10">
      <h1 className="text-2xl font-bold mb-6">Domains</h1>

      {domains.length === 0 ? (
        <p>No domains found</p>
      ) : (
        <div className="space-y-4">
          {domains.map((d) => (
            <div
              key={d.id}
              className="bg-white p-4 rounded shadow"
            >
              {d.name}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Domains
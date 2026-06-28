import { useEffect, useState } from "react";
import "./App.css";

type Detection = {
  id: number;
  label: string;
  confidence: number;
  x: number;
  y: number;
  width: number;
  height: number;
  detected_at: string;
};

const API = import.meta.env.VITE_API_URL ?? "http://localhost:8080";

function App() {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`${API}/detections?limit=50`);
        if (!res.ok) throw new Error(`API ${res.status}`);
        setDetections(await res.json());
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : "fetch failed");
      }
    };
    load();
    const id = setInterval(load, 1000);
    return () => clearInterval(id);
  }, []);

  const counts = detections.reduce<Record<string, number>>((acc, d) => {
    acc[d.label] = (acc[d.label] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <div className="app">
      <header>
        <h1>Robot Perception</h1>
        <span className={error ? "status err" : "status ok"}>
          {error ? `disconnected (${error})` : "live"}
        </span>
      </header>

      <section className="summary">
        {Object.entries(counts).map(([label, n]) => (
          <div key={label} className="chip">
            <strong>{n}</strong> {label}
          </div>
        ))}
      </section>

      <table>
        <thead>
          <tr>
            <th>id</th><th>label</th><th>confidence</th><th>box (x,y,w,h)</th><th>time</th>
          </tr>
        </thead>
        <tbody>
          {detections.map((d) => (
            <tr key={d.id}>
              <td>{d.id}</td>
              <td>{d.label}</td>
              <td>{(d.confidence * 100).toFixed(1)}%</td>
              <td>{d.x}, {d.y}, {d.width}, {d.height}</td>
              <td>{new Date(d.detected_at).toLocaleTimeString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;

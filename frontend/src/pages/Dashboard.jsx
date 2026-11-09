import { useMemo, useState } from "react";
import LineChart from "../components/LineChart";
import SensorStatus from "../components/SensorStatus";
import { useHistory } from "../hooks/useHistory";

const metrics = [
  { key: "temperature", label: "Temperature (C)", short: "T", color: "#ff5c7a" },
  { key: "humidity", label: "Humidity (%)", short: "H", color: "#4da3ff" },
  { key: "co2", label: "CO2 (ppm)", short: "C", color: "#f3c74f" },
  { key: "lighting", label: "Lighting (lux)", short: "L", color: "#7dd3fc" },
];

export default function Dashboard() {
  const [mode, setMode] = useState("realtime");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [visible, setVisible] = useState(Object.fromEntries(metrics.map(({ key }) => [key, true])));
  const { data, error, loading } = useHistory({ mode, startDate, endDate });
  const labels = useMemo(() => data.map(({ time }) => {
    const date = new Date(time);
    return mode === "day" || mode === "month" ? date.toLocaleDateString() : date.toLocaleString();
  }), [data, mode]);
  const datasets = useMemo(() => metrics.filter(({ key }) => visible[key]).map(({ key, label, color }) => ({
    label, yAxisID: key, data: data.map((item) => item[key]), borderColor: color,
    pointRadius: 1, tension: 0.2, spanGaps: false,
  })), [data, visible]);
  function reset() { setMode("realtime"); setStartDate(""); setEndDate(""); }
  return <main className="perf-page">
    <h1 className="dashboard-title">Environmental Metrics</h1>
    <SensorStatus />
    <div className="perf-controls">
      <div className="mode-switch" aria-label="Aggregation mode">
        {["realtime", "minute", "hour", "day", "month"].map((value) => <button key={value}
          type="button" className={`mode-btn ${mode === value ? "is-active" : ""}`}
          aria-pressed={mode === value} onClick={() => setMode(value)}>{value}</button>)}
      </div>
      <div className="perf-field">
        <input className="perf-input" aria-label="Start date" type="date" value={startDate}
          onChange={(event) => setStartDate(event.target.value)} />
        <span className="perf-sep">to</span>
        <input className="perf-input" aria-label="End date" type="date" value={endDate}
          onChange={(event) => setEndDate(event.target.value)} />
      </div>
      <button type="button" className="perf-reset" onClick={reset}>Reset All</button>
      <div className="metric-toggles" aria-label="Metric visibility">
        {metrics.map(({ key, label, short, color }) => <button key={key} type="button"
          className={`metric-toggle ${visible[key] ? "is-active" : ""}`}
          aria-label={label} title={label} aria-pressed={visible[key]} style={{ "--metric-color": color }}
          onClick={() => setVisible((previous) => ({ ...previous, [key]: !previous[key] }))}>{short}</button>)}
      </div>
    </div>
    {error && <p role="alert">Could not update measurements: {error}. Last successful data is shown.</p>}
    <div className="perf-graph">{loading ? <p>Loading data...</p> :
      <LineChart labels={labels} datasets={datasets} />}</div>
  </main>;
}

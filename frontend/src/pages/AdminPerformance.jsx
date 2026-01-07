import React, { useState, useEffect, useCallback } from "react";
import LineChart from "../components/LineChart";

function MetricToggle({ active, color, label, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`metric-toggle ${active ? "is-active" : ""}`}
      style={{ "--metric-color": color }}
      aria-pressed={active}
      title={label}
    >
      {label}
    </button>
  );
}

export default function AdminPerformance() {
  const [rawData, setRawData] = useState([]);
  const [loading, setLoading] = useState(true);

  const [mode, setMode] = useState("realtime");
  const [visibleMetrics, setVisibleMetrics] = useState({
    temp: true,
    hum: true,
    co2: true,
  });

  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [limit, setLimit] = useState(100);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);

      let url = `http://localhost:8000/history?limit=${limit}`;

      if (mode !== "realtime") url += `&aggregate=${mode}`;
      if (startDate) url += `&start_date=${startDate}T00:00:00`;
      if (endDate) url += `&end_date=${endDate}T23:59:59`;

      const response = await fetch(url, { credentials: "include" });
      const json = await response.json();

      setRawData(Array.isArray(json) ? json : []);
    } catch (err) {
      console.error("Fetch error:", err);
      setRawData([]);
    } finally {
      setLoading(false);
    }
  }, [mode, limit, startDate, endDate]);

  useEffect(() => {
    fetchData();

    // Refresh every 10s for realtime/minute modes
    if (mode === "realtime" || mode === "minute") {
      const interval = setInterval(fetchData, 10000);
      return () => clearInterval(interval);
    }
  }, [fetchData, mode]);

  const toggleMetric = (key) => {
    setVisibleMetrics((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleReset = () => {
    setStartDate("");
    setEndDate("");
    setLimit(100);
    setMode("realtime");
  };

  const labels = rawData.map((item) => {
    const d = new Date(item.time);
    if (mode === "day" || mode === "month") {
      return d.toLocaleDateString([], { day: "2-digit", month: "2-digit" });
    }
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  });

  const datasets = [
    visibleMetrics.temp && {
      label: "Temp (°C)",
      data: rawData.map((i) => i.temperature),
      borderColor: "#ff5c7a",
      backgroundColor: "rgba(255, 92, 122, 0.18)",
      fill: true,
      tension: 0.3,
      pointRadius: 2,
    },
    visibleMetrics.hum && {
      label: "Hum (%)",
      data: rawData.map((i) => i.humidity),
      borderColor: "#4da3ff",
      backgroundColor: "rgba(77, 163, 255, 0.18)",
      fill: true,
      tension: 0.3,
      pointRadius: 2,
    },
    visibleMetrics.co2 && {
      label: "CO₂ (ppm)",
      data: rawData.map((i) => i.co2),
      borderColor: "#f3c74f",
      backgroundColor: "rgba(243, 199, 79, 0.18)",
      fill: true,
      tension: 0.3,
      pointRadius: 2,
    },
  ].filter(Boolean);

  const chartData = { labels, datasets };

  return (
    <div className="perf-page">
      <h1 className="dashboard-title">Environmental Performance</h1>

      <div className="perf-controls">
        <div className="mode-switch" role="tablist" aria-label="Aggregation mode">
          {["realtime", "minute", "hour", "day", "month"].map((m) => (
            <button
              key={m}
              type="button"
              className={`mode-btn ${mode === m ? "is-active" : ""}`}
              onClick={() => setMode(m)}
            >
              {m.charAt(0).toUpperCase() + m.slice(1)}
            </button>
          ))}
        </div>

        <div className="perf-field">
          <input
            className="perf-input"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
          <span className="perf-sep">—</span>
          <input
            className="perf-input"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>

        <button type="button" className="perf-reset" onClick={handleReset}>
          Reset All
        </button>

        <div className="metric-toggles" aria-label="Metric visibility">
          <MetricToggle
            active={visibleMetrics.temp}
            color="#ff5c7a"
            label="T"
            onClick={() => toggleMetric("temp")}
          />
          <MetricToggle
            active={visibleMetrics.hum}
            color="#4da3ff"
            label="H"
            onClick={() => toggleMetric("hum")}
          />
          <MetricToggle
            active={visibleMetrics.co2}
            color="#f3c74f"
            label="C"
            onClick={() => toggleMetric("co2")}
          />
        </div>
      </div>

      <div className="perf-graph">
        {loading ? (
          <div className="perf-loading">Loading data...</div>
        ) : (
          <LineChart key={mode} labels={chartData.labels} datasets={chartData.datasets} />
        )}
      </div>
    </div>
  );
}

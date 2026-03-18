import React, { useState, useEffect, useCallback, useMemo } from "react";
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

const API_BASE = import.meta.env.VITE_API_BASE;
const MAX_POINTS = 250;

function formatLabel(d, mode) {
  if (mode === "day" || mode === "month") {
    return d.toLocaleDateString([], { day: "2-digit", month: "2-digit" });
  }
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function AdminPerformance() {
  const [labels, setLabels] = useState([]);
  const [series, setSeries] = useState({
    temp: [],
    hum: [],
    co2: [],
    light: [],
  });

  const [lastTs, setLastTs] = useState(null);

  const [initialLoading, setInitialLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const [mode, setMode] = useState("realtime");
  const [visibleMetrics, setVisibleMetrics] = useState({
    temp: true,
    hum: true,
    co2: true,
    light: true,
  });

  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [limit, setLimit] = useState(100);

  const toggleMetric = (key) => {
    setVisibleMetrics((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleReset = () => {
    setStartDate("");
    setEndDate("");
    setLimit(100);
    setMode("realtime");
  };

  const buildUrl = useCallback(() => {
    let url = `${API_BASE}/history?limit=${limit}`;
    if (mode !== "realtime") url += `&aggregate=${mode}`;
    if (startDate) url += `&start_date=${startDate}T00:00:00`;
    if (endDate) url += `&end_date=${endDate}T23:59:59`;
    return url;
  }, [mode, limit, startDate, endDate]);

  const fullReload = useCallback(async () => {
    try {
      setInitialLoading(true);

      const url = buildUrl();
      const res = await fetch(url, { credentials: "include" });
      const json = await res.json();
      const arr = Array.isArray(json) ? json : [];

      const newLabels = [];
      const newTemp = [];
      const newHum = [];
      const newCo2 = [];
      const newLight = [];

      let newLastTs = null;

      for (const item of arr) {
        const d = new Date(item.time);
        const ts = d.getTime();
        newLastTs = ts;

        newLabels.push(formatLabel(d, mode));
        newTemp.push(item.temperature ?? null);
        newHum.push(item.humidity ?? null);
        newCo2.push(item.co2 ?? null);

        // lighting может приходить как lighting (из /history),
        // а из mqtt приходит lux, но мы рисуем из /history => lighting
        newLight.push(item.lighting ?? null);
      }

      const sliceFrom = Math.max(0, newLabels.length - MAX_POINTS);

      setLabels(newLabels.slice(sliceFrom));
      setSeries({
        temp: newTemp.slice(sliceFrom),
        hum: newHum.slice(sliceFrom),
        co2: newCo2.slice(sliceFrom),
        light: newLight.slice(sliceFrom),
      });
      setLastTs(newLastTs);
    } catch (e) {
      console.error("Full reload failed:", e);
    } finally {
      setInitialLoading(false);
    }
  }, [buildUrl, mode]);

  const appendUpdate = useCallback(async () => {
    if (!lastTs) {
      await fullReload();
      return;
    }

    try {
      setRefreshing(true);

      const url = buildUrl();
      const res = await fetch(url, { credentials: "include" });
      const json = await res.json();
      const arr = Array.isArray(json) ? json : [];

      const newItems = [];
      for (const item of arr) {
        const ts = new Date(item.time).getTime();
        if (ts > lastTs) newItems.push(item);
      }
      if (newItems.length === 0) return;

      setLabels((prev) => {
        const appended = [...prev];
        for (const item of newItems) {
          appended.push(formatLabel(new Date(item.time), mode));
        }
        return appended.slice(Math.max(0, appended.length - MAX_POINTS));
      });

      setSeries((prev) => {
        const t = [...prev.temp];
        const h = [...prev.hum];
        const c = [...prev.co2];
        const l = [...prev.light];

        for (const item of newItems) {
          t.push(item.temperature ?? null);
          h.push(item.humidity ?? null);
          c.push(item.co2 ?? null);
          l.push(item.lighting ?? null);
        }

        const cut = Math.max(0, t.length - MAX_POINTS);
        return {
          temp: t.slice(cut),
          hum: h.slice(cut),
          co2: c.slice(cut),
          light: l.slice(cut),
        };
      });

      const last = newItems[newItems.length - 1];
      setLastTs(new Date(last.time).getTime());
    } catch (e) {
      console.error("Append update failed:", e);
    } finally {
      setRefreshing(false);
    }
  }, [buildUrl, lastTs, mode, fullReload]);

  useEffect(() => {
    setLastTs(null);
    fullReload();
  }, [mode, startDate, endDate, limit, fullReload]);

  useEffect(() => {
    if (mode !== "realtime" && mode !== "minute") return;

    const id = setInterval(() => {
      appendUpdate();
    }, 10000);

    return () => clearInterval(id);
  }, [mode, appendUpdate]);

  const datasets = useMemo(() => {
    const arr = [];

    if (visibleMetrics.temp) {
      arr.push({
        label: "Temp (°C)",
        data: series.temp,
        borderColor: "#ff5c7a",
        backgroundColor: "rgba(255, 92, 122, 0.18)",
        fill: true,
        tension: 0.3,
        pointRadius: 2,
      });
    }

    if (visibleMetrics.hum) {
      arr.push({
        label: "Hum (%)",
        data: series.hum,
        borderColor: "#4da3ff",
        backgroundColor: "rgba(77, 163, 255, 0.18)",
        fill: true,
        tension: 0.3,
        pointRadius: 2,
      });
    }

    if (visibleMetrics.co2) {
      arr.push({
        label: "CO₂ (ppm)",
        data: series.co2,
        borderColor: "#f3c74f",
        backgroundColor: "rgba(243, 199, 79, 0.18)",
        fill: true,
        tension: 0.3,
        pointRadius: 2,
      });
    }

    if (visibleMetrics.light) {
      arr.push({
        label: "Lighting (lux)",
        data: series.light,
        borderColor: "#7dd3fc",
        backgroundColor: "rgba(125, 211, 252, 0.18)",
        fill: true,
        tension: 0.3,
        pointRadius: 2,
      });
    }

    return arr;
  }, [series, visibleMetrics]);

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
          <MetricToggle active={visibleMetrics.temp} color="#ff5c7a" label="T" onClick={() => toggleMetric("temp")} />
          <MetricToggle active={visibleMetrics.hum} color="#4da3ff" label="H" onClick={() => toggleMetric("hum")} />
          <MetricToggle active={visibleMetrics.co2} color="#f3c74f" label="C" onClick={() => toggleMetric("co2")} />
          <MetricToggle active={visibleMetrics.light} color="#7dd3fc" label="L" onClick={() => toggleMetric("light")} />
        </div>
      </div>

      <div className="perf-graph">
        {initialLoading ? (
          <div className="perf-loading">Loading data...</div>
        ) : (
          <>
            {refreshing && <div className="perf-refreshing">Updating…</div>}
            <LineChart labels={labels} datasets={datasets} />
          </>
        )}
      </div>
    </div>
  );
}
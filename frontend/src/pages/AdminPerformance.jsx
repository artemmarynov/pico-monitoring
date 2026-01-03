import React, { useState, useEffect, useCallback } from 'react';
import LineChart from "../components/LineChart";

function AdminPerformance() {
  const [rawData, setRawData] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [mode, setMode] = useState('realtime'); 
  const [visibleMetrics, setVisibleMetrics] = useState({ temp: true, hum: true, co2: true });
  
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [limit, setLimit] = useState(100);

  const fetchData = useCallback(async () => {
    try {
      let url = `http://localhost:8000/history?limit=${limit}`;
      
      if (mode !== 'realtime') {
        url += `&aggregate=${mode}`;
      }
      
      if (startDate) url += `&start_date=${startDate}T00:00:00`;
      if (endDate) url += `&end_date=${endDate}T23:59:59`;

      const response = await fetch(url);
      const json = await response.json();
      setRawData(json);
      setLoading(false);
    } catch (err) {
      console.error("Fetch error:", err);
      setLoading(false);
    }
  }, [mode, limit, startDate, endDate]);

  useEffect(() => {
    fetchData();
    // Refresh every 10 secs
    if (mode === 'realtime' || mode === 'minute') {
      const interval = setInterval(fetchData, 10000);
      return () => clearInterval(interval);
    }
  }, [fetchData, mode]);

  const chartData = {
    labels: rawData.map(item => {
      const d = new Date(item.time);
      if (mode === 'day' || mode === 'month') {
        return d.toLocaleDateString([], { day: '2-digit', month: '2-digit' });
      }
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }),
    datasets: [
      visibleMetrics.temp && {
        label: "Temp (°C)",
        data: rawData.map(item => item.temperature),
        borderColor: "#ff5b7f",
        backgroundColor: "rgba(255, 91, 127, 0.1)",
        yAxisID: 'y',
        fill: true,
        tension: 0.4,
      },
      visibleMetrics.hum && {
        label: "Hum (%)",
        data: rawData.map(item => item.humidity),
        borderColor: "#4fa3ff",
        backgroundColor: "rgba(79, 163, 255, 0.1)",
        yAxisID: 'y',
        fill: true,
        tension: 0.4,
      },
      visibleMetrics.co2 && {
        label: "CO2 (ppm)",
        data: rawData.map(item => item.co2),
        borderColor: "#ffc94d",
        backgroundColor: "rgba(255, 201, 77, 0.1)",
        yAxisID: 'y1',
        fill: true,
        tension: 0.4,
      }
    ].filter(Boolean)
  };

  const handleReset = () => {
    setStartDate('');
    setEndDate('');
    setLimit(100);
    setMode('realtime');
  };

  return (
    
    <div style={{ padding: "20px", color: "#fff", width: "100%", maxWidth: "1600px", margin: "0 auto" }}>
      <h1 className="dashboard-title">Environmental Performance</h1>

      {/* Control panel */}
      <div style={{ 
        background: '#252525', 
        padding: '20px', 
        borderRadius: '12px', 
        display: 'flex', 
        gap: '20px', 
        alignItems: 'center', 
        flexWrap: 'wrap',
        marginBottom: '20px',
        border: '1px solid #333'
      }}>
        
        {/* Aggregation mode switch */}
        <div style={{ display: 'flex', background: '#1a1a1a', borderRadius: '8px', padding: '4px' }}>
          {['realtime', 'minute', 'hour', 'day', 'month'].map((m) => (
            <button 
              key={m}
              onClick={() => setMode(m)}
              style={{
                ...modeBtnStyle,
                background: mode === m ? '#4fa3ff' : 'transparent',
                color: mode === m ? '#fff' : '#888'
              }}
            >
              {m.charAt(0).toUpperCase() + m.slice(1)}
            </button>
          ))}
        </div>

        {/* Calendars */}
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} style={inputStyle} />
          <span style={{color: '#555'}}>—</span>
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} style={inputStyle} />
        </div>

        {/* Reset */}
        <button onClick={handleReset} style={{...modeBtnStyle, background: '#eb4d4b', color: '#fff'}}>Reset All</button>

        {/* Metrics switcher */}
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '10px' }}>
          <MetricToggle active={visibleMetrics.temp} color="#ff5b7f" label="T" onClick={() => setVisibleMetrics(p => ({...p, temp: !p.temp}))} />
          <MetricToggle active={visibleMetrics.hum} color="#4fa3ff" label="H" onClick={() => setVisibleMetrics(p => ({...p, hum: !p.hum}))} />
          <MetricToggle active={visibleMetrics.co2} color="#ffc94d" label="C" onClick={() => setVisibleMetrics(p => ({...p, co2: !p.co2}))} />
        </div>
      </div>

      {/* GRAPH */}
      <div style={{ background: "#1a1a1a", padding: "20px", borderRadius: "15px", height: '600px', width: '100%', border: '1px solid #333' }}>
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>Loading data...</div>
        ) : (
          <LineChart key={mode} labels={chartData.labels} datasets={chartData.datasets} />
        )}
      </div>
    </div>
  );
}

// Styles
const modeBtnStyle = {
  padding: '8px 16px',
  border: 'none',
  borderRadius: '6px',
  cursor: 'pointer',
  fontSize: '13px',
  transition: '0.2s',
  fontWeight: '500'
};

const inputStyle = {
  background: '#1a1a1a',
  color: '#fff',
  border: '1px solid #444',
  padding: '8px',
  borderRadius: '6px',
  outline: 'none'
};

const MetricToggle = ({ active, color, label, onClick }) => (
  <button 
    onClick={onClick}
    style={{
      width: '35px', height: '35px', borderRadius: '50%', border: `2px solid ${color}`,
      background: active ? color : 'transparent', color: active ? '#fff' : color,
      cursor: 'pointer', fontWeight: 'bold', transition: '0.2s'
    }}
  >
    {label}
  </button>
);

export default AdminPerformance;
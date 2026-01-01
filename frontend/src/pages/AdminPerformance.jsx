import React, { useState, useEffect } from 'react';
import LineChart from "../components/LineChart";

function AdminPerformance() {
  const [chartData, setChartData] = useState({ labels: [], datasets: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSensorData = async () => {
    try {
      // Request to the backend
      const response = await fetch("http://localhost:8000/history");
      if (!response.ok) throw new Error("Failed to load data");
      
      const rawData = await response.json();

      // Formate the data from Chart.js
      const formattedData = {
        // X axes: time from DB formatted to the local time
        labels: rawData.map(item => new Date(item.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })), 
        datasets: [
          {
            label: "Temperature (°C)",
            data: rawData.map(item => item.temperature),
            borderColor: "#ff5b7f",
            backgroundColor: "rgba(255, 91, 127, 0.2)",
            fill: true,
            tension: 0.4,
          },
          {
            label: "Humidity (%)",
            data: rawData.map(item => item.humidity),
            borderColor: "#4fa3ff",
            backgroundColor: "rgba(79, 163, 255, 0.2)",
            fill: true,
            tension: 0.4,
          },
          {
            label: "CO2 (ppm)",
            data: rawData.map(item => item.co2),
            borderColor: "#ffc94d",
            backgroundColor: "rgba(255, 201, 77, 0.2)",
            fill: true,
            tension: 0.4,
          }
        ]
      };

      setChartData(formattedData);
      setLoading(false);
    } catch (err) {
      console.error("Fetch error:", err);
      setError(err.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSensorData();
    // Update every 10 seconds
    const interval = setInterval(fetchSensorData, 10000); 
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="p-6 text-white">Loading metrics...</div>;
  if (error) return <div className="p-6 text-red-500">Error: {error}</div>;

  return (
    <div className="admin-performance-page">
      <h1 className="dashboard-title">Environmental Performance</h1>
      
      <div className="chart-container" style={{ 
        backgroundColor: "#1a1a1a", 
        padding: "25px", 
        borderRadius: "15px",
        marginTop: "20px" 
      }}>
        <LineChart 
          title="Real-time Sensor Monitoring"
          labels={chartData.labels}
          datasets={chartData.datasets}
        />
      </div>

      <div className="stats-grid" style={{ 
        display: "grid", 
        gridTemplateColumns: "repeat(3, 1fr)", 
        gap: "20px", 
        marginTop: "30px" 
      }}>
        <StatCard title="Avg Temp" value={`${calculateAvg(chartData.datasets[0]?.data)}°C`} color="#ff5b7f" />
        <StatCard title="Avg Humidity" value={`${calculateAvg(chartData.datasets[1]?.data)}%`} color="#4fa3ff" />
        <StatCard title="Avg CO2" value={`${calculateAvg(chartData.datasets[2]?.data)} ppm`} color="#ffc94d" />
      </div>
    </div>
  );
}

// Additional component for statcard
const StatCard = ({ title, value, color }) => (
  <div style={{ 
    background: "#252525", 
    padding: "20px", 
    borderRadius: "10px", 
    borderLeft: `4px solid ${color}` 
  }}>
    <h4 style={{ color: "#888", margin: 0 }}>{title}</h4>
    <h2 style={{ color: "#fff", margin: "10px 0 0 0" }}>{value}</h2>
  </div>
);

// Вспомогательная функция для расчета среднего
const calculateAvg = (data) => {
  if (!data || data.length === 0) return 0;
  const sum = data.reduce((a, b) => a + b, 0);
  return (sum / data.length).toFixed(1);
};

export default AdminPerformance;
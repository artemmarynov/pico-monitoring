import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const SensorChart = () => {
  const [data, setData] = useState([]);

  // Loading data from FastAPI
  const fetchData = async () => {
    try {
      const response = await fetch('http://localhost:8000/history');
      const jsonData = await response.json();
      setData(jsonData);
    } catch (error) {
      print("Failed loading data:", error);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ width: '100%', height: 400, background: '#1e1e1e', padding: '20px', borderRadius: '10px' }}>
      <h2 style={{ color: 'white' }}>Sensors monitoring</h2>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
          <XAxis 
            dataKey="time" 
            stroke="#888" 
            tickFormatter={(tick) => new Date(tick).toLocaleTimeString()} 
          />
          <YAxis stroke="#888" />
          <Tooltip contentStyle={{ backgroundColor: '#333', border: 'none' }} />
          <Legend />
          {/* Different readings */}
          <Line type="monotone" dataKey="temperature" stroke="#ff4d4d" name="Temperature" dot={false} />
          <Line type="monotone" dataKey="humidity" stroke="#3399ff" name="Humidity" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SensorChart;
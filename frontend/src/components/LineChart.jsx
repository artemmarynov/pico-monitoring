import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const LineChart = ({ title, labels, datasets }) => {
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#e5e7eb',
          font: { size: 12 }
        }
      },
      title: {
        display: !!title,
        text: title,
        color: '#ffffff',
        font: { size: 16 }
      },
      tooltip: {
        backgroundColor: '#1f2937',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: '#374151',
        borderWidth: 1
      }
    },
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        type: 'linear',
        position: 'left',
        suggestedMin: 15,
        suggestedMax: 30,
        grid: { color: '#2d2d2d' },
        ticks: { color: '#9ca3af' },
        title: { display: true, text: 'Temp / Hum', color: '#9ca3af' }
      },
      y1: {
        type: 'linear',
        position: 'right',
        grid: { drawOnChartArea: false },
        ticks: { color: '#ffc94d' },
        title: { display: true, text: 'CO2 (ppm)', color: '#ffc94d' }
      },
      x: {
        grid: { display: false },
        ticks: { color: '#9ca3af', maxRotation: 45, minRotation: 45 }
      }
    },
    plugins: {
      legend: { display: false }
    }
  };

  const data = {
    labels: labels || [],
    datasets: datasets || []
  };

  return (
    <div style={{ height: '400px', width: '100%' }}>
      <Line options={options} data={data} />
    </div>
  );
};

export default LineChart;
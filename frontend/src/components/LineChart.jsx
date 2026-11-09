import { useMemo } from "react";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend } from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);
const axes = {
  temperature: { position: "left", title: { display: true, text: "Temperature (C)" } },
  humidity: { position: "right", min: 0, max: 100, title: { display: true, text: "Humidity (%)" } },
  co2: { position: "right", title: { display: true, text: "CO2 (ppm)" } },
  lighting: { position: "left", title: { display: true, text: "Lighting (lux)" } },
};

export default function LineChart({ labels = [], datasets = [] }) {
  const options = useMemo(() => ({
    responsive: true, maintainAspectRatio: false, animation: false,
    interaction: { mode: "index", intersect: false },
    plugins: { legend: { labels: { color: "#e5e7eb" } } },
    scales: {
      x: { ticks: { color: "#9ca3af", maxTicksLimit: 12 } },
      ...Object.fromEntries(Object.entries(axes).map(([name, axis]) => [name, {
        ...axis, type: "linear", offset: true,
        display: datasets.some((dataset) => dataset.yAxisID === name),
        grid: { drawOnChartArea: name === "temperature", color: "#2d2d2d" },
        ticks: { color: "#9ca3af" }, title: { ...axis.title, color: "#9ca3af" },
      }])),
    },
  }), [datasets]);
  return <div className="chart-container"><Line options={options} data={{ labels, datasets }}
    datasetIdKey="yAxisID" updateMode="none" /></div>;
}

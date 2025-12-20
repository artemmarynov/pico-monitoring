import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";
import ChartCard from "./ChartCard";

ChartJS.register(
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend
);

function LineChart({ title, labels, datasets }) {
  return (
    <ChartCard title={title}>
      <Line
        data={{ labels, datasets }}
        options={{
          responsive: true,
          maintainAspectRatio: false,
          tension: 0.4,
          plugins: {
            legend: {
              position: "bottom",
            },
          },
          scales: {
            y: {
              beginAtZero: true,
            },
          },
        }}
      />
    </ChartCard>
  );
}

export default LineChart;

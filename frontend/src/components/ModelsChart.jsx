import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { Pie } from "react-chartjs-2";
import ChartCard from "./ChartCard";

ChartJS.register(ArcElement, Tooltip, Legend);

function ModelsChart({ data }) {
  const chartData = {
    labels: data.map((item) => item.label),
    datasets: [
      {
        data: data.map((item) => item.value),
        backgroundColor: data.map((item) => item.color),
        borderWidth: 3,
      },
    ],
  };

  return (
    <ChartCard title="Models">
      <Pie
        data={chartData}
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "top",
            },
          },
        }}
      />
    </ChartCard>
  );
}

export default ModelsChart;

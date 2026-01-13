import React, { useMemo } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Line } from "react-chartjs-2";

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

function isCo2Dataset(ds) {
  const lbl = (ds?.label || "").toLowerCase();
  return lbl.includes("co2") || lbl.includes("co₂");
}

function numericArray(arr) {
  return (arr || [])
    .map((v) => (v === null || v === undefined ? NaN : Number(v)))
    .filter((v) => Number.isFinite(v));
}

function autoRange(values, padRatio = 0.08) {
  const nums = numericArray(values);
  if (nums.length === 0) return { min: undefined, max: undefined };

  let min = Math.min(...nums);
  let max = Math.max(...nums);

  if (min === max) {
    const pad = Math.max(1, Math.abs(min) * padRatio);
    return { min: min - pad, max: max + pad };
  }

  const pad = (max - min) * padRatio;
  return { min: min - pad, max: max + pad };
}

const LineChart = ({ title, labels = [], datasets = [] }) => {
  // Важно: стабильные "id" датасетов (react-chartjs-2 будет понимать, что это те же линии)
  const normalizedDatasets = useMemo(() => {
    return (datasets || []).map((ds) => {
      const co2 = isCo2Dataset(ds);
      return {
        ...ds,
        // это ключ для стабильности
        _id: ds._id || ds.label || Math.random().toString(36),

        yAxisID: co2 ? "y1" : "y",
        pointRadius: ds.pointRadius ?? 2,
        tension: ds.tension ?? 0.3,
      };
    });
  }, [datasets]);

  const tempHumValues = useMemo(() => {
    const arr = [];
    for (const ds of normalizedDatasets) {
      if (ds.yAxisID === "y") arr.push(...(ds.data || []));
    }
    return arr;
  }, [normalizedDatasets]);

  const co2Values = useMemo(() => {
    const arr = [];
    for (const ds of normalizedDatasets) {
      if (ds.yAxisID === "y1") arr.push(...(ds.data || []));
    }
    return arr;
  }, [normalizedDatasets]);

  const yRange = useMemo(() => autoRange(tempHumValues), [tempHumValues]);
  const y1Range = useMemo(() => autoRange(co2Values), [co2Values]);

  const options = useMemo(
    () => ({
      responsive: true,
      maintainAspectRatio: false,

      // ✅ ключевой фикс фликера: отключаем анимации при обновлениях
      animation: false,
      transitions: {
        active: { animation: { duration: 0 } },
        resize: { animation: { duration: 0 } },
        show: { animation: { duration: 0 } },
        hide: { animation: { duration: 0 } },
      },

      // ✅ отключаем hover "подсветку" которая тоже может давать микро-перерисовку
      interaction: { mode: "nearest", intersect: false },
      hover: { animationDuration: 0 },

      plugins: {
        legend: {
          position: "top",
          labels: {
            color: "#e5e7eb",
            font: { size: 12 },
          },
        },
        title: {
          display: !!title,
          text: title,
          color: "#ffffff",
          font: { size: 16 },
        },
        tooltip: {
          backgroundColor: "#1f2937",
          titleColor: "#fff",
          bodyColor: "#fff",
          borderColor: "#374151",
          borderWidth: 1,
        },
      },

      scales: {
        y: {
          type: "linear",
          position: "left",
          grid: { color: "#2d2d2d" },
          ticks: { color: "#9ca3af" },
          title: { display: true, text: "Temp / Hum", color: "#9ca3af" },
          ...(yRange.min !== undefined ? { min: yRange.min } : {}),
          ...(yRange.max !== undefined ? { max: yRange.max } : {}),
        },

        y1: {
          type: "linear",
          position: "right",
          grid: { drawOnChartArea: false },
          ticks: { color: "#f3c74f" },
          title: { display: true, text: "CO₂ (ppm)", color: "#f3c74f" },
          ...(y1Range.min !== undefined ? { min: y1Range.min } : {}),
          ...(y1Range.max !== undefined ? { max: y1Range.max } : {}),
        },

        x: {
          grid: { display: false },
          ticks: { color: "#9ca3af", maxRotation: 45, minRotation: 45 },
        },
      },
    }),
    [title, yRange.min, yRange.max, y1Range.min, y1Range.max]
  );

  const data = useMemo(
    () => ({
      labels,
      datasets: normalizedDatasets,
    }),
    [labels, normalizedDatasets]
  );

  return (
    <div style={{ height: "400px", width: "100%" }}>
      <Line
        options={options}
        data={data}
        // ✅ говорит react-chartjs-2 как идентифицировать datasets
        datasetIdKey="_id"
        // ✅ максимально “тихий” апдейт без анимации
        updateMode="none"
      />
    </div>
  );
};

export default LineChart;
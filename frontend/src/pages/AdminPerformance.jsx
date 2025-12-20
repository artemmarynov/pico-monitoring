import LineChart from "../components/LineChart";

function AdminPerformance() {
  return (
    <>
      <h1 className="dashboard-title">Model performance</h1>

      <LineChart
        title="Performance"
        labels={["February", "March"]}
        datasets={[
          {
            label: "Account A",
            data: [45, 30],
            borderColor: "#ff5b7f",
            backgroundColor: "rgba(255,91,127,0.3)",
            fill: true,
          },
          {
            label: "Account B",
            data: [30, 20],
            borderColor: "#4fa3ff",
            backgroundColor: "rgba(79,163,255,0.3)",
            fill: true,
          },
          {
            label: "Account C",
            data: [15, 55],
            borderColor: "#ffc94d",
            backgroundColor: "rgba(255,201,77,0.3)",
            fill: true,
          },
        ]}
      />
    </>
  );
}

export default AdminPerformance;

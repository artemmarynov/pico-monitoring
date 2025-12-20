import LineChart from "../components/LineChart";

function AdminHome() {
  return (
    <>
      <h1 className="dashboard-title">Website traffic schedule</h1>

      <LineChart
        title="Sessions"
        labels={[
          "Jan 1", "Jan 2", "Jan 3", "Jan 4", "Jan 5", "Jan 6", "Jan 7",
        ]}
        datasets={[
          {
            label: "Sessions",
            data: [18, 22, 27, 19, 30, 15, 48],
            borderColor: "#5bc0c8",
            backgroundColor: "rgba(91,192,200,0.3)",
            fill: true,
            pointRadius: 5,
          },
        ]}
      />
    </>
  );
}

export default AdminHome;

import LineChart from "../components/LineChart";

function AdminMisc() {
  return (
    <>
      <h1 className="dashboard-title">Tickets created / solved</h1>

      <LineChart
        title="Support Tickets"
        labels={["Jan 1", "Jan 2", "Jan 3", "Jan 4", "Jan 5", "Jan 6", "Jan 7"]}
        datasets={[
          {
            label: "Received",
            data: [55, 45, 52, 30, 48, 28, 32],
            borderColor: "#6b6fd8",
            backgroundColor: "rgba(107,111,216,0.3)",
            fill: true,
          },
          {
            label: "Resolved",
            data: [50, 30, 48, 22, 43, 14, 30],
            borderColor: "#5cc7be",
            backgroundColor: "rgba(92,199,190,0.3)",
            fill: true,
          },
        ]}
      />
    </>
  );
}

export default AdminMisc;

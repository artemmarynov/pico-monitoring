import ModelsChart from "../components/ModelsChart";

function AdminModels() {
  const modelsData = [
    {
      label: "Wav 2 vec",
      value: 20,
      color: "#145a7c",
    },
    {
      label: "Wav 3 vec",
      value: 30,
      color: "#f07a34",
    },
    {
      label: "Wav 4 vec",
      value: 50,
      color: "#1b6e22",
    },
  ];

  return (
    <>
      <h1 className="dashboard-title">Usage of models</h1>
      <ModelsChart data={modelsData} />
    </>
  );
}

export default AdminModels;
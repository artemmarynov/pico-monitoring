function ChartCard({ title, children }) {
  return (
    <div className="chart-card">
      <h2 className="chart-title">{title}</h2>
      <div className="chart-wrapper">
        {children}
      </div>
    </div>
  );
}

export default ChartCard;
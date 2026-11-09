import { useSensorStatus } from "../hooks/useSensorStatus";

export default function SensorStatus() {
  const { snapshot, error, age, online } = useSensorStatus();
  const message = error ? "Sensor status unavailable" : !snapshot ? "Checking sensor status..."
    : age === null ? "Waiting for measurements" : online ? "Receiving measurements"
      : "Sensor offline: no recent measurements";
  return <div className={`sensor-status ${error ? "unknown" : online ? "online" : "offline"}`} role="status">
    <strong>{message}</strong>
    {snapshot?.last_received_at && <span>Last measurement: <time dateTime={snapshot.last_received_at}>
      {new Date(snapshot.last_received_at).toLocaleString()}</time> ({Math.floor(age)} s ago)</span>}
    {error && <span>{error}</span>}
  </div>;
}

export function historyPath({ mode = "realtime", startDate = "", endDate = "", limit = 100 }) {
  const query = new URLSearchParams({ limit });
  if (mode !== "realtime") query.set("aggregate", mode);
  // Calendar inputs describe the user's local day; send unambiguous UTC instants.
  if (startDate) query.set("start_date", new Date(`${startDate}T00:00:00`).toISOString());
  if (endDate) query.set("end_date", new Date(`${endDate}T23:59:59.999`).toISOString());
  return `/history?${query}`;
}

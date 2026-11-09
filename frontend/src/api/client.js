export async function request(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    credentials: "omit",
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  const text = await response.text();
  let data;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!response.ok) {
    const detail = data?.detail;
    const message = typeof detail === "string" ? detail : `Request failed (${response.status})`;
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  return data;
}

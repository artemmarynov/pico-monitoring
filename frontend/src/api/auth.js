const API_BASE = "http://13.61.186.202:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include", // important for HttpOnly cookie
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }

  if (!res.ok) {
    const message =
      typeof data === "string"
        ? data
        : (data?.detail || `Request failed: ${res.status}`);
    const err = new Error(message);
    err.status = res.status;
    throw err;
  }

  return data;
}

export function apiLogin(email, password) {
  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function apiLogout() {
  return request("/auth/logout", { method: "POST" });
}

export async function apiMe() {
  try {
    return await request("/auth/me", { method: "GET" }); // { user_id, role }
  } catch (e) {
    if (e.status === 401) return null;
    throw e;
  }
}

export function apiCreateAdmin(email, password) {
  return request("/admin/create", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}
const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const getToken = () => localStorage.getItem("token");
export const setToken = (t) => (t ? localStorage.setItem("token", t) : localStorage.removeItem("token"));

const qs = (o) => {
  const p = new URLSearchParams(Object.entries(o).filter(([, v]) => v !== "" && v != null));
  const s = p.toString();
  return s ? `?${s}` : "";
};

async function request(path, { method = "GET", body, form, raw } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  let payload;
  if (form) payload = new URLSearchParams(form);
  else if (body) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(BASE + path, { method, headers, body: payload });
  } catch {
    throw new Error("Cannot reach the server. Is the backend running?");
  }

  if (res.status === 401 && token && path !== "/auth/login") {
    setToken(null);
    window.location.reload();
  }
  if (!res.ok) {
    let detail = "Request failed";
    try {
      const d = await res.json();
      detail = Array.isArray(d.detail) ? d.detail.map((e) => e.msg).join(", ") : d.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return raw ? res : res.json();
}

export const api = {
  login: (email, password) => request("/auth/login", { method: "POST", form: { username: email, password } }),
  me: () => request("/users/me"),
  users: () => request("/users"),
  createUser: (body) => request("/users", { method: "POST", body }),
  deactivate: (id) => request(`/users/${id}/deactivate`, { method: "PATCH" }),
  departments: () => request("/departments"),
  createDepartment: (name) => request("/departments", { method: "POST", body: { name } }),
  checkIn: () => request("/attendance/check-in", { method: "POST" }),
  checkOut: () => request("/attendance/check-out", { method: "POST" }),
  myAttendance: (params = {}) => request(`/attendance/me${qs(params)}`),
  allAttendance: (params = {}) => request(`/attendance${qs(params)}`),
  daily: (date) => request(`/reports/daily${qs({ date })}`),
  monthly: (month, year) => request(`/reports/monthly${qs({ month, year })}`),
  myMonthly: (month, year) => request(`/reports/me/monthly${qs({ month, year })}`),
  async downloadCsv(month, year) {
    const res = await request(`/reports/export${qs({ month, year })}`, { raw: true });
    const url = URL.createObjectURL(await res.blob());
    const a = document.createElement("a");
    a.href = url;
    a.download = `attendance_${year}_${String(month).padStart(2, "0")}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  },
};

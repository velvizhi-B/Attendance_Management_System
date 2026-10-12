import { useEffect, useState } from "react";
import { api, getToken, setToken } from "./api.js";
import Login from "./pages/Login.jsx";
import EmployeeDashboard from "./pages/EmployeeDashboard.jsx";
import AdminAttendance from "./pages/AdminAttendance.jsx";
import AdminUsers from "./pages/AdminUsers.jsx";
import AdminReports from "./pages/AdminReports.jsx";

const ADMIN_TABS = [
  ["attendance", "Attendance"],
  ["users", "Users"],
  ["reports", "Reports"],
  ["mine", "My attendance"],
];

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!getToken());
  const [tab, setTab] = useState("attendance");

  useEffect(() => {
    if (!getToken()) return;
    api.me().then(setUser).catch(() => setToken(null)).finally(() => setLoading(false));
  }, []);

  const logout = () => { setToken(null); setUser(null); setTab("attendance"); };

  if (loading) return <div className="center muted">Loading…</div>;
  if (!user) return <Login onLogin={setUser} />;

  const isAdmin = user.role === "admin";

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand"><span className="logo small">AMS</span> Attendance Management</div>
        <div className="who">
          <span>{user.full_name} <em className="cap">({user.role})</em></span>
          <button className="btn small" onClick={logout}>Log out</button>
        </div>
      </header>

      {isAdmin && (
        <nav className="tabs">
          {ADMIN_TABS.map(([key, label]) => (
            <button key={key} className={tab === key ? "active" : ""} onClick={() => setTab(key)}>{label}</button>
          ))}
        </nav>
      )}

      <main>
        {!isAdmin && <EmployeeDashboard />}
        {isAdmin && tab === "attendance" && <AdminAttendance />}
        {isAdmin && tab === "users" && <AdminUsers currentUser={user} />}
        {isAdmin && tab === "reports" && <AdminReports />}
        {isAdmin && tab === "mine" && <EmployeeDashboard />}
      </main>
    </div>
  );
}

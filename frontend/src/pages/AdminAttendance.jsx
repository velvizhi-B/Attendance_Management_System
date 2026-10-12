import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";
import { Alert, Empty, StatCard, StatusBadge } from "../components/ui.jsx";
import { fmtHours, fmtTime, todayStr } from "../utils.js";

export default function AdminAttendance() {
  const [date, setDate] = useState(todayStr());
  const [userId, setUserId] = useState("");
  const [users, setUsers] = useState([]);
  const [records, setRecords] = useState([]);
  const [daily, setDaily] = useState(null);
  const [alert, setAlert] = useState(null);

  useEffect(() => { api.users().then(setUsers).catch((e) => setAlert({ type: "error", text: e.message })); }, []);

  const load = useCallback(async () => {
    try {
      const [list, d] = await Promise.all([api.allAttendance({ date, user_id: userId }), api.daily(date)]);
      setRecords(list);
      setDaily(d);
    } catch (err) {
      setAlert({ type: "error", text: err.message });
    }
  }, [date, userId]);

  useEffect(() => { load(); }, [load]);

  const name = (id) => users.find((u) => u.id === id)?.full_name ?? `User ${id}`;

  return (
    <>
      <Alert alert={alert} onClose={() => setAlert(null)} />
      <div className="toolbar">
        <h2>Attendance</h2>
        <div className="filters">
          <input type="date" value={date} max={todayStr()} onChange={(e) => e.target.value && setDate(e.target.value)} />
          <select value={userId} onChange={(e) => setUserId(e.target.value)}>
            <option value="">All employees</option>
            {users.map((u) => <option key={u.id} value={u.id}>{u.full_name}</option>)}
          </select>
        </div>
      </div>

      {daily && (
        <div className="stats">
          <StatCard label="Active users" value={daily.total_users} />
          <StatCard label="Present" value={daily.present} tone="good" />
          <StatCard label="Late" value={daily.late} tone="warn" />
          <StatCard label={date === todayStr() ? "Not checked in" : "Absent"} value={daily.absent} tone="bad" />
        </div>
      )}
      {daily && !daily.is_working_day && <p className="muted">This date is a weekend.</p>}

      <section className="card">
        {records.length === 0 ? <Empty text="No records for the selected filters." /> : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Employee</th><th>Check in</th><th>Check out</th><th>Hours</th><th>Status</th></tr></thead>
              <tbody>
                {records.map((r) => (
                  <tr key={r.id}>
                    <td>{name(r.user_id)}</td>
                    <td>{fmtTime(r.check_in)}</td>
                    <td>{r.check_out ? fmtTime(r.check_out) : r.attendance_date < todayStr() ? "Missing" : "—"}</td>
                    <td>{fmtHours(r.hours_worked)}</td>
                    <td><StatusBadge status={r.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}

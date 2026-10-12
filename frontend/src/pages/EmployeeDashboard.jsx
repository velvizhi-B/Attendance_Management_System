import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";
import { Alert, Empty, StatCard, StatusBadge } from "../components/ui.jsx";
import { fmtDate, fmtHours, fmtTime, monthRange, thisMonth, todayStr } from "../utils.js";

export default function EmployeeDashboard() {
  const [month, setMonth] = useState(thisMonth());
  const [records, setRecords] = useState([]);
  const [summary, setSummary] = useState(null);
  const [today, setToday] = useState(null);
  const [busy, setBusy] = useState(false);
  const [alert, setAlert] = useState(null);

  const load = useCallback(async () => {
    const { y, m, from, to } = monthRange(month);
    try {
      const [history, sum, t] = await Promise.all([
        api.myAttendance({ from_date: from, to_date: to }),
        api.myMonthly(m, y),
        api.myAttendance({ from_date: todayStr(), to_date: todayStr() }),
      ]);
      setRecords(history);
      setSummary(sum);
      setToday(t[0] || null);
    } catch (err) {
      setAlert({ type: "error", text: err.message });
    }
  }, [month]);

  useEffect(() => { load(); }, [load]);

  async function act(fn, okText) {
    setBusy(true);
    setAlert(null);
    try {
      await fn();
      setAlert({ type: "success", text: okText });
      await load();
    } catch (err) {
      setAlert({ type: "error", text: err.message });
    } finally {
      setBusy(false);
    }
  }

  const canCheckIn = !today;
  const canCheckOut = today && !today.check_out;

  return (
    <>
      <Alert alert={alert} onClose={() => setAlert(null)} />

      <section className="card today">
        <div>
          <h2>Today</h2>
          <p className="muted">{fmtDate(todayStr())}</p>
          <div className="times">
            <div><span className="muted">Check in</span><strong>{fmtTime(today?.check_in)}</strong></div>
            <div><span className="muted">Check out</span><strong>{fmtTime(today?.check_out)}</strong></div>
            <div><span className="muted">Status</span>{today ? <StatusBadge status={today.status} /> : <strong>Not checked in</strong>}</div>
          </div>
        </div>
        <div className="actions">
          <button className="btn primary" disabled={!canCheckIn || busy} onClick={() => act(api.checkIn, "Checked in successfully.")}>Check in</button>
          <button className="btn" disabled={!canCheckOut || busy} onClick={() => act(api.checkOut, "Checked out successfully.")}>Check out</button>
        </div>
      </section>

      <div className="toolbar">
        <h2>My attendance</h2>
        <input type="month" value={month} max={thisMonth()} onChange={(e) => e.target.value && setMonth(e.target.value)} />
      </div>

      {summary && (
        <div className="stats">
          <StatCard label="Working days" value={summary.working_days} />
          <StatCard label="Present" value={summary.days_present} tone="good" />
          <StatCard label="Late" value={summary.days_late} tone="warn" />
          <StatCard label="Absent" value={summary.days_absent} tone="bad" />
          <StatCard label="Hours worked" value={summary.total_hours.toFixed(1)} />
        </div>
      )}

      <section className="card">
        {records.length === 0 ? <Empty text="No attendance records for this month." /> : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Date</th><th>Check in</th><th>Check out</th><th>Hours</th><th>Status</th></tr></thead>
              <tbody>
                {records.map((r) => (
                  <tr key={r.id}>
                    <td>{fmtDate(r.attendance_date)}</td>
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

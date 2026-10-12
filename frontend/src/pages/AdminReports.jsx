import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";
import { Alert, Empty } from "../components/ui.jsx";
import { monthRange, thisMonth } from "../utils.js";

export default function AdminReports() {
  const [month, setMonth] = useState(thisMonth());
  const [rows, setRows] = useState([]);
  const [alert, setAlert] = useState(null);
  const [busy, setBusy] = useState(false);
  const { y, m } = monthRange(month);

  const load = useCallback(async () => {
    try {
      setRows(await api.monthly(m, y));
    } catch (err) {
      setAlert({ type: "error", text: err.message });
    }
  }, [m, y]);
  useEffect(() => { load(); }, [load]);

  async function download() {
    setBusy(true);
    try {
      await api.downloadCsv(m, y);
    } catch (err) {
      setAlert({ type: "error", text: err.message });
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Alert alert={alert} onClose={() => setAlert(null)} />
      <div className="toolbar">
        <h2>Monthly report</h2>
        <div className="filters">
          <input type="month" value={month} max={thisMonth()} onChange={(e) => e.target.value && setMonth(e.target.value)} />
          <button className="btn primary" onClick={download} disabled={busy}>{busy ? "Preparing…" : "Download CSV"}</button>
        </div>
      </div>
      <section className="card">
        {rows.length === 0 ? <Empty text="No data for this month." /> : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Employee</th><th>Department</th><th>Working days</th><th>Present</th><th>Late</th><th>Absent</th><th>Hours</th><th>Missing check-outs</th></tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.user_id}>
                    <td>{r.full_name}</td>
                    <td>{r.department ?? "—"}</td>
                    <td>{r.working_days}</td>
                    <td>{r.days_present}</td>
                    <td>{r.days_late}</td>
                    <td>{r.days_absent}</td>
                    <td>{r.total_hours.toFixed(1)}</td>
                    <td>{r.missing_checkouts}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <p className="muted note">Absent = working days (Mon to Fri) since the user joined with no present or late record. Public holidays are not excluded.</p>
      </section>
    </>
  );
}

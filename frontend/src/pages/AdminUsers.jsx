import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";
import { Alert } from "../components/ui.jsx";

const blank = { full_name: "", email: "", password: "", role: "employee", department_id: "" };

export default function AdminUsers({ currentUser }) {
  const [users, setUsers] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [form, setForm] = useState(blank);
  const [deptName, setDeptName] = useState("");
  const [alert, setAlert] = useState(null);

  const load = useCallback(async () => {
    try {
      const [u, d] = await Promise.all([api.users(), api.departments()]);
      setUsers(u);
      setDepartments(d);
    } catch (err) {
      setAlert({ type: "error", text: err.message });
    }
  }, []);
  useEffect(() => { load(); }, [load]);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const deptOf = (id) => departments.find((d) => d.id === id)?.name ?? "—";

  async function run(fn, okText, after) {
    setAlert(null);
    try {
      await fn();
      setAlert({ type: "success", text: okText });
      after?.();
      await load();
    } catch (err) {
      setAlert({ type: "error", text: err.message });
    }
  }

  const addUser = (e) => {
    e.preventDefault();
    run(
      () => api.createUser({ ...form, department_id: form.department_id ? Number(form.department_id) : null }),
      "User created.",
      () => setForm(blank),
    );
  };
  const addDept = (e) => {
    e.preventDefault();
    run(() => api.createDepartment(deptName.trim()), "Department created.", () => setDeptName(""));
  };

  return (
    <>
      <Alert alert={alert} onClose={() => setAlert(null)} />
      <div className="grid-2">
        <form className="card form" onSubmit={addUser}>
          <h2>Add user</h2>
          <label>Full name<input value={form.full_name} onChange={set("full_name")} required minLength={2} /></label>
          <label>Email<input type="email" value={form.email} onChange={set("email")} required /></label>
          <label>Password (min 8 characters)<input type="password" value={form.password} onChange={set("password")} required minLength={8} maxLength={72} /></label>
          <div className="row">
            <label>Role
              <select value={form.role} onChange={set("role")}>
                <option value="employee">Employee</option>
                <option value="admin">Admin</option>
              </select>
            </label>
            <label>Department
              <select value={form.department_id} onChange={set("department_id")}>
                <option value="">None</option>
                {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
              </select>
            </label>
          </div>
          <button className="btn primary">Create user</button>
        </form>

        <form className="card form" onSubmit={addDept}>
          <h2>Add department</h2>
          <label>Name<input value={deptName} onChange={(e) => setDeptName(e.target.value)} required minLength={2} /></label>
          <button className="btn primary">Create department</button>
          <p className="muted">Departments: {departments.length ? departments.map((d) => d.name).join(", ") : "none yet"}</p>
        </form>
      </div>

      <section className="card">
        <h2>Users</h2>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Department</th><th>Status</th><th></th></tr></thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.full_name}</td>
                  <td>{u.email}</td>
                  <td className="cap">{u.role}</td>
                  <td>{deptOf(u.department_id)}</td>
                  <td><span className={`badge ${u.is_active ? "present" : "absent"}`}>{u.is_active ? "active" : "inactive"}</span></td>
                  <td>
                    {u.is_active && u.id !== currentUser.id && (
                      <button className="btn small danger" onClick={() => window.confirm(`Deactivate ${u.full_name}?`) && run(() => api.deactivate(u.id), "User deactivated.")}>Deactivate</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

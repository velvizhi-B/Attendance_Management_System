const pad = (n) => String(n).padStart(2, "0");

export const todayStr = () => {
  const d = new Date();
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
};
export const thisMonth = () => todayStr().slice(0, 7);

export const monthRange = (month) => {
  const [y, m] = month.split("-").map(Number);
  return { y, m, from: `${month}-01`, to: `${month}-${pad(new Date(y, m, 0).getDate())}` };
};

export const fmtTime = (s) => (s ? s.slice(11, 16) : "—");
export const fmtDate = (s) =>
  new Date(s + "T00:00:00").toLocaleDateString("en-IN", { weekday: "short", day: "2-digit", month: "short", year: "numeric" });
export const fmtHours = (h) => (h == null ? "—" : `${h.toFixed(2)} h`);

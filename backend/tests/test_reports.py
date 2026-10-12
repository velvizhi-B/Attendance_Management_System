"""Report tests with fixed September 2026 data (22 working days).

Run from the backend folder:
    DATABASE_URL=sqlite:///./test_reports.db python seed.py
    DATABASE_URL=sqlite:///./test_reports.db PYTHONPATH=. python tests/test_reports.py
"""
from datetime import date, datetime

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database import SessionLocal
from app.main import app
from app.models import Attendance, User

c = TestClient(app)


def token(email, pw):
    return {"Authorization": "Bearer " + c.post("/auth/login", data={"username": email, "password": pw}).json()["access_token"]}


ah = token("admin@example.com", "Admin@1234")
eh = token("employee@example.com", "Employee@1234")


def rec(user_id, day, cin, cout, status):
    return Attendance(
        user_id=user_id, attendance_date=day, status=status,
        check_in=datetime.combine(day, cin) if cin else None,
        check_out=datetime.combine(day, cout) if cout else None,
    )


from datetime import time as t

with SessionLocal() as db:
    emp = db.scalar(select(User).where(User.email == "employee@example.com"))
    emp.created_at = datetime(2026, 8, 1)
    db.query(Attendance).delete()
    db.add_all([
        rec(emp.id, date(2026, 9, 1), t(9, 0), t(17, 0), "present"),
        rec(emp.id, date(2026, 9, 2), t(9, 0), t(17, 0), "present"),
        rec(emp.id, date(2026, 9, 3), t(9, 0), t(17, 0), "present"),
        rec(emp.id, date(2026, 9, 4), t(10, 0), t(19, 0), "late"),
        rec(emp.id, date(2026, 9, 7), t(9, 0), None, "present"),  # forgot to check out
    ])
    db.commit()
    emp_id = emp.id

# Monthly summary
rows = c.get("/reports/monthly?month=9&year=2026", headers=ah).json()
e = next(r for r in rows if r["user_id"] == emp_id)
assert e["working_days"] == 22, e
assert (e["days_present"], e["days_late"], e["days_absent"]) == (4, 1, 17), e
assert e["total_hours"] == 33.0, e
assert e["missing_checkouts"] == 1, e
a = next(r for r in rows if r["full_name"] == "Admin User")
assert a["working_days"] == 0 and a["days_absent"] == 0, a  # joined after September
print("monthly summary ok:", e)

# Own summary matches, and employees cannot see the admin report
assert c.get("/reports/me/monthly?month=9&year=2026", headers=eh).json()["days_absent"] == 17
assert c.get("/reports/monthly?month=9&year=2026", headers=eh).status_code == 403
assert c.get("/reports/monthly?month=13&year=2026", headers=ah).status_code == 422
assert c.get("/reports/monthly?month=9&year=2026").status_code == 401
print("access control and validation ok")

# Daily summary
d = c.get("/reports/daily?date=2026-09-04", headers=ah).json()
assert (d["present"], d["late"], d["absent"]) == (0, 1, 0), d
d = c.get("/reports/daily?date=2026-09-08", headers=ah).json()
assert d["absent"] == 1 and d["is_working_day"], d
d = c.get("/reports/daily?date=2026-09-06", headers=ah).json()  # Sunday
assert d["absent"] == 0 and not d["is_working_day"], d
print("daily summary ok")

# CSV export
r = c.get("/reports/export?month=9&year=2026", headers=ah)
assert r.status_code == 200 and r.headers["content-type"].startswith("text/csv")
assert "attendance_2026_09.csv" in r.headers["content-disposition"]
lines = r.text.strip().splitlines()
assert lines[0] == "Date,Employee,Email,Department,Check In,Check Out,Hours Worked,Status"
assert len(lines) == 6, lines
assert "2026-09-04,Test Employee,employee@example.com,Engineering,10:00:00,19:00:00,9.0,late" in lines[4]
assert c.get("/reports/export?month=9&year=2026", headers=eh).status_code == 403
print("csv export ok")

# Formula injection is neutralised
with SessionLocal() as db:
    emp = db.get(User, emp_id)
    emp.full_name = "=HYPERLINK(\"http://x\")"
    db.commit()
r = c.get(f"/reports/export?month=9&year=2026&user_id={emp_id}", headers=ah)
assert "'=HYPERLINK" in r.text and ",=HYPERLINK" not in r.text
print("csv injection protection ok")
print("ALL REPORT TESTS PASSED")

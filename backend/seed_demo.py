"""Fill the database with sample employees and recent attendance for demos.

Run after seed.py, from the backend folder:  python seed_demo.py
Safe to run again: it skips anything that already exists.
FOR DEMO ONLY: do not run against real data.
"""
import random
from datetime import date, datetime, time, timedelta

from sqlalchemy import select

from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Attendance, Department, User
from app.routers.attendance import now_local

Base.metadata.create_all(bind=engine)

PEOPLE = [
    ("Priya Nair", "priya@example.com", "Engineering"),
    ("Arun Kumar", "arun@example.com", "Engineering"),
    ("Meena Raj", "meena@example.com", "HR"),
    ("Karthik S", "karthik@example.com", "Sales"),
    ("Divya Lakshmi", "divya@example.com", "Sales"),
]

today = now_local().date()
joined = datetime.combine(today - timedelta(days=45), time(9, 0))

with SessionLocal() as db:
    depts = {}
    for name in ("Engineering", "HR", "Sales"):
        d = db.scalar(select(Department).where(Department.name == name)) or Department(name=name)
        db.add(d)
        db.flush()
        depts[name] = d

    users = []
    for full_name, email, dept in PEOPLE:
        u = db.scalar(select(User).where(User.email == email))
        if not u:
            u = User(full_name=full_name, email=email, password_hash=hash_password("Employee@1234"),
                     role="employee", department_id=depts[dept].id, created_at=joined)
            db.add(u)
            db.flush()
        users.append(u)

    # Make the seeded test employee look like a regular member too
    test_emp = db.scalar(select(User).where(User.email == "employee@example.com"))
    if test_emp:
        test_emp.created_at = joined
        users.append(test_emp)

    added = 0
    for offset in range(30, 0, -1):          # past 30 days, today left empty so you can check in live
        day = today - timedelta(days=offset)
        if day.weekday() >= 5:
            continue
        for u in users:
            if db.scalar(select(Attendance).where(Attendance.user_id == u.id, Attendance.attendance_date == day)):
                continue
            rng = random.Random(f"{u.email}-{day}")   # same outcome for a given person and day, every run
            roll = rng.random()
            if roll < 0.08:                   # absent: no record
                continue
            late = roll > 0.8
            start = time(9, rng.randint(46, 59)) if late else time(9, rng.randint(0, 20))
            end = time(rng.randint(17, 18), rng.randint(0, 59))
            forgot = day != today - timedelta(days=1) and rng.random() < 0.04
            db.add(Attendance(
                user_id=u.id, attendance_date=day, status="late" if late else "present",
                check_in=datetime.combine(day, start),
                check_out=None if forgot else datetime.combine(day, end),
            ))
            added += 1
    db.commit()

print(f"Demo data ready: {len(users)} employees, {added} new attendance records.")
print("All demo employees use the password Employee@1234")

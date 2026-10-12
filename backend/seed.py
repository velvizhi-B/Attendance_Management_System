"""Create a department, one admin, and one employee for testing.

Run from the backend folder:  python seed.py
"""
from sqlalchemy import select

from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Department, User

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    dept = db.scalar(select(Department).where(Department.name == "Engineering"))
    if not dept:
        dept = Department(name="Engineering")
        db.add(dept)
        db.flush()

    for full_name, email, password, role in [
        ("Admin User", "admin@example.com", "Admin@1234", "admin"),
        ("Test Employee", "employee@example.com", "Employee@1234", "employee"),
    ]:
        if not db.scalar(select(User).where(User.email == email)):
            db.add(User(full_name=full_name, email=email, password_hash=hash_password(password),
                        role=role, department_id=dept.id))
    db.commit()

print("Seed complete.")
print("Admin:    admin@example.com / Admin@1234")
print("Employee: employee@example.com / Employee@1234")

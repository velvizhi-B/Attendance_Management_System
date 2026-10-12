# Attendance Management System

A role-based web application for recording and reporting employee attendance.

**Stack:** React.js, FastAPI, PostgreSQL, JWT authentication, Git.

## Features

- Admin and Employee roles with secure login
- Employee check-in and check-out, once per day, with hours worked
- Late detection based on a configurable work start time
- Admin user and department management
- Admin view of all attendance, filtered by date or employee
- Daily and monthly summaries (present, late, absent, hours worked, missing check-outs)
- CSV export of monthly attendance, protected against spreadsheet formula injection
- Interactive API documentation (Swagger UI)

## Run the backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows   (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env         # then edit DATABASE_URL and SECRET_KEY
```

Create the database in PostgreSQL:

```sql
CREATE DATABASE attendance_db;
```

Then create the tables (or let the app create them on first start) and seed test users:

```bash
python seed.py
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for Swagger UI.

Test accounts after seeding:

| Role | Email | Password |
|---|---|---|
| Admin | admin@example.com | Admin@1234 |
| Employee | employee@example.com | Employee@1234 |

Change these passwords before any real use.

In Swagger, click **Authorize**, enter the email as `username` and the password, then try the endpoints.

## API overview

| Method | Endpoint | Access |
|---|---|---|
| POST | /auth/login | Public |
| GET | /users/me | Any user |
| POST, GET | /users | Admin |
| PATCH | /users/{id}/deactivate | Admin |
| POST, GET | /departments | Admin (create), any user (list) |
| POST | /attendance/check-in | Any user |
| POST | /attendance/check-out | Any user |
| GET | /attendance/me | Any user |
| GET | /attendance?date=&user_id= | Admin |
| GET | /reports/daily?date= | Admin |
| GET | /reports/monthly?month=&year= | Admin |
| GET | /reports/me/monthly?month=&year= | Any user |
| GET | /reports/export?month=&year=&user_id= | Admin (CSV download) |

Absent days are working days (Monday to Friday) from the user's join date up to today with no
present or late record. Public holidays are not excluded yet.

## Run the frontend

```bash
cd frontend
npm install
copy .env.example .env     # Linux/Mac: cp .env.example .env
npm run dev
```

Open http://localhost:5173 (the backend must be running on port 8000).

- **Employee:** check in and out, monthly summary, attendance history
- **Admin:** daily attendance with filters, user and department management, monthly report with CSV download, own attendance

## Demo data

After `python seed.py`, run `python seed_demo.py` to add five sample employees with 30 days of attendance.
See `docs/DEMO_GUIDE.md` for the demo flow and likely questions.

## Run the tests

```bash
cd backend
set DATABASE_URL=sqlite:///./test.db            # Windows (Linux/Mac: export DATABASE_URL=...)
python seed.py
set PYTHONPATH=.
python tests/test_flow.py
python tests/test_reports.py
```

## Known limitations

- Public holidays are not excluded from working days
- Single time zone for all users
- No password reset or change-password screen yet

## Project structure

```
backend/   FastAPI app (routers, models, schemas, security)
frontend/  React app (Vite): login, employee and admin dashboards
database/  schema.sql
docs/      demo guide, SRS, diagrams, screenshots
```

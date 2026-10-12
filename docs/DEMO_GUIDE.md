# Demo Guide

## Setup (do this before the session)

1. Start PostgreSQL and confirm `backend/.env` points to `attendance_db`.
2. In `backend`: `python seed.py`, then `python seed_demo.py` (sample employees and 30 days of history), then `uvicorn app.main:app --reload`.
3. In `frontend`: `npm run dev`.
4. Open three browser tabs: the app (http://localhost:5173), Swagger (http://localhost:8000/docs), and the GitHub repo.
5. Log in once as admin and once as an employee in a private window, so you can switch without typing.
6. Close notifications and extra tabs. Keep the SRS PDF and diagrams open in another window.

Accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@example.com | Admin@1234 |
| Employee | priya@example.com | Employee@1234 |

## Live demo flow (about 5 minutes)

| Step | Action | Say |
|---|---|---|
| 1 | Swagger `/docs`: expand `POST /attendance/check-in` | "The API is documented automatically. Every endpoint can be tested here." |
| 2 | Employee window: log in, click Check in | "The time comes from the server, so it cannot be changed from the browser." |
| 3 | Click Check in again | "A second check-in is rejected. The database also enforces one record per user per day." |
| 4 | Click Check out, point at hours and the monthly cards | "Hours worked and late status are calculated automatically." |
| 5 | Admin window: Attendance tab, change date and employee filter | "The admin sees everyone, filtered by date or employee." |
| 6 | Users tab: create a user, then try to open the Users tab as an employee | "Role checks happen on the server, not only in the interface." |
| 7 | Reports tab: pick last month, click Download CSV, open the file | "Reports export straight to Excel." |
| 8 | GitHub: show folders and commit history | "Backend, frontend, database, and docs are separated." |

## If something breaks

- **App will not load:** show Swagger and run the same flow there.
- **Database error:** show `schema.sql`, the ER diagram, and the passing test output (`python tests/test_flow.py`).
- **No internet or Teams share issue:** have screenshots in `docs/screenshots` ready to present.

## Likely questions

| Question | Answer |
|---|---|
| Why FastAPI and PostgreSQL? | Fast to build, automatic validation and API docs, and PostgreSQL enforces constraints. |
| How is the password protected? | Hashed with bcrypt. Login returns a signed JWT with an expiry. |
| How do you prevent duplicate attendance? | An API check plus a unique constraint on user and date. |
| What if someone forgets to check out? | The record stays open and appears in the report as a missing check-out. |
| Can an employee see others' data? | No. Admin endpoints return 403 for employees. |
| What are the limitations? | Public holidays are counted as working days, one time zone only, and no password reset yet. |
| What would you build next? | Leave management, holiday calendar, QR or location check-in, email notifications, Docker deployment. |

## Screenshots to capture for the documentation

Save these in `docs/screenshots`: `login.png`, `employee-dashboard.png`, `admin-attendance.png`, `admin-reports.png`.

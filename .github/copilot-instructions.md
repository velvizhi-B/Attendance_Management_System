# Project context

Attendance Management System. Backend: FastAPI + SQLAlchemy + PostgreSQL (backend/). Frontend: React + Vite (frontend/).
Roles: admin and employee, JWT auth. Read README.md and docs/DEMO_GUIDE.md first.

## Commands
- Backend run: cd backend && source venv/bin/activate && uvicorn app.main:app --reload   (API docs: http://localhost:8000/docs)
- Frontend run: cd frontend && npm run dev   (http://localhost:5173)
- Frontend check: cd frontend && npm run build
- Backend tests (each on a fresh SQLite file):
  cd backend && rm -f test.db && DATABASE_URL=sqlite:///./test.db python seed.py && DATABASE_URL=sqlite:///./test.db PYTHONPATH=. python tests/test_flow.py
  cd backend && rm -f test.db && DATABASE_URL=sqlite:///./test.db python seed.py && DATABASE_URL=sqlite:///./test.db PYTHONPATH=. python tests/test_reports.py

## Rules
- Work on the dev branch. Make small commits with messages like "fix: ..." or "feat: ...". Never commit .env, venv, node_modules or *.db.
- Keep attendance time taken from the server, the UNIQUE (user_id, attendance_date) constraint, role checks on the server, and CSV formula-injection protection.
- Fix the root cause of a bug. After every change, run the tests and the frontend build. Add a test for each bug fixed.
- Public holidays, password reset and time zones per user are known limitations, not bugs.

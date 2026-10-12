from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (registers tables)
from app.database import Base, engine
from app.routers import attendance, auth, reports, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Attendance Management System API",
    description="Role-based attendance tracking with check-in, check-out, and admin reporting.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(attendance.router)
app.include_router(reports.router)


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "service": "attendance-management-system"}

import calendar
import csv
import io
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_admin
from app.models import Attendance, User
from app.routers.attendance import now_local
from app.schemas import DailySummary, MonthlySummary

router = APIRouter(prefix="/reports", tags=["Reports"])

Month = Query(..., ge=1, le=12)
Year = Query(..., ge=2000, le=2100)


def working_days(start: date, end: date) -> set[date]:
    """Monday to Friday dates between start and end (inclusive)."""
    days, current = set(), start
    while current <= end:
        if current.weekday() < 5:
            days.add(current)
        current += timedelta(days=1)
    return days


def month_bounds(year: int, month: int) -> tuple[date, date]:
    return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])


def joined_date(user: User) -> date | None:
    return user.created_at.date() if user.created_at else None


def summarise(user: User, records: list[Attendance], year: int, month: int, today: date) -> MonthlySummary:
    first, last = month_bounds(year, month)
    start = max(first, joined_date(user) or first)
    end = min(last, today)
    expected = working_days(start, end) if start <= end else set()

    attended = {r.attendance_date for r in records if r.status in ("present", "late")}
    hours = sum(
        (r.check_out - r.check_in).total_seconds() / 3600
        for r in records if r.check_in and r.check_out
    )
    return MonthlySummary(
        user_id=user.id,
        full_name=user.full_name,
        department=user.department.name if user.department else None,
        month=month,
        year=year,
        working_days=len(expected),
        days_present=sum(1 for r in records if r.status == "present"),
        days_late=sum(1 for r in records if r.status == "late"),
        days_absent=len(expected - attended),
        total_hours=round(hours, 2),
        missing_checkouts=sum(
            1 for r in records if r.check_in and not r.check_out and r.attendance_date < today
        ),
    )


def month_records(db: Session, year: int, month: int) -> list[Attendance]:
    first, last = month_bounds(year, month)
    return list(db.scalars(
        select(Attendance).where(Attendance.attendance_date >= first, Attendance.attendance_date <= last)
    ).all())


@router.get("/daily", response_model=DailySummary)
def daily_summary(
    on_date: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Counts for one day across active users.

    For today, `absent` means "not checked in yet".
    """
    is_working = on_date.weekday() < 5
    users = [u for u in db.scalars(select(User).where(User.is_active.is_(True))).all()
             if (joined_date(u) or on_date) <= on_date]
    records = {r.user_id: r for r in db.scalars(
        select(Attendance).where(Attendance.attendance_date == on_date)
    ).all()}

    present = sum(1 for u in users if u.id in records and records[u.id].status == "present")
    late = sum(1 for u in users if u.id in records and records[u.id].status == "late")
    absent = sum(1 for u in users if u.id not in records) if is_working else 0
    return DailySummary(
        date=on_date, is_working_day=is_working, total_users=len(users),
        present=present, late=late, absent=absent,
    )


@router.get("/monthly", response_model=list[MonthlySummary])
def monthly_summary(
    month: int = Month,
    year: int = Year,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Per-user monthly summary for all active users.

    Absent days are working days (Mon to Fri) from the user's join date up to today
    with no present or late record. Public holidays are not excluded.
    """
    today = now_local().date()
    records = month_records(db, year, month)
    users = db.scalars(select(User).where(User.is_active.is_(True)).order_by(User.full_name)).all()
    return [summarise(u, [r for r in records if r.user_id == u.id], year, month, today) for u in users]


@router.get("/me/monthly", response_model=MonthlySummary)
def my_monthly_summary(
    month: int = Month,
    year: int = Year,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    today = now_local().date()
    records = [r for r in month_records(db, year, month) if r.user_id == user.id]
    return summarise(user, records, year, month, today)


def safe_cell(value) -> str:
    """Prevent spreadsheet formula injection when the CSV is opened in Excel."""
    text = "" if value is None else str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


@router.get("/export")
def export_csv(
    month: int = Month,
    year: int = Year,
    user_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Download attendance records for a month as CSV (optionally for one user)."""
    first, last = month_bounds(year, month)
    query = (
        select(Attendance, User)
        .join(User, User.id == Attendance.user_id)
        .where(Attendance.attendance_date >= first, Attendance.attendance_date <= last)
        .order_by(Attendance.attendance_date, User.full_name)
    )
    if user_id:
        query = query.where(Attendance.user_id == user_id)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Date", "Employee", "Email", "Department", "Check In", "Check Out", "Hours Worked", "Status"])
    for record, user in db.execute(query).all():
        hours = (
            round((record.check_out - record.check_in).total_seconds() / 3600, 2)
            if record.check_in and record.check_out else ""
        )
        writer.writerow([
            record.attendance_date.isoformat(),
            safe_cell(user.full_name),
            safe_cell(user.email),
            safe_cell(user.department.name if user.department else ""),
            record.check_in.strftime("%H:%M:%S") if record.check_in else "",
            record.check_out.strftime("%H:%M:%S") if record.check_out else "",
            hours,
            record.status,
        ])

    filename = f"attendance_{year}_{month:02d}.csv"
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

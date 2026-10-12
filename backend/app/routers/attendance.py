from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import config
from app.database import get_db
from app.deps import get_current_user, require_admin
from app.models import Attendance, User
from app.schemas import AttendanceOut

router = APIRouter(prefix="/attendance", tags=["Attendance"])


def now_local() -> datetime:
    """Server time in the configured time zone, stored as a naive datetime."""
    return datetime.now(ZoneInfo(config.TIMEZONE)).replace(tzinfo=None, microsecond=0)


def late_cutoff(day: date) -> datetime:
    hour, minute = map(int, config.WORK_START.split(":"))
    return datetime.combine(day, time(hour, minute)) + timedelta(minutes=config.LATE_GRACE_MINUTES)


def to_out(record: Attendance) -> AttendanceOut:
    out = AttendanceOut.model_validate(record)
    if record.check_in and record.check_out:
        out.hours_worked = round((record.check_out - record.check_in).total_seconds() / 3600, 2)
    return out


@router.post("/check-in", response_model=AttendanceOut, status_code=201)
def check_in(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    now = now_local()
    today = now.date()
    existing = db.scalar(
        select(Attendance).where(Attendance.user_id == user.id, Attendance.attendance_date == today)
    )
    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You have already checked in today")

    record = Attendance(
        user_id=user.id,
        attendance_date=today,
        check_in=now,
        status="late" if now > late_cutoff(today) else "present",
    )
    db.add(record)
    try:
        db.commit()
    except IntegrityError:  # two simultaneous requests: the database constraint wins
        db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You have already checked in today")
    db.refresh(record)
    return to_out(record)


@router.post("/check-out", response_model=AttendanceOut)
def check_out(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    now = now_local()
    record = db.scalar(
        select(Attendance).where(Attendance.user_id == user.id, Attendance.attendance_date == now.date())
    )
    if record is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You have not checked in today")
    if record.check_out is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You have already checked out today")

    record.check_out = now
    db.commit()
    db.refresh(record)
    return to_out(record)


@router.get("/me", response_model=list[AttendanceOut])
def my_attendance(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(Attendance).where(Attendance.user_id == user.id)
    if from_date:
        query = query.where(Attendance.attendance_date >= from_date)
    if to_date:
        query = query.where(Attendance.attendance_date <= to_date)
    records = db.scalars(query.order_by(Attendance.attendance_date.desc())).all()
    return [to_out(r) for r in records]


@router.get("", response_model=list[AttendanceOut])
def all_attendance(
    on_date: date | None = Query(None, alias="date"),
    user_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = select(Attendance)
    if on_date:
        query = query.where(Attendance.attendance_date == on_date)
    if user_id:
        query = query.where(Attendance.user_id == user_id)
    records = db.scalars(query.order_by(Attendance.attendance_date.desc(), Attendance.user_id)).all()
    return [to_out(r) for r in records]

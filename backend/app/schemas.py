from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    role: Literal["admin", "employee"] = "employee"
    department_id: int | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: EmailStr
    role: str
    department_id: int | None
    is_active: bool


class AttendanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    attendance_date: date
    check_in: datetime | None
    check_out: datetime | None
    status: str
    hours_worked: float | None = None


class MonthlySummary(BaseModel):
    user_id: int
    full_name: str
    department: str | None
    month: int
    year: int
    working_days: int
    days_present: int
    days_late: int
    days_absent: int
    total_hours: float
    missing_checkouts: int


class DailySummary(BaseModel):
    date: date
    is_working_day: bool
    total_users: int
    present: int
    late: int
    absent: int

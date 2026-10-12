import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
WORK_START = os.getenv("WORK_START", "09:30")
LATE_GRACE_MINUTES = int(os.getenv("LATE_GRACE_MINUTES", "15"))

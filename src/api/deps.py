"""
FastAPI 의존성 주입 모듈
"""

from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from src.core.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

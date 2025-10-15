"""
DB 엔진/세션/초기화 유틸리티
"""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite 기본값. 필요 시 .env로 덮어쓰기: DATABASE_URL=sqlite:///./app.db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# SQLite에서 다중 스레드 사용 허용
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """앱 시작 시 테이블 자동 생성"""
    from .models import Base  # noqa: WPS433 (지연 임포트로 순환 참조 방지)

    Base.metadata.create_all(bind=engine)




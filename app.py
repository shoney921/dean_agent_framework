"""
FastAPI 애플리케이션 메인 파일
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import subprocess
import sys
import atexit
from pathlib import Path

from src.api.v1.api import api_router
from src.core.db import init_db, get_db
from src.repositories.notion_batch_status import upsert_status
from datetime import datetime

# 데이터베이스 초기화
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시 실행
    init_db()
    
    # 배치 상태를 idle로 초기화
    try:
        db = next(get_db())
        from src.core.models import NotionBatchStatus
        
        # 모든 배치 상태를 idle로 초기화
        batch_statuses = db.query(NotionBatchStatus).all()
        for status in batch_statuses:
            status.status = "idle"
            status.message = "애플리케이션 시작으로 인한 초기화"
            status.updated_at = datetime.utcnow()
        
        db.commit()
        print(f"✅ {len(batch_statuses)}개의 배치 상태가 'idle'로 초기화되었습니다.")
    except Exception as e:
        print(f"⚠️ 배치 상태 초기화 중 오류: {e}")
    finally:
        db.close()
    
    yield
    # 종료 시 실행 (필요시)
    pass

# FastAPI 애플리케이션 생성 (수정)
app = FastAPI(
    title="Dean Framework API",
    description="AI 에이전트 시스템을 위한 백엔드 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix="/api/v1")

# 루트 엔드포인트
@app.get("/", summary="API 상태 확인")
async def root():
    """API 상태를 확인합니다."""
    return {
        "message": "Dean Framework API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

# 헬스 체크 엔드포인트
@app.get("/health", summary="헬스 체크")
async def health_check():
    """서비스 상태를 확인합니다."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn

    # ---------------------------------------------------------------
    # Streamlit 프론트엔드 백그라운드 실행
    # ---------------------------------------------------------------
    project_root = Path(__file__).resolve().parent
    streamlit_app_path = project_root / "frontend" / "streamlit_app" / "app.py"

    # 백엔드 베이스 URL을 프론트에 주입
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1/agent-logs")
    env = os.environ.copy()
    env["API_BASE_URL"] = api_base_url

    streamlit_port = os.getenv("STREAMLIT_PORT", "8501")
    streamlit_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(streamlit_app_path),
        "--server.port",
        str(streamlit_port),
        "--server.headless",
        "true",
        "--server.runOnSave",
        "true",  # 파일 저장 시 자동 실행
        "--server.fileWatcherType",
        "auto",  # 파일 감지 방식 자동 설정
        "--browser.gatherUsageStats",
        "false",  # 사용 통계 수집 비활성화
        "--logger.level",
        "info",  # 로그 레벨 설정
    ]

    try:
        streamlit_proc = subprocess.Popen(streamlit_cmd, env=env)
    except FileNotFoundError:
        streamlit_proc = None

    def _cleanup() -> None:
        if streamlit_proc and streamlit_proc.poll() is None:
            try:
                streamlit_proc.terminate()
            except Exception:
                pass

    atexit.register(_cleanup)

    # ---------------------------------------------------------------
    # Uvicorn 백엔드 실행 (블로킹)
    # ---------------------------------------------------------------
    uvicorn.run(
        "app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
        log_level="info",
    )

"""
FastAPI 애플리케이션 메인 파일
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.api import api_router
from src.core.db import init_db

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="Dean Framework API",
    description="AI 에이전트 시스템을 위한 백엔드 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 초기화
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    init_db()

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
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

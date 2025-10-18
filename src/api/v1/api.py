"""
API v1 라우터 설정
"""

from fastapi import APIRouter

from src.api.v1.endpoints import agent_logs, notion

api_router = APIRouter()

# 에이전트 로그 관련 엔드포인트 등록
api_router.include_router(
    agent_logs.router,
    prefix="/agent-logs",
    tags=["agent-logs"]
)

# Notion 관련 엔드포인트 등록
api_router.include_router(
    notion.router,
    prefix="/notion",
    tags=["notion"]
)

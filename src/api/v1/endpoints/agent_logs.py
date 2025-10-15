"""
에이전트 로그 API 엔드포인트
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.core import schemas
from src.services.agent_log_service import AgentLogService

router = APIRouter()


def get_agent_log_service(db: Session = Depends(get_db)) -> AgentLogService:
    """에이전트 로그 서비스 의존성"""
    return AgentLogService(db)


# ============================================================================
# AgentRun 관련 엔드포인트
# ============================================================================

@router.post("/runs", response_model=schemas.AgentRunRead, summary="새로운 에이전트 실행 기록 생성")
async def create_run(
    run_data: schemas.AgentRunCreate,
    service: AgentLogService = Depends(get_agent_log_service)
):
    """새로운 에이전트 실행 기록을 생성합니다."""
    return service.create_run(run_data)


@router.get("/runs", response_model=List[schemas.AgentRunRead], summary="에이전트 실행 기록 목록 조회")
async def list_runs(
    team_name: Optional[str] = Query(None, description="팀 이름으로 필터링"),
    limit: int = Query(50, ge=1, le=1000, description="조회할 최대 개수"),
    service: AgentLogService = Depends(get_agent_log_service)
):
    """에이전트 실행 기록 목록을 조회합니다."""
    return service.list_runs(team_name=team_name, limit=limit)


@router.get("/runs/{run_id}", response_model=schemas.AgentRunRead, summary="특정 실행 기록 조회")
async def get_run(
    run_id: int,
    service: AgentLogService = Depends(get_agent_log_service)
):
    """특정 실행 기록을 조회합니다 (메시지 포함)."""
    run = service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="실행 기록을 찾을 수 없습니다")
    return run


@router.patch("/runs/{run_id}/finish", response_model=schemas.AgentRunRead, summary="실행 기록 완료 처리")
async def finish_run(
    run_id: int,
    status: str = Query("completed", description="완료 상태"),
    service: AgentLogService = Depends(get_agent_log_service)
):
    """실행 기록을 완료 상태로 변경합니다."""
    run = service.finish_run(run_id, status)
    if not run:
        raise HTTPException(status_code=404, detail="실행 기록을 찾을 수 없습니다")
    return run


# ============================================================================
# AgentMessage 관련 엔드포인트
# ============================================================================

@router.post("/messages", response_model=schemas.AgentMessageRead, summary="새로운 메시지 추가")
async def add_message(
    message_data: schemas.AgentMessageCreate,
    service: AgentLogService = Depends(get_agent_log_service)
):
    """새로운 메시지를 추가합니다."""
    return service.add_message(message_data)


@router.get("/runs/{run_id}/messages", response_model=List[schemas.AgentMessageRead], summary="실행 기록의 메시지 목록 조회")
async def get_messages_by_run(
    run_id: int,
    service: AgentLogService = Depends(get_agent_log_service)
):
    """특정 실행 기록의 모든 메시지를 조회합니다."""
    return service.get_messages_by_run(run_id)


# ============================================================================
# 통계 및 분석 엔드포인트
# ============================================================================

@router.get("/teams/{team_name}/statistics", summary="팀별 통계 정보 조회")
async def get_team_statistics(
    team_name: str,
    service: AgentLogService = Depends(get_agent_log_service)
):
    """특정 팀의 통계 정보를 조회합니다."""
    return service.get_team_statistics(team_name)


@router.get("/runs/{run_id}/full", response_model=schemas.AgentRunRead, summary="실행 기록 전체 조회 (메시지 포함)")
async def get_run_with_messages(
    run_id: int,
    service: AgentLogService = Depends(get_agent_log_service)
):
    """실행 기록과 모든 메시지를 함께 조회합니다."""
    run = service.get_run_with_messages(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="실행 기록을 찾을 수 없습니다")
    return run

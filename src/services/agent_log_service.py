"""
에이전트 로그 서비스 계층
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from src.core import schemas
from src.repositories.agent_logs import AgentRunRepository, AgentMessageRepository


class AgentLogService:
    """에이전트 실행 로그 및 메시지 관리 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.run_repo = AgentRunRepository(db)
        self.message_repo = AgentMessageRepository(db)
    
    # ============================================================================
    # AgentRun 관련 서비스 메서드
    # ============================================================================
    
    def create_run(self, run_data: schemas.AgentRunCreate) -> schemas.AgentRunRead:
        """새로운 에이전트 실행 기록 생성"""
        run = self.run_repo.create(
            team_name=run_data.team_name,
            task=run_data.task,
            model=run_data.model
        )
        return schemas.AgentRunRead.model_validate(run)
    
    def get_run(self, run_id: int) -> Optional[schemas.AgentRunRead]:
        """특정 실행 기록 조회 (메시지 포함)"""
        run = self.run_repo.get(run_id)
        if not run:
            return None
        
        # 메시지도 함께 조회
        messages = self.message_repo.list_by_run(run_id)
        run_data = schemas.AgentRunRead.model_validate(run)
        run_data.messages = [schemas.AgentMessageRead.model_validate(msg) for msg in messages]
        
        return run_data
    
    def list_runs(
        self, 
        team_name: Optional[str] = None, 
        limit: int = 50
    ) -> List[schemas.AgentRunRead]:
        """실행 기록 목록 조회"""
        runs = self.run_repo.list(team_name=team_name, limit=limit)
        return [schemas.AgentRunRead.model_validate(run) for run in runs]
    
    def finish_run(self, run_id: int, status: str = "completed") -> Optional[schemas.AgentRunRead]:
        """실행 기록 완료 처리"""
        run = self.run_repo.finish(run_id, status)
        if not run:
            return None
        return schemas.AgentRunRead.model_validate(run)
    
    # ============================================================================
    # AgentMessage 관련 서비스 메서드
    # ============================================================================
    
    def add_message(self, message_data: schemas.AgentMessageCreate) -> schemas.AgentMessageRead:
        """새로운 메시지 추가"""
        message = self.message_repo.add(
            run_id=message_data.run_id,
            agent_name=message_data.agent_name,
            role=message_data.role,
            content=message_data.content,
            tool_name=message_data.tool_name
        )
        return schemas.AgentMessageRead.model_validate(message)
    
    def get_messages_by_run(self, run_id: int) -> List[schemas.AgentMessageRead]:
        """특정 실행의 모든 메시지 조회"""
        messages = self.message_repo.list_by_run(run_id)
        return [schemas.AgentMessageRead.model_validate(msg) for msg in messages]
    
    # ============================================================================
    # 통합 조회 메서드
    # ============================================================================
    
    def get_run_with_messages(self, run_id: int) -> Optional[schemas.AgentRunRead]:
        """실행 기록과 모든 메시지를 함께 조회"""
        return self.get_run(run_id)
    
    def get_team_statistics(self, team_name: str) -> dict:
        """팀별 통계 정보 조회"""
        runs = self.run_repo.list(team_name=team_name, limit=1000)  # 충분히 큰 수
        
        if not runs:
            return {
                "team_name": team_name,
                "total_runs": 0,
                "completed_runs": 0,
                "running_runs": 0,
                "failed_runs": 0,
                "average_duration": 0,
                "total_messages": 0
            }
        
        completed_runs = [r for r in runs if r.status == "completed"]
        running_runs = [r for r in runs if r.status == "running"]
        failed_runs = [r for r in runs if r.status == "failed"]
        
        # 평균 실행 시간 계산 (완료된 실행만)
        total_duration = 0
        for run in completed_runs:
            if run.ended_at and run.started_at:
                duration = (run.ended_at - run.started_at).total_seconds()
                total_duration += duration
        
        average_duration = total_duration / len(completed_runs) if completed_runs else 0
        
        # 총 메시지 수 계산
        total_messages = 0
        for run in runs:
            messages = self.message_repo.list_by_run(run.id)
            total_messages += len(messages)
        
        return {
            "team_name": team_name,
            "total_runs": len(runs),
            "completed_runs": len(completed_runs),
            "running_runs": len(running_runs),
            "failed_runs": len(failed_runs),
            "average_duration": round(average_duration, 2),
            "total_messages": total_messages
        }

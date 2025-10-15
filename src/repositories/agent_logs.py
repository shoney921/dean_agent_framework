"""
에이전트 실행 및 메시지 저장/조회 리포지토리
"""

from datetime import datetime
from typing import List, Optional, Sequence

from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from src.core import models as orm


class AgentRunRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, team_name: str, task: str, model: Optional[str] = None) -> orm.AgentRun:
        run = orm.AgentRun(team_name=team_name, task=task, model=model)
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def finish(self, run_id: int, status: str = "completed") -> Optional[orm.AgentRun]:
        run = self.db.get(orm.AgentRun, run_id)
        if not run:
            return None
        run.ended_at = datetime.utcnow()
        run.status = status
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def get(self, run_id: int) -> Optional[orm.AgentRun]:
        return self.db.get(orm.AgentRun, run_id)

    def list(self, team_name: Optional[str] = None, limit: int = 50) -> List[orm.AgentRun]:
        stmt = select(orm.AgentRun).order_by(desc(orm.AgentRun.started_at)).limit(limit)
        if team_name:
            stmt = stmt.filter(orm.AgentRun.team_name == team_name)
        return list(self.db.execute(stmt).scalars().all())


class AgentMessageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(
        self,
        run_id: int,
        agent_name: str,
        role: str,
        content: str,
        tool_name: Optional[str] = None,
    ) -> orm.AgentMessage:
        msg = orm.AgentMessage(
            run_id=run_id,
            agent_name=agent_name,
            role=role,
            content=content,
            tool_name=tool_name,
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def list_by_run(self, run_id: int) -> List[orm.AgentMessage]:
        stmt = select(orm.AgentMessage).where(orm.AgentMessage.run_id == run_id).order_by(orm.AgentMessage.created_at)
        return list(self.db.execute(stmt).scalars().all())



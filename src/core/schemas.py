"""
Pydantic 스키마 정의
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AgentMessageCreate(BaseModel):
    run_id: int
    agent_name: str
    role: str
    content: str
    tool_name: Optional[str] = None


class AgentMessageRead(BaseModel):
    id: int
    run_id: int
    agent_name: str
    role: str
    content: str
    tool_name: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class AgentRunCreate(BaseModel):
    team_name: str
    task: str
    model: Optional[str] = None


class AgentRunUpdate(BaseModel):
    ended_at: Optional[datetime] = None
    status: Optional[str] = None


class AgentRunRead(BaseModel):
    id: int
    team_name: str
    task: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: str
    model: Optional[str] = None
    messages: List[AgentMessageRead] = Field(default_factory=list)

    model_config = {
        "from_attributes": True,
    }




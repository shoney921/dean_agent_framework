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


# Notion 관련 스키마
class NotionPageCreate(BaseModel):
    notion_page_id: str
    title: str
    url: Optional[str] = None
    parent_page_id: Optional[str] = None
    is_active: str = "true"


class NotionPageUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    parent_page_id: Optional[str] = None
    is_active: Optional[str] = None
    last_synced_at: Optional[datetime] = None


class NotionPageRead(BaseModel):
    id: int
    notion_page_id: str
    title: str
    url: Optional[str] = None
    parent_page_id: Optional[str] = None
    is_active: str
    created_at: datetime
    updated_at: datetime
    last_synced_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
    }


class NotionTodoCreate(BaseModel):
    notion_page_id: str
    block_id: str
    content: str
    checked: str = "false"
    block_index: int


class NotionTodoUpdate(BaseModel):
    content: Optional[str] = None
    checked: Optional[str] = None
    block_index: Optional[int] = None


class NotionTodoRead(BaseModel):
    id: int
    notion_page_id: str
    block_id: str
    content: str
    checked: str
    block_index: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class NotionConnectionTest(BaseModel):
    success: bool
    message: str
    api_key_valid: bool


class NotionPageListResponse(BaseModel):
    success: bool
    count: int
    pages: List[dict]
    message: Optional[str] = None


class NotionBatchStatusCreate(BaseModel):
    notion_page_id: str
    status: str
    message: Optional[str] = None
    last_run_at: Optional[datetime] = None


class NotionBatchStatusUpdate(BaseModel):
    status: Optional[str] = None
    message: Optional[str] = None
    last_run_at: Optional[datetime] = None


class NotionBatchStatusRead(BaseModel):
    id: int
    notion_page_id: str
    status: str
    message: Optional[str] = None
    last_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


# 배치 관련 스키마
class BatchStartRequest(BaseModel):
    notion_page_id: str


class BatchStartResponse(BaseModel):
    success: bool
    message: str
    notion_page_id: str
    start_time: str
    end_time: str


class BatchStopResponse(BaseModel):
    success: bool
    message: str
    notion_page_id: str
    end_time: str


class BatchStatusResponse(BaseModel):
    success: bool
    notion_page_id: str
    db_status: Optional[str] = None
    db_message: Optional[str] = None
    db_last_run_at: Optional[str] = None
    is_running: bool
    running_info: Optional[dict] = None



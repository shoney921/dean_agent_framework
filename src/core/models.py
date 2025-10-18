"""
SQLAlchemy ORM 모델 정의
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String(255), nullable=False, index=True)
    task = Column(Text, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="running", nullable=False)
    model = Column(String(255), nullable=True)

    messages = relationship("AgentMessage", back_populates="run", cascade="all, delete-orphan")


class AgentMessage(Base):
    __tablename__ = "agent_messages"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(255), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # user | assistant | tool | system
    content = Column(Text, nullable=False)
    tool_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    run = relationship("AgentRun", back_populates="messages")


class NotionPage(Base):
    __tablename__ = "notion_pages"

    id = Column(Integer, primary_key=True, index=True)
    notion_page_id = Column(String(255), nullable=False, unique=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=True)
    parent_page_id = Column(String(255), nullable=True)
    is_active = Column(String(10), default="true", nullable=False)  # AI 배치 동작 여부
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_synced_at = Column(DateTime, nullable=True)


class NotionTodo(Base):
    __tablename__ = "notion_todos"

    id = Column(Integer, primary_key=True, index=True)
    notion_page_id = Column(String(255), ForeignKey("notion_pages.notion_page_id"), nullable=False, index=True)
    block_id = Column(String(255), nullable=False, unique=True, index=True)
    content = Column(Text, nullable=False)
    checked = Column(String(10), default="false", nullable=False)
    block_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    notion_page = relationship("NotionPage")




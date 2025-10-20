"""
Notion 배치 상태 리포지토리
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from src.core.models import NotionBatchStatus


def get_status_map_by_page_ids(db: Session, notion_page_ids: List[str]) -> Dict[str, NotionBatchStatus]:
    if not notion_page_ids:
        return {}
    rows = (
        db.query(NotionBatchStatus)
        .filter(NotionBatchStatus.notion_page_id.in_(notion_page_ids))
        .all()
    )
    latest_by_page: Dict[str, NotionBatchStatus] = {}
    for row in rows:
        current = latest_by_page.get(row.notion_page_id)
        if current is None or (row.updated_at and current.updated_at and row.updated_at > current.updated_at):
            latest_by_page[row.notion_page_id] = row
        elif current is None:
            latest_by_page[row.notion_page_id] = row
    return latest_by_page


def get_status(db: Session, notion_page_id: str) -> Optional[NotionBatchStatus]:
    return (
        db.query(NotionBatchStatus)
        .filter(NotionBatchStatus.notion_page_id == notion_page_id)
        .order_by(NotionBatchStatus.updated_at.desc())
        .first()
    )

def upsert_status(db: Session, notion_page_id: str, status: str, message: Optional[str] = None, last_run_at=None) -> NotionBatchStatus:
    row = (
        db.query(NotionBatchStatus)
        .filter(NotionBatchStatus.notion_page_id == notion_page_id)
        .first()
    )
    if row is None:
        row = NotionBatchStatus(
            notion_page_id=notion_page_id,
            status=status,
            message=message,
            last_run_at=last_run_at,
        )
        db.add(row)
    else:
        row.status = status
        row.message = message
        if last_run_at is not None:
            row.last_run_at = last_run_at
    db.commit()
    db.refresh(row)
    return row



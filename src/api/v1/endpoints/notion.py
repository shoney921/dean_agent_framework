"""
Notion 관련 API 엔드포인트
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
import re

from src.api.deps import get_db
from src.services.notion_service import NotionService
from src.core.schemas import (
    NotionConnectionTest,
    NotionPageListResponse,
    NotionPageRead,
    NotionTodoRead,
    NotionBatchStatusRead
)

router = APIRouter()


@router.post("/test-connection", response_model=NotionConnectionTest)
def test_notion_connection(
    api_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Notion API 연결을 테스트합니다.
    
    Args:
        api_key (str, optional): 테스트할 API 키
        db (Session): 데이터베이스 세션
        
    Returns:
        NotionConnectionTest: 연결 테스트 결과
    """
    notion_service = NotionService(db)
    return notion_service.test_notion_connection(api_key)


@router.get("/pages", response_model=NotionPageListResponse)
def get_notion_pages_list(
    page_size: int = Query(100, ge=1, le=100),
    filter_type: str = Query("page", regex="^(page|database)$"),
    sort_direction: str = Query("descending", regex="^(ascending|descending)$"),
    db: Session = Depends(get_db)
):
    """
    Notion 워크스페이스에서 페이지 목록을 조회합니다.
    
    Args:
        page_size (int): 페이지 크기 (1-100)
        filter_type (str): 필터 타입 ("page" 또는 "database")
        sort_direction (str): 정렬 방향 ("ascending" 또는 "descending")
        db (Session): 데이터베이스 세션
        
    Returns:
        NotionPageListResponse: 페이지 목록 조회 결과
    """
    notion_service = NotionService(db)
    return notion_service.get_notion_pages_list(page_size, filter_type, sort_direction)


@router.post("/pages/register")
def register_notion_page_for_ai_batch(
    notion_page_id: str,
    title: str,
    url: Optional[str] = None,
    parent_page_id: Optional[str] = None,
    is_active: str = "true",
    db: Session = Depends(get_db)
):
    """
    AI 배치 동작할 Notion 페이지를 데이터베이스에 등록합니다.
    
    Args:
        notion_page_id (str): Notion 페이지 ID
        title (str): 페이지 제목
        url (str, optional): 페이지 URL
        parent_page_id (str, optional): 부모 페이지 ID
        is_active (str): AI 배치 동작 여부 ("true" 또는 "false")
        db (Session): 데이터베이스 세션
        
    Returns:
        Dict: 등록 결과
    """
    notion_service = NotionService(db)
    result = notion_service.register_notion_page_for_ai_batch(
        notion_page_id, title, url, parent_page_id, is_active
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.get("/pages/registered", response_model=List[NotionPageRead])
def get_registered_pages(db: Session = Depends(get_db)):
    """
    등록된 Notion 페이지 목록을 조회합니다.
    
    Args:
        db (Session): 데이터베이스 세션
        
    Returns:
        List[NotionPageRead]: 등록된 페이지 목록
    """
    notion_service = NotionService(db)
    return notion_service.get_registered_pages()


@router.get("/pages/active", response_model=List[NotionPageRead])
def get_active_pages(db: Session = Depends(get_db)):
    """
    AI 배치 동작이 활성화된 Notion 페이지 목록을 조회합니다.
    
    Args:
        db (Session): 데이터베이스 세션
        
    Returns:
        List[NotionPageRead]: 활성화된 페이지 목록
    """
    notion_service = NotionService(db)
    return notion_service.get_active_pages()


@router.get("/pages/{notion_page_id}/todos")
def get_notion_todos_from_page(
    notion_page_id: str = Path(..., description="Notion 페이지 ID (UUID 형식)"),
    db: Session = Depends(get_db)
):
    """
    특정 Notion 페이지의 투두리스트 항목들을 조회합니다.
    
    Args:
        notion_page_id (str): Notion 페이지 ID
        db (Session): 데이터베이스 세션
        
    Returns:
        Dict: 투두리스트 조회 결과
    """
    notion_service = NotionService(db)
    result = notion_service.get_notion_todos_from_page(notion_page_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.post("/pages/{notion_page_id}/todos/sync")
def sync_notion_todos_to_db(
    notion_page_id: str = Path(..., description="Notion 페이지 ID (UUID 형식)"),
    db: Session = Depends(get_db)
):
    """
    Notion 페이지의 투두리스트를 데이터베이스에 동기화합니다.
    
    Args:
        notion_page_id (str): Notion 페이지 ID
        db (Session): 데이터베이스 세션
        
    Returns:
        Dict: 동기화 결과
    """
    notion_service = NotionService(db)
    result = notion_service.sync_notion_todos_to_db(notion_page_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.get("/pages/{notion_page_id}/todos/db", response_model=List[NotionTodoRead])
def get_page_todos_from_db(
    notion_page_id: str = Path(..., description="Notion 페이지 ID (UUID 형식)"),
    db: Session = Depends(get_db)
):
    """
    데이터베이스에서 특정 페이지의 투두리스트를 조회합니다.
    
    Args:
        notion_page_id (str): Notion 페이지 ID
        db (Session): 데이터베이스 세션
        
    Returns:
        List[NotionTodoRead]: 투두리스트
    """
    notion_service = NotionService(db)
    return notion_service.get_page_todos_from_db(notion_page_id)


@router.put("/pages/{notion_page_id}/active-status")
def update_page_active_status(
    notion_page_id: str = Path(..., description="Notion 페이지 ID (UUID 형식)"),
    is_active: str = Query(..., regex="^(true|false)$"),
    db: Session = Depends(get_db)
):
    """
    페이지의 AI 배치 동작 활성화 상태를 업데이트합니다.
    
    Args:
        notion_page_id (str): Notion 페이지 ID
        is_active (str): 활성화 상태 ("true" 또는 "false")
        db (Session): 데이터베이스 세션
        
    Returns:
        Dict: 업데이트 결과
    """
    notion_service = NotionService(db)
    result = notion_service.update_page_active_status(notion_page_id, is_active)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.get("/pages/{notion_page_id}/batch-status", response_model=NotionBatchStatusRead | None)
def get_batch_status(
    notion_page_id: str = Path(..., description="Notion 페이지 ID (UUID 형식)"),
    db: Session = Depends(get_db)
):
    """
    특정 페이지의 배치 상태를 조회합니다.
    """
    notion_service = NotionService(db)
    result = notion_service.get_batch_status(notion_page_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result.get("status")


@router.put("/pages/{notion_page_id}/batch-status", response_model=NotionBatchStatusRead)
def update_batch_status(
    notion_page_id: str = Path(..., description="Notion 페이지 ID (UUID 형식)"),
    status: str = Query(..., regex="^(running|completed|failed|idle)$"),
    message: str | None = None,
    db: Session = Depends(get_db)
):
    """
    특정 페이지의 배치 상태를 업데이트합니다.
    """
    notion_service = NotionService(db)
    result = notion_service.update_batch_status(notion_page_id, status, message)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result["status"]

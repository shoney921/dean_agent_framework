"""
배치 API 엔드포인트
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.services.batch_service import BatchService
from src.core.schemas import BatchStartRequest, BatchStartResponse, BatchStopResponse, BatchStatusResponse

router = APIRouter()


@router.post("/start", response_model=BatchStartResponse)
async def start_batch(
    request: BatchStartRequest,
    db: Session = Depends(get_db)
) -> BatchStartResponse:
    """
    배치 작업을 시작합니다.
    
    Args:
        request: 배치 시작 요청
        db: 데이터베이스 세션
        
    Returns:
        BatchStartResponse: 배치 시작 결과
    """
    try:
        batch_service = BatchService(db)
        result = batch_service.start_batch(request.notion_page_id)
        
        if result["success"]:
            return BatchStartResponse(
                success=True,
                message=result["message"],
                notion_page_id=result["notion_page_id"],
                start_time=result["start_time"],
                end_time=result["end_time"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"배치 시작 중 오류가 발생했습니다: {str(e)}")


@router.post("/stop/{notion_page_id}", response_model=BatchStopResponse)
async def stop_batch(
    notion_page_id: str,
    db: Session = Depends(get_db)
) -> BatchStopResponse:
    """
    배치 작업을 중지합니다.
    
    Args:
        notion_page_id: Notion 페이지 ID
        db: 데이터베이스 세션
        
    Returns:
        BatchStopResponse: 배치 중지 결과
    """
    try:
        batch_service = BatchService(db)
        result = batch_service.stop_batch(notion_page_id)
        
        if result["success"]:
            return BatchStopResponse(
                success=True,
                message=result["message"],
                notion_page_id=result["notion_page_id"],
                end_time=result["end_time"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"배치 중지 중 오류가 발생했습니다: {str(e)}")


@router.get("/status/{notion_page_id}", response_model=BatchStatusResponse)
async def get_batch_status(
    notion_page_id: str,
    db: Session = Depends(get_db)
) -> BatchStatusResponse:
    """
    배치 상태를 조회합니다.
    
    Args:
        notion_page_id: Notion 페이지 ID
        db: 데이터베이스 세션
        
    Returns:
        BatchStatusResponse: 배치 상태 정보
    """
    try:
        batch_service = BatchService(db)
        result = batch_service.get_batch_status(notion_page_id)
        
        if result["success"]:
            return BatchStatusResponse(
                success=True,
                notion_page_id=result["notion_page_id"],
                db_status=result["db_status"],
                db_message=result["db_message"],
                db_last_run_at=result["db_last_run_at"],
                is_running=result["is_running"],
                running_info=result["running_info"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"배치 상태 조회 중 오류가 발생했습니다: {str(e)}")


@router.get("/status", response_model=Dict[str, Any])
async def get_all_batch_status(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    모든 배치 상태를 조회합니다.
    
    Args:
        db: 데이터베이스 세션
        
    Returns:
        Dict: 모든 배치 상태 정보
    """
    try:
        batch_service = BatchService(db)
        result = batch_service.get_all_batch_status()
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"전체 배치 상태 조회 중 오류가 발생했습니다: {str(e)}")

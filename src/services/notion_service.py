
"""
Notion 서비스 모듈

Notion API와의 상호작용을 담당하는 비즈니스 로직을 제공합니다.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.client.notion_client import (
    get_notion_client,
    list_notion_pages,
    read_notion_page,
    search_notion
)
from src.core.models import NotionBatchStatus, NotionTodo
from src.core.schemas import NotionConnectionTest, NotionPageListResponse, NotionBatchStatusRead, NotionTodoRead
from src.repositories.notion_batch_status import get_status_map_by_page_ids, upsert_status, get_status


class NotionService:
    """Notion 서비스 클래스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def test_notion_connection(self, api_key: Optional[str] = None) -> NotionConnectionTest:
        """
        Notion API 키 연결을 테스트합니다.
        
        Args:
            api_key (str, optional): 테스트할 API 키. None인 경우 환경변수 사용
            
        Returns:
            NotionConnectionTest: 연결 테스트 결과
        """
        try:
            # API 키가 제공된 경우 임시로 환경변수 설정
            if api_key:
                import os
                original_key = os.getenv("NOTION_API_KEY")
                os.environ["NOTION_API_KEY"] = api_key
            
            # Notion 클라이언트 생성 및 연결 테스트
            notion = get_notion_client()
            
            # 간단한 검색으로 API 연결 테스트
            response = notion.search(query="", page_size=1)
            
            # API 키가 제공된 경우 원래 환경변수 복원
            if api_key:
                if original_key:
                    os.environ["NOTION_API_KEY"] = original_key
                else:
                    os.environ.pop("NOTION_API_KEY", None)
            
            return NotionConnectionTest(
                success=True,
                message="Notion API 연결이 성공적으로 확인되었습니다.",
                api_key_valid=True
            )
            
        except Exception as e:
            # API 키가 제공된 경우 원래 환경변수 복원
            if api_key:
                import os
                original_key = os.getenv("NOTION_API_KEY")
                if original_key:
                    os.environ["NOTION_API_KEY"] = original_key
                else:
                    os.environ.pop("NOTION_API_KEY", None)
            
            return NotionConnectionTest(
                success=False,
                message=f"Notion API 연결 실패: {str(e)}",
                api_key_valid=False
            )
    
    def get_notion_client_pages_and_upsert_batch_status_table(
        self,
        page_size: int = 100,
        filter_type: str = "page",
        sort_direction: str = "descending"
    ) -> NotionPageListResponse:
        """
        Notion 워크스페이스에서 페이지 목록을 조회합니다.
        
        Args:
            page_size (int): 페이지 크기
            filter_type (str): 필터 타입 ("page" 또는 "database")
            sort_direction (str): 정렬 방향
            
        Returns:
            NotionPageListResponse: 페이지 목록 조회 결과
        """
        try:
            # Notion API로 페이지 목록 조회
            result = list_notion_pages(
                page_size=page_size,
                filter_type=filter_type,
                sort_direction=sort_direction
            )
        
            if result["success"]:
                # 배치 상태 병합
                page_ids = [p.get("page_id") for p in result.get("pages", []) if p.get("page_id")]
                
                # 배치 상태 초기화
                for page_id in page_ids:
                    if not get_status(self.db, page_id):
                        upsert_status(self.db, page_id, "idle", None, None)

                # 배치 상태 조회
                status_map = get_status_map_by_page_ids(self.db, page_ids)
                merged_pages = []
                for p in result.get("pages", []):
                    pid = p.get("page_id")
                    status_row = status_map.get(pid)
                    status_payload = None
                    if status_row:
                        status_payload = NotionBatchStatusRead.model_validate(status_row).model_dump()
                    merged = {
                        **p,
                        "batch_status": status_payload
                    }
                    merged_pages.append(merged)

                return NotionPageListResponse(
                    success=True,
                    count=result["count"],
                    pages=merged_pages,
                    message="페이지 목록을 성공적으로 조회했습니다."
                )
            else:
                return NotionPageListResponse(
                    success=False,
                    count=0,
                    pages=[],
                    message=result.get("message", "페이지 목록 조회에 실패했습니다.")
                )
                
        except Exception as e:
            return NotionPageListResponse(
                success=False,
                count=0,
                pages=[],
                message=f"페이지 목록 조회 중 오류가 발생했습니다: {str(e)}"
            )

    def update_batch_status(self, notion_page_id: str, status: str, message: Optional[str] = None, last_run_at: Optional[datetime] = None) -> Dict[str, Any]:
        try:
            row = upsert_status(self.db, notion_page_id, status, message, last_run_at)

            # 투두리스트 동기화
            if status == "running":
                self.sync_notion_todos_to_db(notion_page_id)

            return {
                "success": True,
                "status": NotionBatchStatusRead.model_validate(row)
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"배치 상태 업데이트 중 오류가 발생했습니다: {str(e)}"
            }

    # def get_batch_status(self, notion_page_id: str) -> Dict[str, Any]:
    #     try:
    #         row = get_status(self.db, notion_page_id)
    #         if not row:
    #             return {"success": True, "status": None}
    #         return {
    #             "success": True,
    #             "status": NotionBatchStatusRead.model_validate(row)
    #         }
    #     except Exception as e:
    #         return {
    #             "success": False,
    #             "message": f"배치 상태 조회 중 오류가 발생했습니다: {str(e)}"
    #         }
    
    def get_notion_client_todos_from_page(self, notion_page_id: str) -> Dict[str, Any]:
        """
        특정 Notion 페이지의 투두리스트 항목들을 조회합니다.
        
        Args:
            notion_page_id (str): Notion 페이지 ID
            
        Returns:
            Dict: 투두리스트 조회 결과
        """
        try:
            # Notion API로 페이지 내용 조회
            page_result = read_notion_page(notion_page_id)
            
            if not page_result["success"]:
                return {
                    "success": False,
                    "message": f"페이지 조회 실패: {page_result.get('message', '')}",
                    "todos": []
                }
            
            # 투두 블록만 필터링
            todos = []
            for block in page_result.get("blocks", []):
                if block.get("type") == "to_do":
                    todo_data = {
                        "block_id": block.get("block_id", ""),
                        "content": block.get("content", ""),
                        "checked": "true" if block.get("checked", False) else "false",
                        "block_index": block.get("index", 0)
                    }
                    todos.append(todo_data)
            
            return {
                "success": True,
                "message": f"페이지 '{page_result.get('title', '')}'의 투두리스트를 성공적으로 조회했습니다.",
                "page_title": page_result.get("title", ""),
                "page_id": notion_page_id,
                "todos": todos,
                "total_count": len(todos)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"투두리스트 조회 중 오류가 발생했습니다: {str(e)}",
                "todos": []
            }
    
    def sync_notion_todos_to_db(self, notion_page_id: str) -> Dict[str, Any]:
        """
        Notion 페이지의 투두리스트를 데이터베이스에 동기화합니다.
        
        Args:
            notion_page_id (str): Notion 페이지 ID
            
        Returns:
            Dict: 동기화 결과
        """
        try:
            # Notion에서 투두리스트 조회
            todos_result = self.get_notion_client_todos_from_page(notion_page_id)
            
            if not todos_result["success"]:
                return todos_result

            # 기존 투두 block_id 목록 조회
            existing_block_ids = {
                todo.block_id for todo in self.db.query(NotionTodo).filter(
                    NotionTodo.notion_page_id == notion_page_id
                ).all()
            }
            
            # 새로운 투두만 추가
            synced_count = 0
            new_todos = [
                NotionTodo(
                    notion_page_id=notion_page_id,
                    block_id=todo["block_id"],
                    content=todo["content"], 
                    checked=todo["checked"],
                    status="pending",
                    block_index=todo["block_index"]
                )
                for todo in todos_result["todos"]
                if todo["block_id"] not in existing_block_ids
            ]
            
            if new_todos:
                self.db.bulk_save_objects(new_todos)
                synced_count = len(new_todos)
                
            # 페이지의 마지막 동기화 시간 업데이트
            batch_status = self.db.query(NotionBatchStatus).filter(
                NotionBatchStatus.notion_page_id == notion_page_id
            ).first()
            
            if batch_status:
                batch_status.last_synced_at = datetime.utcnow()
            
            self.db.commit()
            
            return {
                "success": True,
                "message": f"페이지 '{todos_result.get('page_title', '')}'의 투두리스트가 성공적으로 동기화되었습니다.",
                "synced_count": synced_count,
                "page_id": notion_page_id
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"투두리스트 동기화 중 오류가 발생했습니다: {str(e)}",
                "error": str(e)
            }
    
    # def get_registered_pages(self) -> List[NotionPageRead]:
    #     """
    #     등록된 Notion 페이지 목록을 조회합니다.
        
    #     Returns:
    #         List[NotionPageRead]: 등록된 페이지 목록
    #     """
    #     pages = self.db.query(NotionPage).all()
    #     return [NotionPageRead.model_validate(page) for page in pages]
    
    # def get_active_pages(self) -> List[NotionPageRead]:
    #     """
    #     AI 배치 동작이 활성화된 Notion 페이지 목록을 조회합니다.
        
    #     Returns:
    #         List[NotionPageRead]: 활성화된 페이지 목록
    #     """
    #     pages = self.db.query(NotionPage).filter(
    #         NotionPage.is_active == "true"
    #     ).all()
    #     return [NotionPageRead.model_validate(page) for page in pages]
    
    def get_page_todos_from_db(self, notion_page_id: str) -> List[NotionTodoRead]:
        """
        데이터베이스에서 특정 페이지의 투두리스트를 조회합니다.
        
        Args:
            notion_page_id (str): Notion 페이지 ID
            
        Returns:
            List[NotionTodoRead]: 투두리스트
        """
        todos = self.db.query(NotionTodo).filter(
            NotionTodo.notion_page_id == notion_page_id
        ).order_by(NotionTodo.block_index).all()
        
        return [NotionTodoRead.model_validate(todo) for todo in todos]
    
    # def update_page_active_status(self, notion_page_id: str, is_active: str) -> Dict[str, Any]:
    #     """
    #     페이지의 AI 배치 동작 활성화 상태를 업데이트합니다.
        
    #     Args:
    #         notion_page_id (str): Notion 페이지 ID
    #         is_active (str): 활성화 상태 ("true" 또는 "false")
            
    #     Returns:
    #         Dict: 업데이트 결과
    #     """
    #     try:
    #         page = self.db.query(NotionBatchStatus).filter(
    #             NotionBatchStatus.notion_page_id == notion_page_id
    #         ).first()
            
    #         if not page:
    #             return {
    #                 "success": False,
    #                 "message": "해당 페이지를 찾을 수 없습니다."
    #             }
            
    #         page.is_active = is_active
    #         page.updated_at = datetime.utcnow()
            
    #         self.db.commit()
            
    #         status_text = "활성화" if is_active == "true" else "비활성화"
            
    #         return {
    #             "success": True,
    #             "message": f"페이지 '{page.title}'가 {status_text}되었습니다.",
    #             "page_id": page.id,
    #             "notion_page_id": notion_page_id
    #         }
            
    #     except Exception as e:
    #         self.db.rollback()
    #         return {
    #             "success": False,
    #             "message": f"상태 업데이트 중 오류가 발생했습니다: {str(e)}",
    #             "error": str(e)
    #         }
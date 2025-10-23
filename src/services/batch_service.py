"""
배치 서비스 모듈

Notion 배치 작업을 관리하는 서비스입니다.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from threading import Thread
import time

from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from src.core.models import NotionBatchStatus, NotionTodo
from src.core.config import BATCH_INTERVAL_SECONDS, BATCH_DURATION_MINUTES, BATCH_TIMEOUT_MINUTES
from src.client.notion_client import get_notion_client, append_completion_message, append_completion_message_with_toggle
from src.core.schemas import NotionBatchStatusRead
from src.repositories.notion_batch_status import upsert_status, get_status

from src.services.ai_service import AIService
from src.services.notion_service import NotionService

class BatchService:
    """배치 서비스 클래스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.logger = logging.getLogger(__name__)
        
        # 실행 중인 배치 작업 추적
        self.running_batches: Dict[str, Dict[str, Any]] = {}
        self.notion_service = NotionService(db)
        self.notion_client = get_notion_client()
        self.notion_batch_status = NotionBatchStatus()
        self.ai_service = AIService(db)
        self._is_processing = False  # 동시 실행 방지 플래그
    
    def update_batch_status(self, notion_page_id: str, status: str, message: Optional[str] = None, last_run_at: Optional[datetime] = None) -> Dict[str, Any]:
        try:
            row = upsert_status(self.db, notion_page_id, status, message, last_run_at)

            if status == "running":
                self.start_batch(notion_page_id)

            if status == "idle":
                self.stop_batch(notion_page_id)

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
    
    def start_batch(self, notion_page_id: str) -> Dict[str, Any]:
        """
        배치 작업을 시작합니다.
        
        Args:
            notion_page_id (str): Notion 페이지 ID
            
        Returns:
            Dict: 시작 결과
        """
        try:
            # 이미 실행 중인 배치가 있는지 확인
            if notion_page_id in self.running_batches:
                return {
                    "success": False,
                    "message": f"페이지 {notion_page_id}의 배치가 이미 실행 중입니다."
                }
            
            # 배치 상태를 running으로 변경
            upsert_status(
                self.db, 
                notion_page_id, 
                "running", 
                "배치 작업이 시작되었습니다.",
                datetime.utcnow()
            )
            
            # 배치 작업 정보 저장
            batch_info = {
                "notion_page_id": notion_page_id,
                "start_time": datetime.utcnow(),
                "end_time": datetime.utcnow() + timedelta(minutes=BATCH_TIMEOUT_MINUTES),
                "status": "running"
            }
            self.running_batches[notion_page_id] = batch_info
            
            job_id = f"batch_{notion_page_id}"
            self.scheduler.add_job(
                func=self._execute_batch_cycle,
                trigger=IntervalTrigger(seconds=BATCH_INTERVAL_SECONDS), #스케줄 주기
                args=[notion_page_id],
                id=job_id,
                replace_existing=True
            )
            
            end_time = datetime.utcnow() + timedelta(minutes=BATCH_DURATION_MINUTES)
            self.scheduler.add_job(
                func=self.stop_batch,
                trigger=DateTrigger(run_date=end_time), #배치 종료 시간
                args=[notion_page_id],
                id=f"batch_end_{notion_page_id}",
                replace_existing=True
            )
            
            self.logger.info(f"배치 작업이 시작되었습니다: {notion_page_id}")
            
            return {
                "success": True,
                "message": f"배치 작업이 시작되었습니다. 15분 후 자동 종료됩니다.",
                "notion_page_id": notion_page_id,
                "start_time": batch_info["start_time"].isoformat(),
                "end_time": batch_info["end_time"].isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"배치 시작 중 오류 발생: {str(e)}")
            return {
                "success": False,
                "message": f"배치 시작 중 오류가 발생했습니다: {str(e)}"
            }
    
    def stop_batch(self, notion_page_id: str) -> Dict[str, Any]:
        """
        배치 작업을 중지합니다.
        
        Args:
            notion_page_id (str): Notion 페이지 ID
            
        Returns:
            Dict: 중지 결과
        """
        try:
            # 실행 중인 배치가 있는지 확인
            if notion_page_id not in self.running_batches:
                return {
                    "success": False,
                    "message": f"페이지 {notion_page_id}의 배치가 실행 중이 아닙니다."
                }
            
            # 스케줄러에서 작업 제거
            job_id = f"batch_{notion_page_id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            end_job_id = f"batch_end_{notion_page_id}"
            if self.scheduler.get_job(end_job_id):
                self.scheduler.remove_job(end_job_id)
            
            # 배치 상태를 completed로 변경
            upsert_status(
                self.db, 
                notion_page_id, 
                "completed", 
                "배치 작업이 정상적으로 완료되었습니다.",
                datetime.utcnow()
            )
            
            # 실행 중인 배치 정보 제거
            del self.running_batches[notion_page_id]
            
            self.logger.info(f"배치 작업이 중지되었습니다: {notion_page_id}")
            
            return {
                "success": True,
                "message": f"배치 작업이 중지되었습니다.",
                "notion_page_id": notion_page_id,
                "end_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"배치 중지 중 오류 발생: {str(e)}")
            return {
                "success": False,
                "message": f"배치 중지 중 오류가 발생했습니다: {str(e)}"
            }
    
    def _execute_batch_cycle(self, notion_page_id: str):
        """
        배치 사이클을 실행합니다.
        
        Args:
            notion_page_id (str): Notion 페이지 ID
        """
        try:
            # 동시 실행 방지 체크
            if self._is_processing:
                self.logger.warning(f"이미 배치 작업이 실행 중입니다. 건너뜁니다: {notion_page_id}")
                return
                
            self.logger.info(f"배치 사이클 실행: {notion_page_id}")
            
            # 처리 중 플래그 설정
            self._is_processing = True
            
            try:
                # 투두리스트 동기화 (노션 -> DB)
                self.notion_service.sync_notion_todos_to_db(notion_page_id)
                
                # pending 상태인 투두 항목들 조회
                pending_todos = self.db.query(NotionTodo).filter(
                    NotionTodo.notion_page_id == notion_page_id,
                    NotionTodo.status == "pending",
                    NotionTodo.checked == "false"
                ).all()
                
                if not pending_todos:
                    self.logger.info(f"처리할 pending 투두가 없습니다: {notion_page_id}")
                    return
                
                # 설정에서 배치 크기 가져오기
                from src.core.config import QUEUE_BATCH_SIZE
                max_concurrent = QUEUE_BATCH_SIZE
                todos_to_process = pending_todos[:max_concurrent]
                
                self.logger.info(f"처리할 투두 {len(todos_to_process)}개 선택 (전체 {len(pending_todos)}개 중)")
                
                # 각 투두를 순차적으로 처리 (단순하게)
                for i, todo in enumerate(todos_to_process):
                    try:
                        self.logger.info(f"투두 처리 중 ({i+1}/{len(todos_to_process)}): {todo.content[:50]}...")
                        self._process_todo_item(todo)
                        
                    except Exception as e:
                        self.logger.error(f"투두 처리 중 오류: {todo.block_id}, {str(e)}")
                        # 개별 투두 처리 실패는 전체 배치를 중단시키지 않음
                        continue
                
                # 배치 상태 업데이트
                upsert_status(
                    self.db,
                    notion_page_id,
                    "running",
                    f"배치 작업 진행 중 - {len(todos_to_process)}개 항목 처리",
                    datetime.utcnow()
                )
                
            finally:
                # 처리 완료 후 플래그 해제
                self._is_processing = False
            
        except Exception as e:
            self.logger.error(f"배치 사이클 실행 중 오류: {str(e)}")
            # 오류 발생 시에도 플래그 해제
            self._is_processing = False
            # 배치 상태를 failed로 변경
            upsert_status(
                self.db,
                notion_page_id,
                "failed",
                f"배치 작업 중 오류 발생: {str(e)}",
                datetime.utcnow()
            )
    

    def _process_todo_item(self, todo: NotionTodo):
        """
        개별 투두 항목을 처리합니다.
        
        Args:
            todo (NotionTodo): 처리할 투두 항목
        """
        try:
            # AI Agent 랭그래프 호출해서 투두 내용을 처리
            self.logger.info(f"투두 라우팅 시작: {todo.content}")
            
            # 배치별로 새로운 AI 서비스 인스턴스 생성 (팀 충돌 방지)
            from src.services.ai_service import AIService
            batch_ai_service = AIService(self.db)
            
            # 팀 라우팅 실행 (비동기) - 더 안전한 처리
            import asyncio
            try:
                # 새로운 이벤트 루프 생성 (기존 루프와 충돌 방지)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(batch_ai_service.route_todo_to_agent(todo))
                loop.close()
            except Exception as ai_error:
                self.logger.error(f"AI 처리 중 오류: {ai_error}")
                result = {
                    "success": False,
                    "ai_result": f"AI 처리 중 오류 발생: {str(ai_error)}",
                    "url": ""
                }

            print(f"투두 처리 결과: {result}")

            # AI 처리 결과를 Notion에 추가
            ai_summary = result.get('ai_result', 'AI 처리 완료')
            url = result.get('url', '')
            completion_message = f"{todo.content} 투두 처리 결과:\n{ai_summary}\n{url}"
            
            try:
                # append_result = append_completion_message(todo.block_id, completion_message)
                append_result = append_completion_message_with_toggle(todo.block_id, completion_message)
                
                if append_result.get('success'):
                    self.logger.info(f"Notion에 AI 처리 결과 추가 성공: {todo.block_id}")
                else:
                    self.logger.warning(f"Notion AI 결과 추가 실패: {append_result.get('message')}")
            except Exception as notion_error:
                self.logger.error(f"Notion 업데이트 중 오류: {notion_error}")

            # 투두 상태를 done으로 변경
            todo.status = "done"
            todo.updated_at = datetime.utcnow()
            self.db.commit()
            
            self.logger.info(f"투두 처리 완료: {todo.block_id}")
            
        except Exception as e:
            self.logger.error(f"투두 처리 실패: {todo.block_id}, {str(e)}")
            # 개별 투두 실패는 전체 배치를 중단시키지 않음
            try:
                todo.status = "failed"
                todo.updated_at = datetime.utcnow()
                self.db.commit()
            except Exception as db_error:
                self.logger.error(f"DB 업데이트 실패: {db_error}")
    
    def _add_completion_message_to_notion(self, notion_page_id: str, block_id: str):
        """
        Notion 페이지에 완료 메시지를 추가합니다.
        
        Args:
            notion_page_id (str): Notion 페이지 ID
            block_id (str): 완료된 블록 ID
        """
        try:
            notion = get_notion_client()
            
            # 완료 메시지 추가
            completion_text = f"✅ 작업 완료: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # 해당 블록 아래에 완료 메시지 추가
            notion.blocks.children.append(
                block_id=block_id,
                children=[
                    {
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": completion_text
                                    }
                                }
                            ]
                        }
                    }
                ]
            )
            
            self.logger.info(f"Notion에 완료 메시지 추가: {block_id}")
            
        except Exception as e:
            self.logger.error(f"Notion 완료 메시지 추가 실패: {str(e)}")
            # Notion API 오류는 배치를 중단시키지 않음
    
    def get_batch_status(self, notion_page_id: str) -> Dict[str, Any]:
        """
        배치 상태를 조회합니다.
        
        Args:
            notion_page_id (str): Notion 페이지 ID
            
        Returns:
            Dict: 배치 상태 정보
        """
        try:
            # 데이터베이스에서 상태 조회
            batch_status = get_status(self.db, notion_page_id)
            
            # 실행 중인 배치 정보
            running_info = self.running_batches.get(notion_page_id)
            
            return {
                "success": True,
                "notion_page_id": notion_page_id,
                "db_status": batch_status.status if batch_status else None,
                "db_message": batch_status.message if batch_status else None,
                "db_last_run_at": batch_status.last_run_at.isoformat() if batch_status and batch_status.last_run_at else None,
                "is_running": notion_page_id in self.running_batches,
                "running_info": running_info
            }
            
        except Exception as e:
            self.logger.error(f"배치 상태 조회 중 오류: {str(e)}")
            return {
                "success": False,
                "message": f"배치 상태 조회 중 오류가 발생했습니다: {str(e)}"
            }
    
    def get_all_batch_status(self) -> Dict[str, Any]:
        """
        모든 배치 상태를 조회합니다.
        
        Returns:
            Dict: 모든 배치 상태 정보
        """
        try:
            return {
                "success": True,
                "running_batches": list(self.running_batches.keys()),
                "running_count": len(self.running_batches),
                "scheduler_jobs": [job.id for job in self.scheduler.get_jobs()]
            }
            
        except Exception as e:
            self.logger.error(f"전체 배치 상태 조회 중 오류: {str(e)}")
            return {
                "success": False,
                "message": f"전체 배치 상태 조회 중 오류가 발생했습니다: {str(e)}"
            }
    
    def shutdown(self):
        """배치 서비스를 종료합니다."""
        try:
            # 모든 실행 중인 배치를 중지
            for notion_page_id in list(self.running_batches.keys()):
                self.stop_batch(notion_page_id)
            
            # 스케줄러 종료
            self.scheduler.shutdown()
            
            self.logger.info("배치 서비스가 종료되었습니다.")
            
        except Exception as e:
            self.logger.error(f"배치 서비스 종료 중 오류: {str(e)}")

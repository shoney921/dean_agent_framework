


import asyncio
from typing import List, Dict, Any
from requests import Session

from src.ai.agents.analysis_agent import create_devil_advocate_analyst_agent
from src.ai.agents.base import create_model_client
from src.ai.agents.analysis_agent import create_analysis_agent
from src.ai.agents.data_analyst_agent import create_data_analyst_agent
from src.ai.agents.insight_agent import create_insight_agent
from src.ai.agents.web_search_agent import create_web_search_agent, create_google_search_agent
from src.ai.orchestrator.team import create_team, run_team_task
from src.core.models import NotionTodo
from src.repositories.agent_logs import AgentMessageRepository, AgentRunRepository


class AIService:
    """AI 서비스 클래스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.run_repo = AgentRunRepository(db)
        self.msg_repo = AgentMessageRepository(db)
        self.model_client = create_model_client()

        # 에이전트 생성
        self.web_search_agent = create_web_search_agent(self.model_client)
        self.google_search_agent = create_google_search_agent(self.model_client)
        self.data_analyst_agent = create_data_analyst_agent(self.model_client)
        self.analysis_agent = create_analysis_agent(self.model_client)
        self.insight_agent = create_insight_agent(self.model_client)
        self.devil_advocate_analyst_agent = create_devil_advocate_analyst_agent(self.model_client)
        
        # 팀 생성
        self.team = create_team(
            [
                self.web_search_agent, 
                self.google_search_agent, 
                self.data_analyst_agent, 
                # self.analysis_agent, 
                # self.insight_agent, 
                # self.devil_advocate_analyst_agent
            ],
            self.model_client
        )
    
    async def route_todo_to_agent(self, todo: NotionTodo):
        from src.core.config import DEFAULT_MODEL, TEAM_RUN_TIMEOUT_SECONDS
        import asyncio
        
        run = self.run_repo.create(team_name="투두 처리팀", task=todo.content, model=DEFAULT_MODEL)
        
        try:
            # 타임아웃과 함께 AI 작업 실행
            ai_result = await asyncio.wait_for(
                run_team_task(self.team, todo.content, run.id, self.msg_repo),
                timeout=TEAM_RUN_TIMEOUT_SECONDS
            )
            self.run_repo.finish(run.id, status="completed")
            
            # AI 처리 결과를 요약해서 반환 (너무 길면 잘라내기)
            summary_result = ai_result[:200] + "..." if len(ai_result) > 200 else ai_result
            
            return {
                "success": True, 
                "message": f"투두 '{todo.content}' 처리가 완료되었습니다.",
                "ai_result": summary_result,
                "url": self.generate_run_detail_url(run.id),
                "full_result": ai_result
            }
            
        except asyncio.TimeoutError:
            self.run_repo.finish(run.id, status="timeout")
            return {
                "success": False,
                "message": f"투두 '{todo.content}' 처리가 타임아웃으로 중단되었습니다.",
                "ai_result": "작업이 타임아웃으로 인해 중단되었습니다.",
                "url": self.generate_run_detail_url(run.id),
                "full_result": "타임아웃 발생"
            }
        except Exception as e:
            self.run_repo.finish(run.id, status="error")
            return {
                "success": False,
                "message": f"투두 '{todo.content}' 처리 중 오류가 발생했습니다: {str(e)}",
                "ai_result": f"오류 발생: {str(e)}",
                "url": self.generate_run_detail_url(run.id),
                "full_result": f"오류: {str(e)}"
            }

    def generate_run_detail_url(self, run_id: int):
        import os
        base_url = os.getenv("STREAMLIT_BASE_URL", "http://localhost:8501")
        return f"{base_url}/run_detail?run_id={run_id}"
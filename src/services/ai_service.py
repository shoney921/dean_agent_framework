


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
        from src.core.config import DEFAULT_MODEL
        run = self.run_repo.create(team_name="투두 처리팀", task=todo.content, model=DEFAULT_MODEL)
        ai_result = await run_team_task(self.team, todo.content, run.id, self.msg_repo)
        self.run_repo.finish(run.id, status="completed")
        
        # AI 처리 결과를 요약해서 반환 (너무 길면 잘라내기)
        summary_result = ai_result[:200] + "..." if len(ai_result) > 200 else ai_result
        
        return {
            "success": True, 
            "message": f"투두 '{todo.content}' 처리가 완료되었습니다.",
            "ai_result": summary_result,
            "full_result": ai_result
        }

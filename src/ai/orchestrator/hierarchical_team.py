"""
계층적 팀 구조 관리자

AutoGen의 SelectorGroupChat을 활용하여 더 깔끔하고 확장 가능한 
계층적 팀 구조를 구현합니다.
"""

import asyncio
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.core.config import MAX_MESSAGES
from src.repositories.agent_logs import AgentMessageRepository


class TeamType(Enum):
    """팀 타입 정의"""
    DATA_COLLECTION = "data_collection"
    ANALYSIS = "analysis"
    VALIDATION = "validation"
    MASTER = "master"


@dataclass
class TeamConfig:
    """팀 구성 설정"""
    name: str
    team_type: TeamType
    agent_factories: List[Callable[[OpenAIChatCompletionClient], AssistantAgent]]
    max_messages: int = MAX_MESSAGES
    termination_keyword: str = "TERMINATE"


@dataclass
class TeamResult:
    """팀 실행 결과"""
    team_name: str
    result: str
    success: bool = True
    error: Optional[str] = None


@dataclass
class HierarchicalTask:
    """계층적 작업 정의"""
    main_task: str
    sub_tasks: Dict[str, str] = field(default_factory=dict)
    execution_order: List[str] = field(default_factory=list)


class TeamManager:
    """계층적 팀 관리자"""
    
    def __init__(self, model_client: OpenAIChatCompletionClient):
        self.model_client = model_client
        self.teams: Dict[str, SelectorGroupChat] = {}
        self.team_configs: Dict[str, TeamConfig] = {}
        self._setup_default_teams()
    
    def _setup_default_teams(self):
        """기본 팀 구성 설정"""
        from src.ai.agents.web_search_agent import create_web_search_agent
        from src.ai.agents.data_analyst_agent import create_data_analyst_agent
        from src.ai.agents.analysis_agent import create_analysis_agent, create_devil_advocate_analyst_agent
        from src.ai.agents.insight_agent import create_insight_agent
        from src.ai.agents.summary_agent import create_summary_agent
        
        # 데이터 수집 팀
        self.register_team(TeamConfig(
            name="데이터수집팀",
            team_type=TeamType.DATA_COLLECTION,
            agent_factories=[create_web_search_agent, create_data_analyst_agent]
        ))
        
        # 분석 팀
        self.register_team(TeamConfig(
            name="분석팀",
            team_type=TeamType.ANALYSIS,
            agent_factories=[create_analysis_agent, create_insight_agent]
        ))
        
        # 검증 팀
        self.register_team(TeamConfig(
            name="검증팀",
            team_type=TeamType.VALIDATION,
            agent_factories=[create_devil_advocate_analyst_agent, create_summary_agent]
        ))
        
        # 마스터 팀
        self.register_team(TeamConfig(
            name="마스터팀",
            team_type=TeamType.MASTER,
            agent_factories=[create_analysis_agent]
        ))
    
    def register_team(self, config: TeamConfig):
        """팀 등록"""
        self.team_configs[config.name] = config
        self._create_team(config)
    
    def _create_team(self, config: TeamConfig):
        """팀 생성"""
        agents = [factory(self.model_client) for factory in config.agent_factories]
        
        termination = TextMentionTermination(config.termination_keyword) | MaxMessageTermination(max_messages=config.max_messages)
        
        team = SelectorGroupChat(
            participants=agents,
            termination_condition=termination,
            model_client=self.model_client,
        )
        
        self.teams[config.name] = team
    
    async def run_team_task(
        self, 
        team_name: str, 
        task: str, 
        run_id: int, 
        msg_repo: AgentMessageRepository
    ) -> TeamResult:
        """단일 팀 작업 실행"""
        if team_name not in self.teams:
            return TeamResult(team_name, "", False, f"팀 '{team_name}'을 찾을 수 없습니다")
        
        team = self.teams[team_name]
        
        try:
            print(f"\n{'='*60}")
            print(f"🏢 {team_name} 작업 시작")
            print(f"📋 작업: {task}")
            print(f"{'='*60}")
            
            stream = team.run_stream(task=task)
            final_result = ""
            
            async for message in stream:
                if hasattr(message, 'source') and hasattr(message, 'content'):
                    print(f"\n---------- {message.source} ----------")
                    print(message.content)
                    
                    final_result = str(message.content)
                    
                    msg_repo.add(
                        run_id=run_id,
                        agent_name=f"{team_name}_{message.source}",
                        role="assistant",
                        content=str(message.content),
                        tool_name=getattr(message, "tool", None),
                    )
            
            print(f"\n✅ {team_name} 작업 완료!")
            return TeamResult(team_name, final_result, True)
            
        except Exception as e:
            error_msg = f"팀 '{team_name}' 실행 중 오류: {str(e)}"
            print(f"❌ {error_msg}")
            return TeamResult(team_name, "", False, error_msg)
    
    async def run_hierarchical_task(
        self, 
        task: HierarchicalTask, 
        run_id: int, 
        msg_repo: AgentMessageRepository
    ) -> Dict[str, TeamResult]:
        """계층적 작업 실행"""
        print(f"\n{'='*80}")
        print("🎯 계층적 팀 구조 작업 시작")
        print(f"📋 전체 작업: {task.main_task}")
        print(f"{'='*80}")
        
        results = {}
        
        # 1단계: 하위 팀들 병렬 실행
        if task.sub_tasks:
            sub_team_tasks = []
            for team_name, sub_task in task.sub_tasks.items():
                if team_name in self.teams:
                    task_coroutine = self.run_team_task(team_name, sub_task, run_id, msg_repo)
                    sub_team_tasks.append((team_name, task_coroutine))
            
            # 병렬 실행
            for team_name, task_coroutine in sub_team_tasks:
                result = await task_coroutine
                results[team_name] = result
        
        # 2단계: 마스터 팀이 결과 종합
        if "마스터팀" in self.teams and results:
            master_task = self._create_master_task(task.main_task, results)
            master_result = await self.run_team_task("마스터팀", master_task, run_id, msg_repo)
            results["마스터팀"] = master_result
        
        print(f"\n{'='*80}")
        print("🎉 계층적 팀 작업 완료!")
        print(f"{'='*80}")
        
        return results
    
    def _create_master_task(self, main_task: str, sub_results: Dict[str, TeamResult]) -> str:
        """마스터 팀용 종합 작업 생성"""
        results_text = ""
        for team_name, result in sub_results.items():
            if result.success:
                results_text += f"\n**{team_name} 결과**:\n{result.result}\n"
            else:
                results_text += f"\n**{team_name} 오류**: {result.error}\n"
        
        return f"""
다음은 하위 팀들의 작업 결과입니다. 이를 종합하여 최종 결과를 만들어주세요.

**원본 작업**: {main_task}

{results_text}

위 결과들을 바탕으로 최종 종합 보고서를 작성해주세요.
"""
    
    def create_auto_task(self, main_task: str) -> HierarchicalTask:
        """자동으로 하위 작업을 생성하는 헬퍼 메서드"""
        sub_tasks = {
            "데이터수집팀": f"다음 작업에 필요한 데이터를 수집해주세요: {main_task}",
            "분석팀": f"다음 작업을 분석해주세요: {main_task}",
            "검증팀": f"다음 작업의 결과를 검증하고 요약해주세요: {main_task}"
        }
        
        return HierarchicalTask(
            main_task=main_task,
            sub_tasks=sub_tasks,
            execution_order=["데이터수집팀", "분석팀", "검증팀", "마스터팀"]
        )


# 편의 함수들
async def run_hierarchical_team_task(
    task: str,
    run_id: int,
    msg_repo: AgentMessageRepository,
    model_client: OpenAIChatCompletionClient,
) -> Dict[str, TeamResult]:
    """
    계층적 팀 작업을 실행하는 편의 함수
    
    Args:
        task: 수행할 작업 설명
        run_id: 실행 ID
        msg_repo: 메시지 저장소
        model_client: 사용할 모델 클라이언트
        
    Returns:
        Dict[str, TeamResult]: 각 팀별 결과
    """
    team_manager = TeamManager(model_client)
    hierarchical_task = team_manager.create_auto_task(task)
    return await team_manager.run_hierarchical_task(hierarchical_task, run_id, msg_repo)


async def test_hierarchical_team_manager():
    """TeamManager 테스트 함수"""
    from src.ai.agents.base import create_model_client, print_model_info
    from src.core.config import DEFAULT_MODEL
    from src.repositories.agent_logs import AgentMessageRepository
    from src.core.db import init_db, SessionLocal
    
    init_db()
    db = SessionLocal()
    
    try:
        msg_repo = AgentMessageRepository(db)
        run_id = 1
        
        print("🏗️ 계층적 팀 매니저 테스트")
        
        # 모델 클라이언트 생성
        model_client = create_model_client()
        print_model_info(DEFAULT_MODEL)
        
        # 팀 매니저 생성
        team_manager = TeamManager(model_client)
        
        # 테스트 작업
        task = """
        LG CNS의 최근 주식 동향과 전망을 종합적으로 분석해주세요.
        다음 항목들을 포함해주세요:
        1. 최근 주가 동향 및 성과
        2. 재무 상태 분석
        3. 사업 포트폴리오 및 성장 동력
        4. 시장 전망 및 투자 의견
        5. 위험 요소 및 주의사항
        """
        
        # 계층적 작업 실행
        results = await team_manager.run_hierarchical_task(
            team_manager.create_auto_task(task), 
            run_id, 
            msg_repo
        )
        
        print("\n📊 최종 결과 요약")
        for team_name, result in results.items():
            print(f"\n**{team_name}**:")
            print("-" * 50)
            if result.success:
                print(result.result[:200] + "..." if len(result.result) > 200 else result.result)
            else:
                print(f"❌ 오류: {result.error}")
            print("-" * 50)
            
    finally:
        db.close()


if __name__ == "__main__":
    """
    계층적 팀 매니저 테스트 실행
    
    실행 방법:
        python -m src.ai.orchestrator.hierarchical_team
    """
    # SSL 검증 비활성화 설정
    import urllib3
    import requests
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    _original_request = requests.Session.request
    def _patched_request(self, *args, **kwargs):
        kwargs['verify'] = False
        return _original_request(self, *args, **kwargs)
    requests.Session.request = _patched_request
    
    asyncio.run(test_hierarchical_team_manager())


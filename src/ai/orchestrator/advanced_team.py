"""
고급 계층적 팀 시스템

설정 기반 팀 구성, 메시지 버스 통신, 그리고 깔끔한 API를 제공하는
통합 계층적 팀 관리 시스템입니다.
"""

import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.core.config import MAX_MESSAGES
from src.repositories.agent_logs import AgentMessageRepository
from .team_config import TeamConfigManager, get_config_manager
from .message_bus import MessageBus, TeamCoordinator, MessageType, TeamMessage, get_message_bus, get_team_coordinator


@dataclass
class ExecutionResult:
    """실행 결과"""
    success: bool
    results: Dict[str, Any]
    errors: Dict[str, str]
    execution_time: float
    team_statuses: Dict[str, Any]


class AdvancedTeamManager:
    """고급 팀 관리자"""
    
    def __init__(self, model_client: OpenAIChatCompletionClient):
        self.model_client = model_client
        self.config_manager = get_config_manager()
        self.message_bus = get_message_bus()
        self.coordinator = get_team_coordinator()
        self.teams: Dict[str, SelectorGroupChat] = {}
        self.team_handlers: Dict[str, callable] = {}
        self._initialized = False
    
    async def initialize(self):
        """시스템 초기화"""
        if self._initialized:
            return
        
        # 메시지 버스 시작
        await self.message_bus.start()
        
        # 모든 팀 생성
        for team_name in self.config_manager.list_teams():
            await self._create_team(team_name)
        
        # 팀별 메시지 핸들러 등록
        self._register_team_handlers()
        
        self._initialized = True
        print("✅ 고급 팀 관리자 초기화 완료")
    
    async def _create_team(self, team_name: str):
        """팀 생성"""
        team_def = self.config_manager.get_team_definition(team_name)
        if not team_def:
            raise ValueError(f"팀 정의를 찾을 수 없습니다: {team_name}")
        
        # 에이전트 생성
        agents = self.config_manager.create_agents_for_team(team_name, self.model_client)
        
        # 팀 생성
        termination = TextMentionTermination(team_def.termination_keyword) | MaxMessageTermination(max_messages=team_def.max_messages)
        
        team = SelectorGroupChat(
            participants=agents,
            termination_condition=termination,
            model_client=self.model_client,
        )
        
        self.teams[team_name] = team
        
        # 팀 상태 초기화
        self.message_bus.update_team_status(team_name, "idle")
        
        print(f"✅ 팀 생성 완료: {team_name}")
    
    def _register_team_handlers(self):
        """팀별 메시지 핸들러 등록"""
        for team_name in self.teams.keys():
            handler = self._create_team_handler(team_name)
            self.team_handlers[team_name] = handler
            self.message_bus.subscribe(team_name, handler)
    
    def _create_team_handler(self, team_name: str):
        """팀별 메시지 핸들러 생성"""
        async def team_handler(message: TeamMessage):
            if message.type == MessageType.TASK_REQUEST:
                await self._handle_team_task_request(team_name, message)
        
        return team_handler
    
    async def _handle_team_task_request(self, team_name: str, message: TeamMessage):
        """팀 작업 요청 처리"""
        try:
            # 팀 상태 업데이트
            self.message_bus.update_team_status(team_name, "running", current_task=message.content)
            
            # 작업 실행
            result = await self._execute_team_task(team_name, message.content)
            
            # 결과 전송
            result_message = TeamMessage(
                type=MessageType.TASK_RESULT,
                sender=team_name,
                recipient=message.sender,
                content=result,
                correlation_id=message.correlation_id
            )
            
            await self.message_bus.publish(result_message)
            
            # 팀 상태 업데이트
            self.message_bus.update_team_status(team_name, "completed", result=result)
            
        except Exception as e:
            # 오류 전송
            error_message = TeamMessage(
                type=MessageType.ERROR,
                sender=team_name,
                recipient=message.sender,
                content=str(e),
                correlation_id=message.correlation_id
            )
            
            await self.message_bus.publish(error_message)
            
            # 팀 상태 업데이트
            self.message_bus.update_team_status(team_name, "error", error=str(e))
    
    async def _execute_team_task(self, team_name: str, task: str) -> str:
        """팀 작업 실행"""
        team = self.teams[team_name]
        
        stream = team.run_stream(task=task)
        final_result = ""
        
        async for message in stream:
            if hasattr(message, 'source') and hasattr(message, 'content'):
                final_result = str(message.content)
        
        return final_result
    
    async def execute_workflow(
        self, 
        workflow_name: str, 
        main_task: str, 
        run_id: int, 
        msg_repo: AgentMessageRepository
    ) -> ExecutionResult:
        """워크플로우 실행"""
        if not self._initialized:
            await self.initialize()
        
        workflow = self.config_manager.get_workflow(workflow_name)
        if not workflow:
            raise ValueError(f"워크플로우를 찾을 수 없습니다: {workflow_name}")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            print(f"\n{'='*80}")
            print(f"🚀 워크플로우 실행: {workflow_name}")
            print(f"📋 작업: {main_task}")
            print(f"{'='*80}")
            
            # 하위 팀 작업 준비
            team_tasks = {}
            for team_name in workflow.teams:
                task_template = workflow.task_templates.get(team_name, "{main_task}")
                team_task = task_template.format(main_task=main_task)
                team_tasks[team_name] = team_task
            
            # 워크플로우 실행 전략에 따른 실행
            if workflow.execution_strategy == "parallel":
                results = await self._execute_parallel_workflow(team_tasks, run_id, msg_repo)
            else:
                results = await self._execute_sequential_workflow(team_tasks, run_id, msg_repo)
            
            # 마스터 팀이 있는 경우 결과 종합
            if workflow.master_team and workflow.master_team in self.teams:
                master_result = await self._execute_master_team(
                    workflow.master_team, 
                    main_task, 
                    results, 
                    run_id, 
                    msg_repo
                )
                results[workflow.master_team] = master_result
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return ExecutionResult(
                success=True,
                results=results,
                errors={},
                execution_time=execution_time,
                team_statuses=self.message_bus.get_all_team_statuses()
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ExecutionResult(
                success=False,
                results={},
                errors={"workflow_error": str(e)},
                execution_time=execution_time,
                team_statuses=self.message_bus.get_all_team_statuses()
            )
    
    async def _execute_parallel_workflow(
        self, 
        team_tasks: Dict[str, str], 
        run_id: int, 
        msg_repo: AgentMessageRepository
    ) -> Dict[str, str]:
        """병렬 워크플로우 실행"""
        print("🔄 병렬 워크플로우 실행 시작")
        
        # 모든 팀에 병렬로 작업 요청
        results = await self.coordinator.coordinate_parallel_tasks(team_tasks)
        
        # 결과를 메시지 저장소에 기록
        for team_name, result in results.items():
            if result:
                msg_repo.add(
                    run_id=run_id,
                    agent_name=team_name,
                    role="assistant",
                    content=result,
                    tool_name=None,
                )
        
        return results
    
    async def _execute_sequential_workflow(
        self, 
        team_tasks: Dict[str, str], 
        run_id: int, 
        msg_repo: AgentMessageRepository
    ) -> Dict[str, str]:
        """순차 워크플로우 실행"""
        print("🔄 순차 워크플로우 실행 시작")
        
        team_task_list = list(team_tasks.items())
        results = await self.coordinator.coordinate_sequential_tasks(team_task_list)
        
        # 결과를 메시지 저장소에 기록
        for i, (team_name, result) in enumerate(zip(team_tasks.keys(), results)):
            if result:
                msg_repo.add(
                    run_id=run_id,
                    agent_name=team_name,
                    role="assistant",
                    content=result,
                    tool_name=None,
                )
        
        return dict(zip(team_tasks.keys(), results))
    
    async def _execute_master_team(
        self, 
        master_team_name: str, 
        main_task: str, 
        sub_results: Dict[str, str], 
        run_id: int, 
        msg_repo: AgentMessageRepository
    ) -> str:
        """마스터 팀 실행"""
        print(f"🎖️ 마스터 팀 실행: {master_team_name}")
        
        # 마스터 팀 작업 생성
        master_task = self.config_manager.create_task_for_team(
            master_team_name, 
            main_task, 
            "standard_analysis"
        )
        
        # 하위 팀 결과를 마스터 작업에 포함
        sub_results_text = "\n".join([
            f"**{team_name} 결과**:\n{result}\n"
            for team_name, result in sub_results.items()
            if result
        ])
        
        master_task = master_task.replace("{sub_results}", sub_results_text)
        
        # 마스터 팀 실행
        result = await self.coordinator.request_task_from_team(master_team_name, master_task)
        
        # 결과 저장
        msg_repo.add(
            run_id=run_id,
            agent_name=master_team_name,
            role="assistant",
            content=result,
            tool_name=None,
        )
        
        return result
    
    async def shutdown(self):
        """시스템 종료"""
        await self.message_bus.stop()
        self._initialized = False
        print("🛑 고급 팀 관리자 종료 완료")
    
    def get_team_status(self, team_name: str) -> Optional[Any]:
        """팀 상태 조회"""
        return self.message_bus.get_team_status(team_name)
    
    def get_all_team_statuses(self) -> Dict[str, Any]:
        """모든 팀 상태 조회"""
        return self.message_bus.get_all_team_statuses()


# 편의 함수들
async def run_advanced_hierarchical_task(
    task: str,
    run_id: int,
    msg_repo: AgentMessageRepository,
    model_client: OpenAIChatCompletionClient,
    workflow_name: str = "standard_analysis"
) -> ExecutionResult:
    """
    고급 계층적 팀 작업 실행
    
    Args:
        task: 수행할 작업 설명
        run_id: 실행 ID
        msg_repo: 메시지 저장소
        model_client: 사용할 모델 클라이언트
        workflow_name: 사용할 워크플로우 이름
        
    Returns:
        ExecutionResult: 실행 결과
    """
    team_manager = AdvancedTeamManager(model_client)
    
    try:
        result = await team_manager.execute_workflow(workflow_name, task, run_id, msg_repo)
        return result
    finally:
        await team_manager.shutdown()


async def test_advanced_team_system():
    """고급 팀 시스템 테스트"""
    from src.ai.agents.base import create_model_client, print_model_info
    from src.core.config import DEFAULT_MODEL
    from src.repositories.agent_logs import AgentMessageRepository
    from src.core.db import init_db, SessionLocal
    
    init_db()
    db = SessionLocal()
    
    try:
        msg_repo = AgentMessageRepository(db)
        run_id = 1
        
        print("🏗️ 고급 팀 시스템 테스트")
        
        # 모델 클라이언트 생성
        model_client = create_model_client()
        print_model_info(DEFAULT_MODEL)
        
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
        
        # 고급 팀 시스템 실행
        result = await run_advanced_hierarchical_task(task, run_id, msg_repo, model_client)
        
        print(f"\n{'='*80}")
        print("📊 실행 결과")
        print(f"{'='*80}")
        print(f"✅ 성공: {result.success}")
        print(f"⏱️ 실행 시간: {result.execution_time:.2f}초")
        
        if result.success:
            print(f"\n📋 팀별 결과:")
            for team_name, team_result in result.results.items():
                print(f"\n**{team_name}**:")
                print("-" * 50)
                if team_result:
                    print(team_result[:200] + "..." if len(team_result) > 200 else team_result)
                else:
                    print("결과 없음")
                print("-" * 50)
        else:
            print(f"\n❌ 오류:")
            for error_type, error_msg in result.errors.items():
                print(f"- {error_type}: {error_msg}")
        
        print(f"\n🏢 팀 상태:")
        for team_name, status in result.team_statuses.items():
            print(f"- {team_name}: {status.status}")
            
    finally:
        db.close()


if __name__ == "__main__":
    """
    고급 팀 시스템 테스트 실행
    
    실행 방법:
        python -m src.ai.orchestrator.advanced_team
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
    
    asyncio.run(test_advanced_team_system())



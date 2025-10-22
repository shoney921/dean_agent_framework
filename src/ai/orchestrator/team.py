"""
멀티 에이전트 팀 관리

여러 에이전트를 조율하여 협업하는 팀을 생성하고 관리합니다.
팀의 팀(Hierarchical Teams) 구조도 지원합니다.
"""

import asyncio
from typing import List, Optional, Dict, Any

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.core.config import MAX_MESSAGES, TEAM_RUN_TIMEOUT_SECONDS, DEVILS_ADVOCATE_PREVIEW_ROUNDS
from src.repositories.agent_logs import AgentMessageRepository


def create_team(
    agents: List[AssistantAgent],
    model_client: OpenAIChatCompletionClient,
    max_messages: int = MAX_MESSAGES
) -> SelectorGroupChat:
    """
    멀티 에이전트 팀을 생성합니다.
    
    Args:
        agents: 팀에 참여할 에이전트 리스트
        model_client: 사용할 모델 클라이언트
        max_messages: 최대 메시지 수
        
    Returns:
        SelectorGroupChat: 설정된 팀
    """
    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(max_messages=max_messages)
    
    selector_prompt = """다음 작업을 수행할 에이전트를 선택하세요.

    {roles}

    현재 대화 맥락:
    {history}

    위 대화를 읽고, {participants} 중에서 다음 작업을 수행할 에이전트를 선택하세요.
    다른 에이전트가 작업을 시작하기 전에 플래너 에이전트가 작업을 할당했는지 확인하세요.
    한 명의 에이전트만 선택하세요.
    """

    return SelectorGroupChat(
        participants=agents,
        termination_condition=termination,
        model_client=model_client,
        selector_prompt=selector_prompt,
        # allow_multiple_speaker=True,
    )

def print_section_header(title: str) -> None:
    """섹션 헤더를 출력합니다."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


async def run_team_task(
    team: SelectorGroupChat,
    task: str,
    run_id: int,
    msg_repo: AgentMessageRepository,
) -> None:
    """
    팀에 작업을 할당하고 결과를 스트리밍 방식으로 출력합니다.
    
    Args:
        team: 실행할 팀
        task: 수행할 작업 설명
    """
    print_section_header("SelectorGroupChat 예시 시작")
    print(f"\n질문: {task}\n")
    print("=" * 80)
    
    stream = team.run_stream(task=task)
    
    async for message in stream:
        if hasattr(message, 'source') and hasattr(message, 'content'):
            print(f"\n---------- {message.source} ----------")
            print(message.content)

            msg_repo.add(
                run_id=run_id,
                agent_name=str(message.source),
                role="assistant",  # 필요 시 매핑 로직 적용
                content=str(message.content),
                tool_name=getattr(message, "tool", None),
            )
    
    print_section_header("작업 완료!")


# =============================================================================
# 하위 팀 생성 함수들 (Sub-teams)
# =============================================================================

def create_data_collection_team(model_client: OpenAIChatCompletionClient) -> SelectorGroupChat:
    """
    데이터 수집 팀을 생성합니다.
    
    Args:
        model_client: 사용할 모델 클라이언트
        
    Returns:
        SelectorGroupChat: 데이터 수집 팀
    """
    from src.ai.agents.web_search_agent import create_web_search_agent
    from src.ai.agents.data_analyst_agent import create_data_analyst_agent
    
    agents = [
        create_web_search_agent(model_client),
        create_data_analyst_agent(model_client)
    ]
    
    return create_team(agents, model_client)


def create_analysis_team(model_client: OpenAIChatCompletionClient) -> SelectorGroupChat:
    """
    분석 팀을 생성합니다.
    
    Args:
        model_client: 사용할 모델 클라이언트
        
    Returns:
        SelectorGroupChat: 분석 팀
    """
    from src.ai.agents.analysis_agent import create_analysis_agent
    from src.ai.agents.insight_agent import create_insight_agent
    
    agents = [
        create_analysis_agent(model_client),
        create_insight_agent(model_client)
    ]
    
    return create_team(agents, model_client)


def create_validation_team(model_client: OpenAIChatCompletionClient) -> SelectorGroupChat:
    """
    검증 팀을 생성합니다.
    
    Args:
        model_client: 사용할 모델 클라이언트
        
    Returns:
        SelectorGroupChat: 검증 팀
    """
    from src.ai.agents.analysis_agent import create_devil_advocate_analyst_agent
    from src.ai.agents.summary_agent import create_summary_agent
    
    agents = [
        create_devil_advocate_analyst_agent(model_client),
        create_summary_agent(model_client)
    ]
    
    return create_team(agents, model_client)


# =============================================================================
# 마스터 팀 생성 및 실행 함수들
# =============================================================================

async def run_sub_team_task(
    team: SelectorGroupChat,
    task: str,
    team_name: str,
    run_id: int,
    msg_repo: AgentMessageRepository,
) -> str:
    """
    하위 팀에 작업을 할당하고 결과를 반환합니다.
    
    Args:
        team: 실행할 하위 팀
        task: 수행할 작업 설명
        team_name: 팀 이름
        run_id: 실행 ID
        msg_repo: 메시지 저장소
        
    Returns:
        str: 팀의 최종 결과
    """
    print_section_header(f"{team_name} 작업 시작")
    print(f"\n작업: {task}\n")
    print("=" * 80)
    
    stream = team.run_stream(task=task)
    final_result = ""
    
    async for message in stream:
        if hasattr(message, 'source') and hasattr(message, 'content'):
            print(f"\n---------- {message.source} ----------")
            print(message.content)
            
            # 마지막 메시지를 최종 결과로 저장
            final_result = str(message.content)
            
            msg_repo.add(
                run_id=run_id,
                agent_name=f"{team_name}_{message.source}",
                role="assistant",
                content=str(message.content),
                tool_name=getattr(message, "tool", None),
            )
    
    print_section_header(f"{team_name} 작업 완료!")
    return final_result


async def run_hierarchical_team_task(
    task: str,
    run_id: int,
    msg_repo: AgentMessageRepository,
    model_client: OpenAIChatCompletionClient,
) -> Dict[str, str]:
    """
    계층적 팀 구조로 작업을 실행합니다. (레거시 함수)
    
    새로운 고급 팀 시스템을 사용하려면 run_advanced_hierarchical_task를 사용하세요.
    
    Args:
        task: 수행할 작업 설명
        run_id: 실행 ID
        msg_repo: 메시지 저장소
        model_client: 사용할 모델 클라이언트
        
    Returns:
        Dict[str, str]: 각 팀별 결과
    """
    # 새로운 고급 팀 시스템 사용
    from .advanced_team import run_advanced_hierarchical_task
    
    print("⚠️  레거시 함수 사용 중. 새로운 고급 팀 시스템으로 전환을 권장합니다.")
    
    result = await run_advanced_hierarchical_task(task, run_id, msg_repo, model_client)
    
    # 결과를 기존 형식으로 변환
    return result.results if result.success else {}


async def test_team():
    """
    팀을 독립적으로 테스트하는 함수
    """
    from src.ai.agents.base import create_model_client, print_model_info
    from src.ai.agents.web_search_agent import create_web_search_agent
    from src.ai.agents.data_analyst_agent import create_data_analyst_agent
    from src.core.config import DEFAULT_MODEL
    
    print_section_header("팀 통합 테스트")
    
    # 모델 클라이언트 생성
    model_client = create_model_client()
    
    # 모델 정보 출력
    print_model_info(DEFAULT_MODEL)
    
    # 에이전트 생성
    web_search_agent = create_web_search_agent(model_client)
    data_analyst_agent = create_data_analyst_agent(model_client)
    
    # 팀 생성
    team = create_team([web_search_agent, data_analyst_agent], model_client)
    
    # 테스트 작업
    task = "lg cns 주식 전망은 어떤지 알아봐줘"
    
    await run_team_task(team, task)


async def test_hierarchical_teams():
    """
    계층적 팀 구조를 테스트하는 함수
    """
    from src.ai.agents.base import create_model_client, print_model_info
    from src.core.config import DEFAULT_MODEL
    from src.repositories.agent_logs import AgentMessageRepository
    from src.core.db import init_db, SessionLocal
    
    init_db()
    db = SessionLocal()
    
    try:
        msg_repo = AgentMessageRepository(db)
        run_id = 1  # 테스트용 ID
        
        print_section_header("🏗️ 계층적 팀 구조 테스트")
        
        # 모델 클라이언트 생성
        model_client = create_model_client()
        
        # 모델 정보 출력
        print_model_info(DEFAULT_MODEL)
        
        # 복잡한 테스트 작업
        task = """
        LG CNS의 최근 주식 동향과 전망을 종합적으로 분석해주세요.
        다음 항목들을 포함해주세요:
        1. 최근 주가 동향 및 성과
        2. 재무 상태 분석
        3. 사업 포트폴리오 및 성장 동력
        4. 시장 전망 및 투자 의견
        5. 위험 요소 및 주의사항
        """
        
        # 계층적 팀 작업 실행
        results = await run_hierarchical_team_task(task, run_id, msg_repo, model_client)
        
        print_section_header("📊 최종 결과 요약")
        for team_name, result in results.items():
            print(f"\n**{team_name} 결과**:")
            print("-" * 50)
            print(result[:200] + "..." if len(result) > 200 else result)
            print("-" * 50)
            
    finally:
        # 데이터베이스 연결 정리
        db.close()


if __name__ == "__main__":
    """
    이 파일을 직접 실행하여 팀 기능을 테스트할 수 있습니다.
    
    실행 방법:
        python -m src.ai.orchestrator.team
        
    계층적 팀 구조 테스트:
        python -c "import asyncio; from src.ai.orchestrator.team import test_hierarchical_teams; asyncio.run(test_hierarchical_teams())"
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
    
    # # 기본 팀 테스트
    # print("🔧 기본 팀 테스트를 실행합니다...")
    # asyncio.run(test_team())
    
    print("\n" + "="*100)
    print("🏗️ 계층적 팀 구조 테스트를 실행합니다...")
    print("="*100)
    
    # 계층적 팀 테스트
    asyncio.run(test_hierarchical_teams())


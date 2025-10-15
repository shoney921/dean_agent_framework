"""
멀티 에이전트 팀 관리

여러 에이전트를 조율하여 협업하는 팀을 생성하고 관리합니다.
"""

import asyncio
from typing import List

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.core.config import MAX_MESSAGES
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
    
    return SelectorGroupChat(
        participants=agents,
        termination_condition=termination,
        model_client=model_client,
    )


def print_section_header(title: str) -> None:
    """섹션 헤더를 출력합니다."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


async def run_team_task(team: SelectorGroupChat, task: str, run_id: int, msg_repo: AgentMessageRepository) -> None:
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


if __name__ == "__main__":
    """
    이 파일을 직접 실행하여 팀 기능을 테스트할 수 있습니다.
    
    실행 방법:
        python -m src.ai.orchestrator.team
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
    
    asyncio.run(test_team())


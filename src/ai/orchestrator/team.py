"""
멀티 에이전트 팀 관리

여러 에이전트를 조율하여 협업하는 팀을 생성하고 관리합니다.
"""

import asyncio
import logging
from typing import List

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.core.config import MAX_MESSAGES

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LoggingSelectorGroupChat(SelectorGroupChat):
    """로깅 기능이 강화된 SelectorGroupChat"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_count = 0
        self.agent_usage_count = {}
        
    async def select_speaker(self, messages, *args, **kwargs):
        """에이전트 선택 과정을 로깅하는 오버라이드 메서드"""
        selected_agent = await super().select_speaker(messages, *args, **kwargs)
        
        # 에이전트 사용 횟수 추적
        agent_name = selected_agent.name if hasattr(selected_agent, 'name') else str(selected_agent)
        self.agent_usage_count[agent_name] = self.agent_usage_count.get(agent_name, 0) + 1
        
        # 선택 과정 로깅
        print(f"\n🤖 [에이전트 선택] {agent_name} 선택됨 (총 {self.agent_usage_count[agent_name]}번째 사용)")
        print(f"📊 [사용 통계] {self.agent_usage_count}")
        
        return selected_agent
    
    async def run_stream(self, task: str, **kwargs):
        """스트림 실행 과정을 로깅하는 오버라이드 메서드"""
        print(f"\n🚀 [팀 시작] 작업: '{task}'")
        print(f"👥 [참여 에이전트] {[agent.name for agent in self._participants]}")
        print("-" * 80)
        
        async for message in super().run_stream(task, **kwargs):
            self.message_count += 1
            print(f"\n📝 [메시지 #{self.message_count}]")
            yield message


def create_team(
    agents: List[AssistantAgent],
    model_client: OpenAIChatCompletionClient,
    max_messages: int = MAX_MESSAGES
) -> LoggingSelectorGroupChat:
    """
    멀티 에이전트 팀을 생성합니다.
    
    Args:
        agents: 팀에 참여할 에이전트 리스트
        model_client: 사용할 모델 클라이언트
        max_messages: 최대 메시지 수
        
    Returns:
        LoggingSelectorGroupChat: 설정된 팀 (로깅 기능 포함)
    """
    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(max_messages=max_messages)
    
    return LoggingSelectorGroupChat(
        participants=agents,
        termination_condition=termination,
        model_client=model_client,
    )


def print_section_header(title: str) -> None:
    """섹션 헤더를 출력합니다."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


async def run_team_task(team: LoggingSelectorGroupChat, task: str) -> None:
    """
    팀에 작업을 할당하고 결과를 스트리밍 방식으로 출력합니다.
    
    Args:
        team: 실행할 팀 (로깅 기능 포함)
        task: 수행할 작업 설명
    """
    print_section_header("SelectorGroupChat 예시 시작")
    print(f"\n질문: {task}\n")
    print("=" * 80)
    
    # 팀 실행 시작 시간 기록
    import time
    start_time = time.time()
    
    # 팀에 작업을 실행하고 스트림을 가져옵니다
    stream = team.run_stream(task=task)
    
    async for message in stream:
        if hasattr(message, 'source') and hasattr(message, 'content'):
            print(f"\n---------- {message.source} ----------")
            
            # 메시지 타입 및 길이 정보 추가
            content_preview = message.content[:100] + "..." if len(message.content) > 100 else message.content
            print(f"💬 [메시지 길이: {len(message.content)}자] {content_preview}")
            
            # 함수 호출 정보가 있다면 표시
            if hasattr(message, 'function_calls') and message.function_calls:
                print(f"🔧 [함수 호출] {len(message.function_calls)}개 함수 호출됨")
                for call in message.function_calls:
                    print(f"   - {call.get('name', 'Unknown')}: {call.get('arguments', '')[:50]}...")
            
            # 전체 메시지 내용 출력
            print(message.content)
    
    # 실행 완료 통계
    end_time = time.time()
    execution_time = end_time - start_time
    
    print_section_header("작업 완료!")
    print(f"⏱️  [실행 시간] {execution_time:.2f}초")
    print(f"📊 [총 메시지 수] {team.message_count}개")
    print(f"👥 [에이전트 사용 통계] {team.agent_usage_count}")
    
    # 에이전트별 기여도 분석
    total_usage = sum(team.agent_usage_count.values())
    if total_usage > 0:
        print("\n📈 [에이전트 기여도 분석]")
        for agent_name, count in team.agent_usage_count.items():
            percentage = (count / total_usage) * 100
            print(f"   - {agent_name}: {count}회 ({percentage:.1f}%)")


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


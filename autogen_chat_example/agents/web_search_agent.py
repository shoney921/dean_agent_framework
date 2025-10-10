"""
웹 검색 에이전트

스포츠 통계 및 일반 정보를 웹에서 검색하는 에이전트입니다.
"""

import asyncio
import sys
import os

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from config import WEB_SEARCH_AGENT_SYSTEM_MESSAGE
from tools import search_web_tool

# 직접 실행과 모듈 import 모두 지원
try:
    from .base import create_model_client
except ImportError:
    from agents.base import create_model_client


def create_web_search_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """
    웹 검색 에이전트를 생성합니다.
    
    Args:
        model_client: 사용할 모델 클라이언트
        
    Returns:
        AssistantAgent: 웹 검색 에이전트
    """
    return AssistantAgent(
        "WebSearchAgent",
        description="스포츠 통계에 대한 웹 정보를 검색하는 에이전트입니다.",
        tools=[search_web_tool],
        model_client=model_client,
        system_message=WEB_SEARCH_AGENT_SYSTEM_MESSAGE,
    )


async def test_web_search_agent():
    """
    웹 검색 에이전트를 독립적으로 테스트하는 함수
    """
    print("\n" + "=" * 80)
    print("웹 검색 에이전트 독립 테스트")
    print("=" * 80)
    
    # 모델 클라이언트 생성
    model_client = create_model_client()
    
    # 에이전트 생성
    agent = create_web_search_agent(model_client)
    
    # 테스트 쿼리
    test_query = "lg cns 주식 전망은 어떤지 알아봐줘"
    print(f"\n질문: {test_query}\n")
    print("-" * 80)
    
    # 에이전트 실행
    from autogen_agentchat.messages import TextMessage
    response = await agent.on_messages(
        [TextMessage(content=test_query, source="user")],
        cancellation_token=None
    )
    
    print(f"\n응답:\n{response.chat_message.content}")
    print("\n" + "=" * 80)
    print("테스트 완료!")
    print("=" * 80)


if __name__ == "__main__":
    """
    이 파일을 직접 실행하여 웹 검색 에이전트를 테스트할 수 있습니다.
    
    실행 방법:
        python -m agents.web_search_agent
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
    
    asyncio.run(test_web_search_agent())


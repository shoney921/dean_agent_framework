"""
데이터 분석 에이전트

통계 계산 및 데이터 분석을 수행하는 에이전트입니다.
"""

import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.core.config import DATA_ANALYST_AGENT_SYSTEM_MESSAGE
from src.ai.tools.data_analysis_tool import percentage_change_tool
from src.ai.agents.base import create_model_client


def create_data_analyst_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """
    데이터 분석 에이전트를 생성합니다.
    
    Args:
        model_client: 사용할 모델 클라이언트
        
    Returns:
        AssistantAgent: 데이터 분석 에이전트
    """
    agent = AssistantAgent(
        "DataAnalystAgent",
        description="계산 및 데이터 분석을 수행하는 에이전트입니다.",
        model_client=model_client,
        tools=[percentage_change_tool],
        system_message=DATA_ANALYST_AGENT_SYSTEM_MESSAGE,
    )
    
    # 에이전트 활성화 로깅
    print(f"📊 [DataAnalystAgent 활성화] 분석 도구: {len([percentage_change_tool])}개")
    
    return agent


async def test_data_analyst_agent():
    """
    데이터 분석 에이전트를 독립적으로 테스트하는 함수
    """
    print("\n" + "=" * 80)
    print("데이터 분석 에이전트 독립 테스트")
    print("=" * 80)
    
    # 모델 클라이언트 생성
    model_client = create_model_client()
    
    # 에이전트 생성
    agent = create_data_analyst_agent(model_client)
    
    # 테스트 쿼리
    test_query = "2020년 매출이 1000만원이고 2021년 매출이 1500만원일 때, 퍼센트 변화를 계산해줘"
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
    이 파일을 직접 실행하여 데이터 분석 에이전트를 테스트할 수 있습니다.
    
    실행 방법:
        python -m src.ai.agents.data_analyst_agent
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
    
    asyncio.run(test_data_analyst_agent())


"""
분석 에이전트

정보 분석 및 패턴 식별에 특화된 에이전트입니다.
도구 없이 순수 LLM의 분석 능력을 활용합니다.
"""

import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.core.config import ANALYSIS_AGENT_SYSTEM_MESSAGE, DEVIL_ADVOCATE_SYSTEM_MESSAGE
from src.ai.agents.base import create_model_client


def create_analysis_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """
    분석 에이전트를 생성합니다.
    
    Args:
        model_client: 사용할 모델 클라이언트
        
    Returns:
        AssistantAgent: 분석 에이전트 (도구 없음)
    """
    return AssistantAgent(
        "AnalysisAgent",
        description="정보 분석 및 패턴 식별에 특화된 에이전트입니다.",
        model_client=model_client,
        # 도구 없이 순수 LLM 분석 능력 활용
        system_message=ANALYSIS_AGENT_SYSTEM_MESSAGE,
    )

def create_devil_advocate_analyst_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """
    악마의 대변인 모드로 분석하는 에이전트를 생성합니다.
    
    주어진 정보나 주장에 대해 의도적으로 반대 입장을 취하고 
    비판적인 관점에서 분석합니다.
    
    Args:
        model_client: 사용할 모델 클라이언트
        
    Returns:
        AssistantAgent: 악마의 대변인 분석 에이전트 (도구 없음)
    """
    return AssistantAgent(
        "DevilsAdvocateAnalyst",
        description="악마의 대변인 관점에서 비판적 분석을 수행하는 에이전트입니다. 단순 검색 정보를 요구할때는 사용하지 않아도 됩니다.",
        model_client=model_client,
        system_message=DEVIL_ADVOCATE_SYSTEM_MESSAGE,
    )


async def test_analysis_agent():
    """
    분석 에이전트를 독립적으로 테스트하는 함수
    """
    print("\n" + "=" * 80)
    print("분석 에이전트 독립 테스트")
    print("=" * 80)
    
    # 모델 클라이언트 생성
    model_client = create_model_client()
    
    # 에이전트 생성
    agent = create_analysis_agent(model_client)
    
    # 테스트 쿼리 - 복잡한 데이터 분석 요청
    test_query = """
    다음 매출 데이터를 분석해주세요:
    
    **2023년 분기별 매출 (단위: 백만원)**
    - Q1: 1,200 (전년 동기 대비 +5%)
    - Q2: 1,450 (전년 동기 대비 +12%)
    - Q3: 1,380 (전년 동기 대비 +8%)
    - Q4: 1,680 (전년 동기 대비 +18%)
    
    **2024년 분기별 매출 (단위: 백만원)**
    - Q1: 1,320 (전년 동기 대비 +10%)
    - Q2: 1,595 (전년 동기 대비 +10%)
    - Q3: 1,518 (전년 동기 대비 +10%)
    - Q4: 1,848 (전년 동기 대비 +10%)
    
    이 데이터에서 패턴을 분석하고 트렌드를 파악해주세요.
    """
    
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
    이 파일을 직접 실행하여 분석 에이전트를 테스트할 수 있습니다.
    
    실행 방법:
        python -m src.ai.agents.analysis_agent
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
    
    asyncio.run(test_analysis_agent())

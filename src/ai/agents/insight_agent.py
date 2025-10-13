"""
인사이트 에이전트

비즈니스 데이터에서 전략적 인사이트를 도출하는 에이전트입니다.
도구 없이 순수 LLM의 분석 및 추론 능력을 활용합니다.
"""

import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.core.config import INSIGHT_AGENT_SYSTEM_MESSAGE
from src.ai.agents.base import create_model_client


def create_insight_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """
    인사이트 에이전트를 생성합니다.
    
    Args:
        model_client: 사용할 모델 클라이언트
        
    Returns:
        AssistantAgent: 인사이트 에이전트 (도구 없음)
    """
    agent = AssistantAgent(
        "InsightAgent",
        description="비즈니스 데이터에서 전략적 인사이트를 도출하는 에이전트입니다.",
        model_client=model_client,
        # 도구 없이 순수 LLM 인사이트 도출 능력 활용
        system_message=INSIGHT_AGENT_SYSTEM_MESSAGE,
    )
    
    # 에이전트 활성화 로깅
    print(f"💡 [InsightAgent 활성화] 순수 LLM 인사이트 모드 (도구 없음)")
    
    return agent


async def test_insight_agent():
    """
    인사이트 에이전트를 독립적으로 테스트하는 함수
    """
    print("\n" + "=" * 80)
    print("인사이트 에이전트 독립 테스트")
    print("=" * 80)
    
    # 모델 클라이언트 생성
    model_client = create_model_client()
    
    # 에이전트 생성
    agent = create_insight_agent(model_client)
    
    # 테스트 쿼리 - 비즈니스 인사이트 도출 요청
    test_query = """
    다음 고객 행동 데이터를 분석하여 비즈니스 인사이트를 도출해주세요:
    
    **고객 세그먼트별 분석 (2024년 상반기)**
    
    **세그먼트 A (신규 고객)**
    - 고객 수: 1,200명
    - 평균 주문 금액: 45,000원
    - 재구매율: 23%
    - 고객 생애 가치(LTV): 89,000원
    - 주요 채널: 소셜미디어 광고 (65%), 추천 (25%), 검색 (10%)
    
    **세그먼트 B (기존 고객)**
    - 고객 수: 800명
    - 평균 주문 금액: 78,000원
    - 재구매율: 67%
    - 고객 생애 가치(LTV): 234,000원
    - 주요 채널: 이메일 (40%), 앱 푸시 (35%), 웹사이트 (25%)
    
    **세그먼트 C (VIP 고객)**
    - 고객 수: 150명
    - 평균 주문 금액: 156,000원
    - 재구매율: 89%
    - 고객 생애 가치(LTV): 567,000원
    - 주요 채널: 개인 상담 (50%), 전화 (30%), 앱 (20%)
    
    **추가 컨텍스트:**
    - 전체 매출의 60%가 세그먼트 B와 C에서 발생
    - 세그먼트 A의 이탈률이 45%로 높음
    - 세그먼트 C 고객들이 새로운 제품 출시 시 가장 빠른 반응을 보임
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
    이 파일을 직접 실행하여 인사이트 에이전트를 테스트할 수 있습니다.
    
    실행 방법:
        python -m src.ai.agents.insight_agent
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
    
    asyncio.run(test_insight_agent())

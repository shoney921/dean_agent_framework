"""
요약 에이전트

긴 텍스트와 복잡한 정보를 핵심 포인트로 압축하는 에이전트입니다.
도구 없이 순수 LLM의 요약 능력을 활용합니다.
"""

import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.core.config import SUMMARY_AGENT_SYSTEM_MESSAGE
from src.ai.agents.base import create_model_client


def create_summary_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """
    요약 에이전트를 생성합니다.
    
    Args:
        model_client: 사용할 모델 클라이언트
        
    Returns:
        AssistantAgent: 요약 에이전트 (도구 없음)
    """
    return AssistantAgent(
        "SummaryAgent",
        description="긴 텍스트와 복잡한 정보를 핵심 포인트로 압축하는 에이전트입니다.",
        model_client=model_client,
        # 도구 없이 순수 LLM 요약 능력 활용
        system_message=SUMMARY_AGENT_SYSTEM_MESSAGE,
    )


async def test_summary_agent():
    """
    요약 에이전트를 독립적으로 테스트하는 함수
    """
    print("\n" + "=" * 80)
    print("요약 에이전트 독립 테스트")
    print("=" * 80)
    
    # 모델 클라이언트 생성
    model_client = create_model_client()
    
    # 에이전트 생성
    agent = create_summary_agent(model_client)
    
    # 테스트 쿼리 - 긴 텍스트 요약 요청
    test_query = """
    다음 긴 보고서를 핵심 포인트로 요약해주세요:
    
    **2024년 디지털 마케팅 트렌드 종합 보고서**
    
    디지털 마케팅 분야에서 2024년은 인공지능과 자동화 기술의 본격적인 도입이 이루어진 해로 평가된다. 특히 생성형 AI 기술이 콘텐츠 제작, 개인화 마케팅, 고객 서비스 등 다양한 영역에서 활용되기 시작했다. 
    
    소셜미디어 마케팅에서는 단순한 광고 게시를 넘어서 브랜드와 소비자 간의 진정한 상호작용이 중요해졌다. 인플루언서 마케팅의 경우, 마이크로 인플루언서들의 영향력이 거대 인플루언서들을 넘어서는 현상이 나타났다. 이는 소비자들이 더욱 진정성 있는 추천을 선호하기 때문으로 분석된다.
    
    데이터 프라이버시와 쿠키 정책의 변화로 인해 써드파티 쿠키에 의존하던 타겟팅 방식이 크게 변화했다. 대신 퍼스트파티 데이터와 컨텍스트 타겟팅이 중요한 전략으로 부상했다. 이에 따라 브랜드들은 고객과의 직접적인 관계 구축에 더욱 집중하게 되었다.
    
    비디오 마케팅의 경우, 숏폼 콘텐츠가 여전히 주류를 이루고 있지만, 인터랙티브 비디오와 라이브 스트리밍의 중요성이 증가했다. 특히 실시간 상호작용이 가능한 라이브 커머스는 전자상거래 분야에서 혁신적인 변화를 가져왔다.
    
    마지막으로, 지속가능성과 사회적 가치에 대한 관심이 높아지면서 ESG 마케팅이 중요한 브랜드 차별화 요소로 부상했다. 소비자들은 단순히 제품의 기능과 가격뿐만 아니라 브랜드의 가치관과 사회적 기여도까지 고려하여 구매 결정을 내리는 경향이 강해졌다.
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
    이 파일을 직접 실행하여 요약 에이전트를 테스트할 수 있습니다.
    
    실행 방법:
        python -m src.ai.agents.summary_agent
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
    
    asyncio.run(test_summary_agent())

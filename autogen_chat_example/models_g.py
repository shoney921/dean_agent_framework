from typing import List, Sequence
import asyncio

from autogen_core.models import ModelInfo
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient


# Mock tools - 데모용 도구 함수들
def search_web_tool(query: str) -> str:
    """웹 검색을 시뮬레이션하는 도구"""
    if "2006-2007" in query:
        return """2006-2007 시즌 마이애미 히트 선수들의 총 득점은 다음과 같습니다:
        우도니스 하슬렘: 844점
        드웨인 웨이드: 1397점
        제임스 포지: 550점
        ...
        """
    elif "2007-2008" in query:
        return "마이애미 히트 2007-2008 시즌 드웨인 웨이드의 총 리바운드 수는 214개입니다."
    elif "2008-2009" in query:
        return "마이애미 히트 2008-2009 시즌 드웨인 웨이드의 총 리바운드 수는 398개입니다."
    return "데이터를 찾을 수 없습니다."


def percentage_change_tool(start: float, end: float) -> float:
    """퍼센트 변화를 계산하는 도구"""
    return ((end - start) / start) * 100


async def main() -> None:
    # Gemini 모델 클라이언트 설정
    model_client = OpenAIChatCompletionClient(
        model="gemini-2.5-flash",
        model_info=ModelInfo(
            vision=True, 
            function_calling=True, 
            json_output=True, 
            family="unknown", 
            structured_output=True
        ),
        api_key="AIzaSyAsh2RsHqQxUMiMxEdNv6moXnw-jkAn0NU",
    )
    
    # 사용 가능한 모델 정보 출력
    print("=" * 80)
    print("모델 정보 확인")
    print("=" * 80)
    
    # 일반적으로 사용 가능한 Gemini 모델들
    available_gemini_models = [
        "gemini-1.5-flash",
        "gemini-1.5-pro", 
        "gemini-2.0-flash-exp",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro-002"
    ]
    
    print("📋 일반적으로 사용 가능한 Gemini 모델들:")
    print("-" * 50)
    
    for i, model in enumerate(available_gemini_models, 1):
        status = "✅ 현재 사용 중" if model == "gemini-2.0-flash-lite" else "   "
        print(f"{status} {i}. {model}")
    
    print("-" * 50)
    print(f"현재 사용 중인 모델: gemini-2.0-flash-lite")
    print("💡 다른 모델을 사용하려면 코드에서 model 파라미터를 변경하세요.")
    print("=" * 80)

    # 1. Web Search Agent - 정보를 검색하는 에이전트
    web_search_agent = AssistantAgent(
        "WebSearchAgent",
        description="스포츠 통계에 대한 웹 정보를 검색하는 에이전트입니다.",
        tools=[search_web_tool],
        model_client=model_client,
        system_message="""
        당신은 스포츠 통계를 찾는 데 특화된 웹 검색 에이전트입니다.
        요청된 정보를 찾기 위해 search_web_tool을 사용하세요.
        검색 결과를 제공한 후, 계산이 필요한 경우 DataAnalystAgent에게 문의하세요.
        한 번에 하나의 검색만 수행하세요.
        """,
    )

    # 2. Data Analyst Agent - 데이터를 분석하는 에이전트
    data_analyst_agent = AssistantAgent(
        "DataAnalystAgent",
        description="계산 및 데이터 분석을 수행하는 에이전트입니다.",
        model_client=model_client,
        tools=[percentage_change_tool],
        system_message="""
        당신은 통계적 계산에 특화된 데이터 분석가입니다.
        데이터가 필요할 때는 WebSearchAgent에게 검색을 요청하세요.
        퍼센트 변화를 계산하기 위해 percentage_change_tool을 사용하세요.
        모든 계산을 완료한 후, 최종 요약을 제공하고 "TERMINATE"라고 말하세요.
        """,
    )

    # 종료 조건 설정
    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(max_messages=25)

    # SelectorGroupChat 팀 생성
    team = SelectorGroupChat(
        participants=[web_search_agent, data_analyst_agent],
        termination_condition=termination,
        model_client=model_client,
    )

    # 작업 실행
    print("=" * 80)
    print("SelectorGroupChat 예시 시작")
    print("=" * 80)
    
    task = """2006-2007 시즌에 가장 높은 득점을 기록한 마이애미 히트 선수는 누구였고, 
    그의 2007-2008 시즌과 2008-2009 시즌 간 총 리바운드 수의 퍼센트 변화는 얼마인가요?"""
    
    print(f"\n질문: {task}\n")
    print("=" * 80)
    
    # 스트림 방식으로 실행하여 진행 과정 확인
    stream = team.run_stream(task=task)
    
    async for message in stream:
        if hasattr(message, 'source') and hasattr(message, 'content'):
            print(f"\n---------- {message.source} ----------")
            print(message.content)
    
    print("\n" + "=" * 80)
    print("작업 완료!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
"""
AutoGen 기반 웹 검색 및 데이터 분석 에이전트 시스템

이 모듈은 Gemini 모델을 사용하여 웹 검색과 데이터 분석을 수행하는
멀티 에이전트 시스템을 구현합니다.
"""

import asyncio
import os
from typing import List

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_core.models import ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# ============================================================================
# 상수 정의
# ============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAsh2RsHqQxUMiMxEdNv6moXnw-jkAn0NU")
DEFAULT_MODEL = "gemini-2.5-flash"
MAX_MESSAGES = 25
MAX_SEARCH_RESULTS = 5

AVAILABLE_GEMINI_MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash-exp",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro-002"
]

WEB_SEARCH_AGENT_SYSTEM_MESSAGE = """
당신은 스포츠 통계를 찾는 데 특화된 웹 검색 에이전트입니다.
요청된 정보를 찾기 위해 search_web_tool을 사용하세요.
검색 결과를 제공한 후, 계산이 필요한 경우 DataAnalystAgent에게 문의하세요.
한 번에 하나의 검색만 수행하세요.
"""

DATA_ANALYST_AGENT_SYSTEM_MESSAGE = """
당신은 통계적 계산에 특화된 데이터 분석가입니다.
데이터가 필요할 때는 WebSearchAgent에게 검색을 요청하세요.
퍼센트 변화를 계산하기 위해 percentage_change_tool을 사용하세요.
모든 계산을 완료한 후, 최종 요약을 제공하고 "TERMINATE"라고 말하세요.
"""


# ============================================================================
# 도구 함수 (Tools)
# ============================================================================

def search_web_tool(query: str) -> str:
    """
    Tavily API를 사용하여 실제 웹 검색을 수행하는 도구
    
    Args:
        query (str): 검색할 쿼리 문자열
        
    Returns:
        str: 검색 결과를 포맷팅한 문자열
    """
    try:
        from tavily import TavilyClient
        
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        
        if not tavily_api_key:
            return "❌ TAVILY_API_KEY 환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요."
        
        tavily = TavilyClient(api_key=tavily_api_key)
        response = tavily.search(query, max_results=MAX_SEARCH_RESULTS)
        
        if not response.get('results'):
            return "검색 결과를 찾을 수 없습니다."
        
        formatted_results = []
        for i, result in enumerate(response['results'], 1):
            formatted_results.append(
                f"{i}. {result.get('title', 'No title')}\n"
                f"   출처: {result.get('url', 'No URL')}\n"
                f"   내용: {result.get('content', 'No description')}\n"
            )
        
        return "\n".join(formatted_results)
        
    except ImportError as e:
        return f"필요한 패키지가 설치되지 않았습니다: {str(e)}\n'pip install tavily-python' 을 실행하세요."
    except Exception as e:
        return f"검색 중 오류가 발생했습니다: {str(e)}"


def percentage_change_tool(start: float, end: float) -> float:
    """
    두 값 사이의 퍼센트 변화를 계산하는 도구
    
    Args:
        start (float): 시작 값
        end (float): 종료 값
        
    Returns:
        float: 퍼센트 변화 값
    """
    return ((end - start) / start) * 100


# ============================================================================
# 모델 및 에이전트 설정 함수
# ============================================================================

def create_model_client(model: str = DEFAULT_MODEL, api_key: str = GEMINI_API_KEY) -> OpenAIChatCompletionClient:
    """
    Gemini 모델 클라이언트를 생성합니다.
    
    Args:
        model (str): 사용할 Gemini 모델 이름
        api_key (str): Gemini API 키
        
    Returns:
        OpenAIChatCompletionClient: 설정된 모델 클라이언트
    """
    return OpenAIChatCompletionClient(
        model=model,
        model_info=ModelInfo(
            vision=True,
            function_calling=True,
            json_output=True,
            family="unknown",
            structured_output=True
        ),
        api_key=api_key,
    )


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


def create_data_analyst_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """
    데이터 분석 에이전트를 생성합니다.
    
    Args:
        model_client: 사용할 모델 클라이언트
        
    Returns:
        AssistantAgent: 데이터 분석 에이전트
    """
    return AssistantAgent(
        "DataAnalystAgent",
        description="계산 및 데이터 분석을 수행하는 에이전트입니다.",
        model_client=model_client,
        tools=[percentage_change_tool],
        system_message=DATA_ANALYST_AGENT_SYSTEM_MESSAGE,
    )


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


# ============================================================================
# 유틸리티 함수
# ============================================================================

def print_model_info(current_model: str = DEFAULT_MODEL) -> None:
    """
    사용 가능한 Gemini 모델 정보를 출력합니다.
    
    Args:
        current_model: 현재 사용 중인 모델 이름
    """
    print("=" * 80)
    print("모델 정보 확인")
    print("=" * 80)
    print("📋 일반적으로 사용 가능한 Gemini 모델들:")
    print("-" * 50)
    
    for i, model in enumerate(AVAILABLE_GEMINI_MODELS, 1):
        status = "✅ 현재 사용 중" if model == current_model else "   "
        print(f"{status} {i}. {model}")
    
    print("-" * 50)
    print(f"현재 사용 중인 모델: {current_model}")
    print("💡 다른 모델을 사용하려면 코드에서 DEFAULT_MODEL 상수를 변경하세요.")
    print("=" * 80)


def print_section_header(title: str) -> None:
    """섹션 헤더를 출력합니다."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


async def run_team_task(team: SelectorGroupChat, task: str) -> None:
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
    
    print_section_header("작업 완료!")


# ============================================================================
# 메인 실행 함수
# ============================================================================

async def main() -> None:
    """메인 실행 함수"""
    
    # 1. 모델 클라이언트 생성
    model_client = create_model_client()
    
    # 2. 모델 정보 출력
    print_model_info(DEFAULT_MODEL)
    
    # 3. 에이전트 생성
    web_search_agent = create_web_search_agent(model_client)
    data_analyst_agent = create_data_analyst_agent(model_client)
    
    # 4. 팀 생성
    team = create_team([web_search_agent, data_analyst_agent], model_client)
    
    # 5. 작업 실행
    # task = """2006-2007 시즌에 가장 높은 득점을 기록한 마이애미 히트 선수는 누구였고, 
    # 그의 2007-2008 시즌과 2008-2009 시즌 간 총 리바운드 수의 퍼센트 변화는 얼마인가요?"""
    task = "lg cns 주식 전망은 어떤지 알아봐줘"
    
    await run_team_task(team, task)


if __name__ == "__main__":
    asyncio.run(main())
"""
웹 검색 에이전트

스포츠 통계 및 일반 정보를 웹에서 검색하는 에이전트입니다.
"""

import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.core.config import WEB_SEARCH_AGENT_SYSTEM_MESSAGE
from src.ai.tools.web_search_tool import search_web_tool
from src.ai.agents.base import create_model_client


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
        description="웹 정보를 검색하는 에이전트입니다.",
        handoffs=["GoogleSearchAgent"],
        tools=[search_web_tool],
        model_client=model_client,
        system_message=WEB_SEARCH_AGENT_SYSTEM_MESSAGE,
    )

def google_search(query: str, num_results: int = 2, max_chars: int = 500) -> list:  # type: ignore[type-arg]
    import os
    import time

    import requests
    from bs4 import BeautifulSoup
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        raise ValueError("API key or Search Engine ID not found in environment variables")

    url = "https://customsearch.googleapis.com/customsearch/v1"
    params = {"key": str(api_key), "cx": str(search_engine_id), "q": str(query), "num": str(num_results)}

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(response.json())
        raise Exception(f"Error in API request: {response.status_code}")

    results = response.json().get("items", [])

    def get_page_content(url: str) -> str:
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            words = text.split()
            content = ""
            for word in words:
                if len(content) + len(word) + 1 > max_chars:
                    break
                content += " " + word
            return content.strip()
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return ""

    enriched_results = []
    for item in results:
        body = get_page_content(item["link"])
        enriched_results.append(
            {"title": item["title"], "link": item["link"], "snippet": item["snippet"], "body": body}
        )
        time.sleep(1)  # Be respectful to the servers

    return enriched_results

def create_google_search_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """
    Google 검색 에이전트를 생성합니다.
    
    Args:
        model_client: 사용할 모델 클라이언트
        
    Returns:
        AssistantAgent: Google 검색 에이전트
    """
    google_search_tool = FunctionTool(
        google_search,
        description="Google에서 정보를 검색하고, 스니펫과 본문 내용이 포함된 결과를 반환합니다",
        name="google_search"
    )
    return AssistantAgent(
        "GoogleSearchAgent",
        description="Google 검색 에이전트입니다.",
        handoffs=["WebSearchAgent"],
        tools=[google_search_tool],
        model_client=model_client,
        system_message="You are a helpful AI assistant. Solve tasks using your tools. You can use the WebSearchAgent to search the web for information.",
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
        python -m src.ai.agents.web_search_agent
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


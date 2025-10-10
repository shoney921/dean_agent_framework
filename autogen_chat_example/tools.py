"""
AutoGen 에이전트가 사용하는 도구 함수들

이 모듈은 웹 검색, 데이터 분석 등에 사용되는 도구 함수들을 제공합니다.
"""

import os
from tavily import TavilyClient
from config import MAX_SEARCH_RESULTS, TAVILY_API_KEY


def search_web_tool(query: str) -> str:
    """
    Tavily API를 사용하여 실제 웹 검색을 수행하는 도구
    
    Args:
        query (str): 검색할 쿼리 문자열
        
    Returns:
        str: 검색 결과를 포맷팅한 문자열
    """
    try:
        tavily = TavilyClient(api_key=TAVILY_API_KEY)
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


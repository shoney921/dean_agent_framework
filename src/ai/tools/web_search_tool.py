"""
웹 검색 도구

Tavily API를 사용하여 웹 검색을 수행하는 도구입니다.
"""

import logging
from tavily import TavilyClient
from src.core.config import MAX_SEARCH_RESULTS, TAVILY_API_KEY

# 로거 설정
logger = logging.getLogger(__name__)


def search_web_tool(query: str) -> str:
    """
    Tavily API를 사용하여 실제 웹 검색을 수행하는 도구
    
    Args:
        query (str): 검색할 쿼리 문자열
        
    Returns:
        str: 검색 결과를 포맷팅한 문자열
    """
    # 검색 시도 로깅
    print(f"\n🔍 [웹 검색 시도] 검색 쿼리: '{query}'")
    logger.info(f"웹 검색 시도 - 쿼리: {query}")
    
    try:
        tavily = TavilyClient(api_key=TAVILY_API_KEY)
        response = tavily.search(query, max_results=MAX_SEARCH_RESULTS)
        
        if not response.get('results'):
            print(f"❌ [검색 실패] 검색 결과를 찾을 수 없습니다.")
            logger.warning(f"검색 결과 없음 - 쿼리: {query}")
            return "검색 결과를 찾을 수 없습니다."
        
        formatted_results = []
        for i, result in enumerate(response['results'], 1):
            formatted_results.append(
                f"{i}. {result.get('title', 'No title')}\n"
                f"   출처: {result.get('url', 'No URL')}\n"
                f"   내용: {result.get('content', 'No description')}\n"
            )
        
        print(f"✅ [검색 성공] {len(response['results'])}개의 결과를 찾았습니다.")
        logger.info(f"검색 성공 - 쿼리: {query}, 결과 수: {len(response['results'])}")
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        error_msg = f"검색 중 오류가 발생했습니다: {str(e)}"
        print(f"❌ [검색 오류] {error_msg}")
        logger.error(f"검색 오류 - 쿼리: {query}, 오류: {str(e)}")
        return error_msg


"""
데이터 분석 도구

통계 계산 및 데이터 분석을 위한 도구들입니다.
"""

import logging

# 로거 설정
logger = logging.getLogger(__name__)


def percentage_change_tool(start: float, end: float) -> float:
    """
    두 값 사이의 퍼센트 변화를 계산하는 도구
    
    Args:
        start (float): 시작 값
        end (float): 종료 값
        
    Returns:
        float: 퍼센트 변화 값
    """
    # 계산 시도 로깅
    print(f"\n📊 [퍼센트 변화 계산] 시작 값: {start}, 종료 값: {end}")
    logger.info(f"퍼센트 변화 계산 시도 - 시작: {start}, 종료: {end}")
    
    try:
        result = ((end - start) / start) * 100
        print(f"✅ [계산 완료] 퍼센트 변화: {result:.2f}%")
        logger.info(f"퍼센트 변화 계산 완료 - 결과: {result}%")
        return result
    except Exception as e:
        error_msg = f"계산 중 오류 발생: {str(e)}"
        print(f"❌ [계산 오류] {error_msg}")
        logger.error(f"퍼센트 변화 계산 오류 - 시작: {start}, 종료: {end}, 오류: {str(e)}")
        raise


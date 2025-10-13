"""
AutoGen 기반 웹 검색 및 데이터 분석 에이전트 시스템 - 메인 실행 파일

이 모듈은 Gemini 모델을 사용하여 웹 검색과 데이터 분석을 수행하는
멀티 에이전트 시스템을 실행합니다.
"""

import asyncio
import urllib3
import requests

from src.ai.agents.base import create_model_client, print_model_info
from src.ai.agents.web_search_agent import create_web_search_agent
from src.ai.agents.data_analyst_agent import create_data_analyst_agent
from src.ai.agents.analysis_agent import create_analysis_agent
from src.ai.agents.summary_agent import create_summary_agent
from src.ai.agents.insight_agent import create_insight_agent
from src.ai.orchestrator.team import create_team, run_team_task
from src.core.config import DEFAULT_MODEL

# ============================================================================
# 전역 SSL 검증 비활성화 설정
# ============================================================================
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# requests 라이브러리의 모든 요청에 verify=False 자동 적용
_original_request = requests.Session.request
def _patched_request(self, *args, **kwargs):
    """모든 requests 요청에 자동으로 verify=False를 적용"""
    kwargs['verify'] = False
    return _original_request(self, *args, **kwargs)
requests.Session.request = _patched_request


async def main() -> None:
    """메인 실행 함수"""
    
    # 1. 모델 클라이언트 생성
    model_client = create_model_client()
    
    # 2. 모델 정보 출력
    print_model_info(DEFAULT_MODEL)
    
    # 3. 에이전트 생성
    print("\n🤖 [에이전트 생성 시작]")
    print("-" * 50)
    
    web_search_agent = create_web_search_agent(model_client)
    data_analyst_agent = create_data_analyst_agent(model_client)
    analysis_agent = create_analysis_agent(model_client)
    insight_agent = create_insight_agent(model_client)
    
    agents = [web_search_agent, data_analyst_agent, analysis_agent, insight_agent]
    print(f"✅ [에이전트 생성 완료] 총 {len(agents)}개 에이전트 준비됨")
    
    # 4. 팀 생성
    print("\n👥 [팀 생성]")
    print("-" * 50)
    team = create_team(agents, model_client)
    print(f"✅ [팀 생성 완료] {len(agents)}개 에이전트로 구성된 팀 준비됨")
    
    # 5. 작업 실행
    # task = """2006-2007 시즌에 가장 높은 득점을 기록한 마이애미 히트 선수는 누구였고, 
    # 그의 2007-2008 시즌과 2008-2009 시즌 간 총 리바운드 수의 퍼센트 변화는 얼마인가요?"""
    task = "lg cns 주식 전망은 어떤지 알아봐줘"
    
    await run_team_task(team, task)


if __name__ == "__main__":
    asyncio.run(main())


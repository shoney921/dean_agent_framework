"""
AutoGen 기반 웹 검색 및 데이터 분석 에이전트 시스템 - 메인 실행 파일

이 모듈은 Gemini 모델을 사용하여 웹 검색과 데이터 분석을 수행하는
멀티 에이전트 시스템을 실행합니다.
"""

import asyncio
import urllib3
import requests

from src.ai.agents.base import create_model_client, print_model_info
from src.ai.agents.web_search_agent import create_web_search_agent, create_google_search_agent
from src.ai.agents.data_analyst_agent import create_data_analyst_agent
from src.ai.agents.analysis_agent import create_analysis_agent, create_devil_advocate_analyst_agent
from src.ai.agents.summary_agent import create_summary_agent
from src.ai.agents.insight_agent import create_insight_agent
from src.ai.orchestrator.team import create_team, run_team_task
from src.core.config import DEFAULT_MODEL
from src.core.db import init_db, SessionLocal
from src.repositories.agent_logs import AgentRunRepository, AgentMessageRepository

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
    
    # 0. DB 초기화
    init_db()
    db = SessionLocal()
    run_repo = AgentRunRepository(db)
    msg_repo = AgentMessageRepository(db)

    # 1. 모델 클라이언트 생성
    model_client = create_model_client()
    
    # 2. 모델 정보 출력
    print_model_info(DEFAULT_MODEL)
    
    # 3. 에이전트 생성
    web_search_agent = create_web_search_agent(model_client)
    google_search_agent = create_google_search_agent(model_client)
    data_analyst_agent = create_data_analyst_agent(model_client)
    analysis_agent = create_analysis_agent(model_client)
    insight_agent = create_insight_agent(model_client)
    devil_advocate_analyst_agent = create_devil_advocate_analyst_agent(model_client)
    
    # 4. 팀 생성
    team = create_team([web_search_agent, google_search_agent, data_analyst_agent, analysis_agent, insight_agent, devil_advocate_analyst_agent], model_client)
    
    # 5. 작업 실행
    # task = """2006-2007 시즌에 가장 높은 득점을 기록한 마이애미 히트 선수는 누구였고, 
    # 그의 2007-2008 시즌과 2008-2009 시즌 간 총 리바운드 수의 퍼센트 변화는 얼마인가요?"""
    task = "jtbc 마라톤에 대해서 설명해줘"
    
    # 실행 기록 시작
    run = run_repo.create(team_name="SelectorGroupChat", task=task, model=DEFAULT_MODEL)

    # 팀 태스크 실행
    await run_team_task(team, task, run.id, msg_repo)

    # 간단 예시: 종료 상태만 업데이트 (상세 메시지 저장은 오케스트레이터에 연결 권장)
    run_repo.finish(run.id, status="completed")


if __name__ == "__main__":
    asyncio.run(main())


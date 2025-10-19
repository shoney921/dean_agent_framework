import streamlit as st
from datetime import datetime, timedelta
import sys
import os
import urllib.parse

# 프로젝트 루트 경로를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.append(project_root)

from frontend.streamlit_app.services.api import BackendAPIClient


def main():
    """실행 로그 목록 페이지"""
    
    # 페이지 설정
    st.set_page_config(
        page_title="실행 로그 - Dean Agent Framework",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    
    st.title("📋 실행 로그 목록")
    st.markdown("---")
    
    # API 클라이언트 초기화
    try:
        client = BackendAPIClient()
    except Exception as e:
        st.error(f"API 클라이언트 초기화 실패: {str(e)}")
        return
    
    # 필터 옵션
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        team_filter = st.selectbox(
            "팀 필터",
            ["전체"] + get_team_list(client),
            index=0
        )
    
    with col2:
        status_filter = st.selectbox(
            "상태 필터",
            ["전체", "running", "completed", "failed"],
            index=0
        )
    
    with col3:
        limit = st.number_input("조회 개수", min_value=10, max_value=1000, value=50)
    
    # 실행 목록 조회
    try:
        # 필터 파라미터 설정
        params = {"limit": limit}
        if team_filter != "전체":
            params["team_name"] = team_filter
        
        runs = client.list_runs(**params)
        
        if not runs:
            st.info("실행 기록이 없습니다.")
            return
        
        # 상태 필터 적용
        if status_filter != "전체":
            runs = [run for run in runs if run.get('status') == status_filter]
        
        if not runs:
            st.info(f"'{status_filter}' 상태의 실행 기록이 없습니다.")
            return
        
        # 실행 목록을 카드 형태로 표시
        st.subheader(f"📊 실행 목록 ({len(runs)}개)")
        
        for i, run in enumerate(runs):
            show_run_card(run, i)
        
    except Exception as e:
        st.error(f"실행 기록 조회 실패: {str(e)}")


def show_run_card(run: dict, index: int):
    """개별 실행 기록을 카드 형태로 표시"""
    
    run_id = run.get('id', 'N/A')
    team_name = run.get('team_name', 'N/A')
    task = run.get('task', '작업 내용이 없습니다.')
    status = run.get('status', 'N/A')
    model = run.get('model', 'N/A')
    started_at = run.get('started_at', 'N/A')
    ended_at = run.get('ended_at', 'N/A')
    
    # 상태에 따른 색상 설정
    status_color = {
        'running': '🟡',
        'completed': '🟢', 
        'failed': '🔴'
    }.get(status, '⚪')
    
    # 실행 시간 계산
    duration = calculate_duration(started_at, ended_at)
    
    # 카드 컨테이너
    with st.container():
        # 카드 헤더
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"### 🆔 {run_id}")
        
        with col2:
            st.markdown(f"**{status_color} {status.upper()}**")
        
        # 카드 내용
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # 작업 내용 (간략하게)
            task_preview = task[:100] + "..." if len(task) > 100 else task
            st.markdown(f"**📝 작업**: {task_preview}")
        
        with col2:
            st.markdown(f"**🏢 팀**: {team_name}")
            st.markdown(f"**🤖 모델**: {model}")
        
        with col3:
            st.markdown(f"**⏱️ 시간**: {duration}")
            if started_at != 'N/A':
                try:
                    start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                    formatted_time = start_time.strftime("%m/%d %H:%M")
                    st.markdown(f"**📅 시작**: {formatted_time}")
                except:
                    st.markdown(f"**📅 시작**: {started_at}")
        
        # 상세 보기 버튼
        if st.button(f"🔍 상세 보기", key=f"detail_btn_{run_id}"):
            # 세션 상태에 run_id 저장 후 상세 페이지로 이동
            st.session_state.selected_run_id = run_id
            st.switch_page("pages/_run_detail.py")
        
        st.markdown("---")


def get_team_list(client: BackendAPIClient) -> list:
    """팀 목록 조회"""
    try:
        runs = client.list_runs(limit=1000)
        teams = list(set(run.get('team_name') for run in runs if run.get('team_name')))
        return sorted(teams)
    except:
        return []


def calculate_duration(started_at: str, ended_at: str) -> str:
    """실행 시간 계산"""
    if not started_at:
        return "N/A"
    
    try:
        start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
        
        if ended_at:
            end_time = datetime.fromisoformat(ended_at.replace('Z', '+00:00'))
            duration = end_time - start_time
            
            # 시간, 분, 초로 변환
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            if hours > 0:
                return f"{hours}시간 {minutes}분 {seconds}초"
            elif minutes > 0:
                return f"{minutes}분 {seconds}초"
            else:
                return f"{seconds}초"
        else:
            return "진행 중"
            
    except Exception as e:
        return f"오류: {str(e)}"


if __name__ == "__main__":
    main()

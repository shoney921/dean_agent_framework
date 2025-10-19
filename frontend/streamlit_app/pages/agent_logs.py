import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import sys
import os

# 프로젝트 루트 경로를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.append(project_root)

from frontend.streamlit_app.services.api import BackendAPIClient


def main():
    """실행 로그 및 메시지 페이지"""
    
    # 페이지 설정
    st.set_page_config(
        page_title="실행 로그 - Dean Agent Framework",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📋 실행 로그 및 메시지")
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
        
        # 실행 목록 표시
        st.subheader(f"📊 실행 목록 ({len(runs)}개)")
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(runs)
        
        # 컬럼 선택 및 표시
        display_columns = ['id', 'team_name', 'task', 'status', 'model', 'started_at', 'ended_at']
        available_columns = [col for col in display_columns if col in df.columns]
        
        # 실행 기록 테이블
        selected_runs = st.dataframe(
            df[available_columns],
            use_container_width=True,
            hide_index=True,
            selection_mode="single-row"
        )
        
        # 선택된 실행의 상세 정보 표시
        if selected_runs.selection.rows:
            selected_index = selected_runs.selection.rows[0]
            selected_run = runs[selected_index]
            show_run_details(client, selected_run)
        
    except Exception as e:
        st.error(f"실행 기록 조회 실패: {str(e)}")


def show_run_details(client: BackendAPIClient, run_data: dict):
    """선택된 실행의 상세 정보 및 메시지 표시"""
    
    st.markdown("---")
    st.subheader(f"🔍 실행 상세 정보 (ID: {run_data.get('id', 'N/A')})")
    
    # 실행 기본 정보
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("팀명", run_data.get('team_name', 'N/A'))
    
    with col2:
        status = run_data.get('status', 'N/A')
        status_color = {
            'running': '🟡',
            'completed': '🟢', 
            'failed': '🔴'
        }.get(status, '⚪')
        st.metric("상태", f"{status_color} {status}")
    
    with col3:
        st.metric("모델", run_data.get('model', 'N/A'))
    
    with col4:
        duration = calculate_duration(
            run_data.get('started_at'),
            run_data.get('ended_at')
        )
        st.metric("실행 시간", duration)
    
    # 작업 내용
    st.markdown("### 📝 작업 내용")
    task = run_data.get('task', '작업 내용이 없습니다.')
    st.text_area("", value=task, height=100, disabled=True)
    
    # 시간 정보
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⏰ 시작 시간")
        started_at = run_data.get('started_at', 'N/A')
        st.text(started_at)
    
    with col2:
        st.markdown("### ⏰ 종료 시간")
        ended_at = run_data.get('ended_at', 'N/A')
        st.text(ended_at)
    
    # 메시지 목록
    st.markdown("### 💬 메시지 목록")
    
    try:
        run_id = run_data.get('id')
        if run_id:
            messages = client.list_messages_by_run(run_id)
            
            if messages:
                # 메시지 그룹화 (에이전트별)
                agent_messages = {}
                for msg in messages:
                    agent_name = msg.get('agent_name', 'Unknown')
                    if agent_name not in agent_messages:
                        agent_messages[agent_name] = []
                    agent_messages[agent_name].append(msg)
                
                # 에이전트별로 메시지 표시
                for agent_name, msgs in agent_messages.items():
                    with st.expander(f"🤖 {agent_name} ({len(msgs)}개 메시지)", expanded=False):
                        for i, msg in enumerate(msgs):
                            show_message_details(msg, i)
            else:
                st.info("메시지가 없습니다.")
        else:
            st.warning("실행 ID가 없어 메시지를 조회할 수 없습니다.")
            
    except Exception as e:
        st.error(f"메시지 조회 실패: {str(e)}")


def show_message_details(msg: dict, index: int):
    """개별 메시지 상세 정보 표시"""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        role = msg.get('role', 'unknown')
        role_emoji = {
            'user': '👤',
            'assistant': '🤖',
            'system': '⚙️',
            'tool': '🛠️'
        }.get(role, '❓')
        
        st.markdown(f"**{role_emoji} {role.upper()}**")
        
        content = msg.get('content', '내용 없음')
        if len(content) > 500:
            content = content[:500] + "..."
        st.text_area("", value=content, height=100, disabled=True, key=f"msg_{index}")
    
    with col2:
        # 메시지 메타데이터
        st.markdown("**메타데이터**")
        
        tool_name = msg.get('tool_name')
        if tool_name:
            st.markdown(f"🛠️ **도구**: {tool_name}")
        
        created_at = msg.get('created_at', 'N/A')
        st.markdown(f"⏰ **시간**: {created_at}")
        
        msg_id = msg.get('id', 'N/A')
        st.markdown(f"🆔 **ID**: {msg_id}")
    
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

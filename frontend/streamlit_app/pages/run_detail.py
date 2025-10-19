import streamlit as st
from datetime import datetime, timedelta
import sys
import os

# 프로젝트 루트 경로를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.append(project_root)

from frontend.streamlit_app.services.api import BackendAPIClient


def main():
    """실행 상세 정보 페이지"""
    
    # 페이지 설정
    st.set_page_config(
        page_title="실행 상세 - Dean Agent Framework",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 세션 상태에서 run_id 가져오기
    run_id = st.session_state.get('selected_run_id')
    
    # 디버깅 정보 표시
    with st.expander("🔧 디버깅 정보", expanded=False):
        st.write(f"세션 상태: {dict(st.session_state)}")
        st.write(f"run_id: {run_id}")
    
    if not run_id:
        st.error("실행 ID가 없습니다. 목록에서 실행을 선택해주세요.")
        if st.button("🔙 목록으로 돌아가기"):
            st.switch_page("pages/agent_logs.py")
        return
    
    st.title(f"🔍 실행 상세 정보")
    
    # 뒤로가기 버튼
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔙 목록으로 돌아가기"):
            # 세션 상태 정리 후 목록으로 이동
            if 'selected_run_id' in st.session_state:
                del st.session_state.selected_run_id
            st.switch_page("pages/agent_logs.py")
    with col2:
        st.markdown(f"**실행 ID**: {run_id}")
    
    st.markdown("---")
    
    # API 클라이언트 초기화
    try:
        client = BackendAPIClient()
    except Exception as e:
        st.error(f"API 클라이언트 초기화 실패: {str(e)}")
        return
    
    # 실행 상세 정보 조회
    try:
        # 실행 정보 조회
        run_data = get_run_by_id(client, run_id)
        
        if not run_data:
            st.error(f"실행 ID '{run_id}'에 해당하는 데이터를 찾을 수 없습니다.")
            return
        
        # 실행 기본 정보 표시
        show_run_overview(run_data)
        
        # 메시지 목록 표시
        show_messages(client, run_id)
        
    except Exception as e:
        st.error(f"실행 상세 정보 조회 실패: {str(e)}")


def get_run_by_id(client: BackendAPIClient, run_id: str):
    """특정 실행 ID로 실행 정보 조회"""
    try:
        runs = client.list_runs(limit=1000)
        for run in runs:
            if run.get('id') == run_id:
                return run
        return None
    except Exception as e:
        st.error(f"실행 정보 조회 실패: {str(e)}")
        return None


def show_run_overview(run_data: dict):
    """실행 개요 정보 표시"""
    
    st.subheader("📊 실행 개요")
    
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
    st.text_area("", value=task, height=150, disabled=True, key="task_content")
    
    # 시간 정보
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⏰ 시작 시간")
        started_at = run_data.get('started_at', 'N/A')
        if started_at != 'N/A':
            try:
                start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                formatted_start = start_time.strftime("%Y-%m-%d %H:%M:%S")
                st.text(formatted_start)
            except:
                st.text(started_at)
        else:
            st.text(started_at)
    
    with col2:
        st.markdown("### ⏰ 종료 시간")
        ended_at = run_data.get('ended_at', 'N/A')
        if ended_at != 'N/A':
            try:
                end_time = datetime.fromisoformat(ended_at.replace('Z', '+00:00'))
                formatted_end = end_time.strftime("%Y-%m-%d %H:%M:%S")
                st.text(formatted_end)
            except:
                st.text(ended_at)
        else:
            st.text(ended_at)


def show_messages(client: BackendAPIClient, run_id: str):
    """메시지 목록 표시"""
    
    st.markdown("### 💬 메시지 목록")
    
    try:
        messages = client.list_messages_by_run(run_id)
        
        if not messages:
            st.info("메시지가 없습니다.")
            return
        
        # 메시지 그룹화 (에이전트별)
        agent_messages = {}
        for msg in messages:
            agent_name = msg.get('agent_name', 'Unknown')
            if agent_name not in agent_messages:
                agent_messages[agent_name] = []
            agent_messages[agent_name].append(msg)
        
        # 에이전트별로 메시지 표시
        for agent_name, msgs in agent_messages.items():
            with st.expander(f"🤖 {agent_name} ({len(msgs)}개 메시지)", expanded=True):
                for i, msg in enumerate(msgs):
                    show_message_details(msg, i, agent_name)
                    
    except Exception as e:
        st.error(f"메시지 조회 실패: {str(e)}")


def show_message_details(msg: dict, index: int, agent_name: str):
    """개별 메시지 상세 정보 표시"""
    
    # 메시지 ID와 에이전트명을 조합해서 고유한 key 생성
    msg_id = msg.get('id', f'msg_{index}')
    unique_key_prefix = f"{agent_name}_{msg_id}_{index}"
    
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
        if len(content) > 1000:
            # 긴 내용의 경우 접기/펼치기 기능 추가
            if st.checkbox("전체 내용 보기", key=f"expand_{unique_key_prefix}"):
                st.text_area("", value=content, height=200, disabled=True, key=f"msg_full_{unique_key_prefix}")
            else:
                preview = content[:500] + "..."
                st.text_area("", value=preview, height=100, disabled=True, key=f"msg_preview_{unique_key_prefix}")
        else:
            st.text_area("", value=content, height=100, disabled=True, key=f"msg_{unique_key_prefix}")
    
    with col2:
        # 메시지 메타데이터
        st.markdown("**메타데이터**")
        
        tool_name = msg.get('tool_name')
        if tool_name:
            st.markdown(f"🛠️ **도구**: {tool_name}")
        
        created_at = msg.get('created_at', 'N/A')
        if created_at != 'N/A':
            try:
                msg_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                formatted_time = msg_time.strftime("%m/%d %H:%M:%S")
                st.markdown(f"⏰ **시간**: {formatted_time}")
            except:
                st.markdown(f"⏰ **시간**: {created_at}")
        else:
            st.markdown(f"⏰ **시간**: {created_at}")
        
        msg_id = msg.get('id', 'N/A')
        st.markdown(f"🆔 **ID**: {msg_id}")
    
    st.markdown("---")


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

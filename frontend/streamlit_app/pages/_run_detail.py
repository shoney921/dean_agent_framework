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
        st.markdown("<div style='font-size: 0.8em'>", unsafe_allow_html=True)
        st.metric("팀명", run_data.get('team_name', 'N/A'))
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        status = run_data.get('status', 'N/A')
        status_color = {
            'running': '🟡',
            'completed': '🟢', 
            'failed': '🔴'
        }.get(status, '⚪')
        st.markdown("<div style='font-size: 0.8em'>", unsafe_allow_html=True)
        st.metric("상태", f"{status_color} {status}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div style='font-size: 0.8em'>", unsafe_allow_html=True)
        st.metric("모델", run_data.get('model', 'N/A'))
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        duration = calculate_duration(
            run_data.get('started_at'),
            run_data.get('ended_at')
        )
        st.markdown("<div style='font-size: 0.8em'>", unsafe_allow_html=True)
        st.metric("실행 시간", duration)
        st.markdown("</div>", unsafe_allow_html=True)
    
    
    # 시간 정보
    col1, col2 = st.columns(2)
    
    with col1:
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
    """메시지 목록을 대화 형태로 표시"""
    
    st.markdown("### 💬 대화 내용")
    
    try:
        messages = client.list_messages_by_run(run_id)
        
        if not messages:
            st.info("메시지가 없습니다.")
            return
        
        # 메시지를 시간순으로 정렬
        messages.sort(key=lambda x: x.get('created_at', ''))
        
        # 대화 컨테이너 생성
        chat_container = st.container()
        
        with chat_container:
            for i, msg in enumerate(messages):
                show_chat_message(msg, i)
                    
    except Exception as e:
        st.error(f"메시지 조회 실패: {str(e)}")


def show_chat_message(msg: dict, index: int):
    """대화 형태로 메시지 표시"""
    
    role = msg.get('role', 'unknown')
    agent_name = msg.get('agent_name', 'Unknown')
    content = msg.get('content', '내용 없음')
    tool_name = msg.get('tool_name')
    created_at = msg.get('created_at', 'N/A')
    
    # 메시지 ID와 인덱스를 조합해서 고유한 key 생성
    msg_id = msg.get('id', f'msg_{index}')
    unique_key_prefix = f"{agent_name}_{msg_id}_{index}"
    
    # 역할에 따른 스타일링
    if role == 'user':
        # 사용자 메시지는 오른쪽 정렬
        with st.chat_message("user"):
            st.markdown(f"**👤 사용자**")
            st.markdown(content)
    elif role == 'assistant':
        # AI 에이전트 메시지는 왼쪽 정렬
        with st.chat_message("assistant"):
            st.markdown(f"**🤖 {agent_name}**")
            
            # 스크립트나 코드가 포함된 경우 실행 가능하게 표시
            if is_script_content(content):
                st.markdown("**📝 스크립트 내용:**")
                st.code(content, language="python")
                
                # 스크립트 실행 버튼 (실제 실행은 하지 않고 표시만)
                if st.button(f"스크립트 실행 (시뮬레이션)", key=f"run_script_{unique_key_prefix}"):
                    st.success("스크립트가 실행되었습니다! (시뮬레이션)")
            else:
                st.markdown(content)
    elif role == 'system':
        # 시스템 메시지는 중앙에 작게 표시
        st.markdown(f"<div style='text-align: center; color: #666; font-size: 0.9em; margin: 10px 0;'>⚙️ 시스템: {content}</div>", unsafe_allow_html=True)
    elif role == 'tool':
        # 도구 메시지는 특별한 스타일로 표시
        with st.chat_message("assistant"):
            st.markdown(f"**🛠️ {tool_name or '도구'}**")
            st.markdown(content)
    
    # 메시지 메타데이터 (작게 표시)
    if created_at != 'N/A':
        try:
            msg_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            formatted_time = msg_time.strftime("%H:%M:%S")
            st.caption(f"⏰ {formatted_time} | 🆔 {msg_id}")
        except:
            st.caption(f"⏰ {created_at} | 🆔 {msg_id}")
    
    st.markdown("---")


def is_script_content(content: str) -> bool:
    """내용이 스크립트인지 판단"""
    if not content:
        return False
    
    # Python 스크립트 패턴 감지
    script_indicators = [
        'import ', 'from ', 'def ', 'class ', 'if __name__',
        'print(', 'return ', 'for ', 'while ', 'try:',
        'except:', 'finally:', 'with ', 'as ', 'lambda'
    ]
    
    content_lower = content.lower()
    script_count = sum(1 for indicator in script_indicators if indicator in content_lower)
    
    # 스크립트 지시어가 2개 이상 있으면 스크립트로 판단
    return script_count >= 2


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

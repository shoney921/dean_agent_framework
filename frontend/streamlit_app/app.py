"""
Agent Framework Streamlit 메인 애플리케이션
"""

import streamlit as st
from services.api import BackendAPIClient
from pages.dashboard import show_dashboard
from pages.agent_logs import show_agent_logs
from pages.notion_management import show_notion_management


def init_state() -> None:
    """세션 상태를 초기화합니다."""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"
    if "selected_run_id" not in st.session_state:
        st.session_state.selected_run_id = None
    if "selected_pages" not in st.session_state:
        st.session_state.selected_pages = []


def main() -> None:
    """메인 애플리케이션 함수"""
    st.set_page_config(page_title="Agent Framework Dashboard", layout="wide")

    init_state()
    api = BackendAPIClient()

    # 사이드바 네비게이션
    st.sidebar.title("Menu")
    
    # 페이지 선택 라디오 버튼
    page_options = ["🏠 대시보드", "📝 Agent 로그", "📋 Notion 관리"]
    current_display = st.session_state.get("current_page_display", "🏠 대시보드")
    
    try:
        current_index = page_options.index(current_display)
    except ValueError:
        current_index = 0
        current_display = page_options[0]
    
    page = st.sidebar.radio(
        "페이지 선택",
        page_options,
        index=current_index,
        label_visibility="collapsed"
    )
    
    # 페이지 상태 업데이트
    if page != current_display:
        if page == "🏠 대시보드":
            st.session_state.current_page = "dashboard"
        elif page == "📝 Agent 로그":
            st.session_state.current_page = "agent_logs"
        elif page == "📋 Notion 관리":
            st.session_state.current_page = "notion_management"
        st.session_state.current_page_display = page
        st.rerun()
    
    # 페이지별 라우팅
    if st.session_state.current_page == "dashboard":
        show_dashboard(api)
    elif st.session_state.current_page == "agent_logs":
        show_agent_logs(api)
    elif st.session_state.current_page == "notion_management":
        show_notion_management(api)


if __name__ == "__main__":
    main()
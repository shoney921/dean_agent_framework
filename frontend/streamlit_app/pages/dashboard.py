"""
대시보드 페이지 모듈
"""

import streamlit as st
from services.api import BackendAPIClient


def show_dashboard(api: BackendAPIClient) -> None:
    """대시보드 페이지를 표시합니다."""
    st.title("🏠 Agent Framework 대시보드")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("총 실행 수", "0", "0")
    
    with col2:
        st.metric("활성 팀", "0", "0")
    
    with col3:
        st.metric("Notion 페이지", "0", "0")
    
    st.markdown("---")
    st.info("대시보드 기능은 추후 구현 예정입니다.")

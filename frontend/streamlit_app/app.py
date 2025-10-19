import streamlit as st
import sys
import os

# 프로젝트 루트 경로를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)

from frontend.streamlit_app.pages import home


def main():
    """스트림릿 메인 애플리케이션 (홈페이지)"""
    
    # 페이지 설정
    st.set_page_config(
        page_title="Dean Agent Framework",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 사이드바 네비게이션
    with st.sidebar:
        st.title("🤖 Dean Agent Framework")
        st.markdown("---")
        
        # 네비게이션 링크
        st.markdown("### 📋 페이지")
        st.markdown("- [🏠 홈](/)" + (" ← 현재 페이지" if st.query_params.get("page") is None else ""))
        st.markdown("- [📊 실행 로그](/agent_logs)")
        st.markdown("- [📝 노션 관리](/notion_management)")
        
        st.markdown("---")
        
        # 상태 정보 표시
        st.markdown("### 📊 시스템 상태")
        
        # API 연결 상태 확인 (간단한 예시)
        try:
            from frontend.streamlit_app.services.api import BackendAPIClient
            client = BackendAPIClient()
            # 간단한 API 호출로 연결 상태 확인
            client.list_runs(limit=1)
            st.success("✅ API 연결됨")
        except Exception as e:
            st.error(f"❌ API 연결 실패: {str(e)}")
    
    # 홈페이지 표시
    home.show()


if __name__ == "__main__":
    main()

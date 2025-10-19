"""
Notion 관리 페이지 모듈
"""

import streamlit as st
from services.api import BackendAPIClient


def show_notion_management(api: BackendAPIClient) -> None:
    """Notion 관리 페이지를 표시합니다."""
    st.title("📋 Notion 관리")
    
    # 세션 상태 초기화
    if "selected_pages" not in st.session_state:
        st.session_state.selected_pages = []
    if "notion_pages_cache" not in st.session_state:
        st.session_state.notion_pages_cache = None
    
    # Notion 페이지 목록 조회
    try:
        # 캐시된 데이터가 있으면 사용, 없으면 API 호출
        if st.session_state.notion_pages_cache is None:
            with st.spinner("Notion 페이지 목록을 불러오는 중..."):
                pages_result = api.get_notion_pages_list(page_size=50)
                if pages_result["success"]:
                    st.session_state.notion_pages_cache = pages_result
                else:
                    st.error(f"❌ 페이지 목록 조회 실패: {pages_result.get('message', '')}")
                    return
        else:
            pages_result = st.session_state.notion_pages_cache
            
        pages = pages_result["pages"]
        st.toast(f"✅ {pages_result['count']}개의 페이지를 찾았습니다.")
        
        if pages:
            st.subheader("📄 페이지 목록")
            
            # 체크박스로 페이지 선택
            selected_pages = []
            for page in pages:
                # API 응답에서는 'page_id'를 사용하므로 이를 'id'로 매핑
                page_id = page.get("page_id", page.get("id", ""))
                page_title = page.get("title", "제목 없음")
                page_url = page.get("url", "")

                # 각 페이지를 컨테이너로 감싸기
                with st.container():
                    col1, col2 = st.columns([1, 6])
                    
                    with col1:
                        # 체크박스
                        checkbox_key = f"page_checkbox_{page_id}"
                    
                        is_selected = st.checkbox(
                            "",
                            value=page_id in st.session_state.selected_pages,
                            key=checkbox_key,
                            label_visibility="collapsed"
                        )
                        
                        # 상태 즉시 업데이트
                        if is_selected and page_id not in st.session_state.selected_pages:
                            st.session_state.selected_pages.append(page_id)
                        elif not is_selected and page_id in st.session_state.selected_pages:
                            st.session_state.selected_pages.remove(page_id)
                        
                        if is_selected:
                            selected_pages.append(page_id)
                    
                    with col2:
                        st.write(f"📄 **{page_title}**")
                        if page_url:
                            st.caption(f"🔗 {page_url}")
                st.divider()
            
            # 선택된 페이지가 있으면 AI 배치 실행 버튼 표시
            if st.session_state.selected_pages:
                if st.button("🚀 AI 배치 실행", use_container_width=True, type="primary"):
                    st.info("AI 배치 실행 기능은 추후 구현 예정입니다.")
            else:
                st.info("AI 배치를 실행할 페이지를 선택해주세요.")
                
        else:
            st.info("Notion 워크스페이스에 페이지가 없습니다.")
            
    except Exception as e:
        st.error(f"❌ 페이지 목록 조회 중 오류가 발생했습니다: {str(e)}")

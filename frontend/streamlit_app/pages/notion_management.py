import streamlit as st
import pandas as pd
from datetime import datetime
import json
import sys
import os

# 프로젝트 루트 경로를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.append(project_root)

from frontend.streamlit_app.services.api import BackendAPIClient


def main():
    """노션 페이지 관리 및 체크리스트 페이지"""
    
    # 페이지 설정
    st.set_page_config(
        page_title="노션 관리 - Dean Agent Framework",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📝 노션 페이지 관리")
    st.markdown("---")
    
    # API 클라이언트 초기화
    try:
        client = BackendAPIClient()
    except Exception as e:
        st.error(f"API 클라이언트 초기화 실패: {str(e)}")
        return
    
    # 탭으로 구분
    tab1, tab2, tab3 = st.tabs(["📋 등록된 페이지", "🔗 페이지 등록", "✅ 체크리스트 관리"])
    
    with tab1:
        show_registered_pages(client)
    
    with tab2:
        show_page_registration(client)
    
    with tab3:
        show_checklist_management(client)


def show_registered_pages(client: BackendAPIClient):
    """등록된 페이지 목록 표시"""
    
    st.subheader("📋 등록된 노션 페이지")
    
    try:
        # 등록된 페이지 목록 조회
        pages = client.get_registered_pages()
        
        if not pages:
            st.info("등록된 페이지가 없습니다.")
            return
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(pages)
        
        # 페이지 목록 표시
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # 페이지별 액션 버튼
        st.markdown("### 🎛️ 페이지 액션")
        
        for page in pages:
            with st.expander(f"📄 {page.get('title', '제목 없음')}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"🔄 동기화", key=f"sync_{page.get('id')}"):
                        sync_page_todos(client, page)
                
                with col2:
                    is_active = page.get('is_active') == 'true'
                    button_text = "⏸️ 비활성화" if is_active else "▶️ 활성화"
                    if st.button(button_text, key=f"toggle_{page.get('id')}"):
                        toggle_page_status(client, page, not is_active)
                
                with col3:
                    if st.button(f"📊 체크리스트 보기", key=f"view_{page.get('id')}"):
                        show_page_checklist(client, page)
                
                # 페이지 정보 표시
                st.markdown(f"**ID**: {page.get('notion_page_id', 'N/A')}")
                st.markdown(f"**상태**: {'🟢 활성' if is_active else '🔴 비활성'}")
                if page.get('url'):
                    st.markdown(f"**URL**: {page.get('url')}")
                if page.get('last_synced_at'):
                    st.markdown(f"**마지막 동기화**: {page.get('last_synced_at')}")
        
    except Exception as e:
        st.error(f"등록된 페이지 조회 실패: {str(e)}")


def show_page_registration(client: BackendAPIClient):
    """새 페이지 등록"""
    
    st.subheader("🔗 새 페이지 등록")
    
    # Notion API 연결 테스트
    st.markdown("### 🔗 Notion API 연결 테스트")
    
    test_api_key = st.text_input(
        "Notion API 키 (선택사항 - 비워두면 환경변수 사용)",
        type="password",
        help="API 키를 입력하면 연결을 테스트합니다. 비워두면 환경변수의 API 키를 사용합니다."
    )
    
    if st.button("🔍 연결 테스트"):
        try:
            result = client.test_notion_connection(test_api_key if test_api_key else None)
            if result.get('success'):
                st.success("✅ Notion API 연결 성공!")
            else:
                st.error(f"❌ 연결 실패: {result.get('message', '알 수 없는 오류')}")
        except Exception as e:
            st.error(f"❌ 연결 테스트 실패: {str(e)}")
    
    st.markdown("---")
    
    # 페이지 등록 폼
    st.markdown("### 📝 페이지 등록")
    
    with st.form("page_registration_form"):
        notion_page_id = st.text_input(
            "Notion 페이지 ID",
            help="Notion 페이지 URL에서 32자리 ID를 입력하세요"
        )
        
        title = st.text_input("페이지 제목")
        
        url = st.text_input("페이지 URL (선택사항)")
        
        parent_page_id = st.text_input("부모 페이지 ID (선택사항)")
        
        is_active = st.selectbox(
            "AI 배치 동작 활성화",
            ["true", "false"],
            index=0,
            help="true: AI 배치 동작 활성화, false: 비활성화"
        )
        
        submitted = st.form_submit_button("📝 페이지 등록")
        
        if submitted:
            if not notion_page_id or not title:
                st.error("페이지 ID와 제목은 필수 입력 항목입니다.")
            else:
                try:
                    result = client.register_notion_page_for_ai_batch(
                        notion_page_id=notion_page_id,
                        title=title,
                        url=url if url else None,
                        parent_page_id=parent_page_id if parent_page_id else None,
                        is_active=is_active
                    )
                    
                    if result.get('success'):
                        st.success(f"✅ {result.get('message', '페이지가 성공적으로 등록되었습니다.')}")
                        st.rerun()
                    else:
                        st.error(f"❌ 등록 실패: {result.get('message', '알 수 없는 오류')}")
                        
                except Exception as e:
                    st.error(f"❌ 등록 실패: {str(e)}")


def show_checklist_management(client: BackendAPIClient):
    """체크리스트 관리"""
    
    st.subheader("✅ 체크리스트 관리")
    
    try:
        # 활성화된 페이지 목록 조회
        active_pages = client.get_active_pages()
        
        if not active_pages:
            st.info("활성화된 페이지가 없습니다. 먼저 페이지를 등록하고 활성화하세요.")
            return
        
        # 페이지 선택
        page_options = {f"{page.get('title', '제목 없음')} (ID: {page.get('notion_page_id', 'N/A')})": page for page in active_pages}
        selected_page_name = st.selectbox("페이지 선택", list(page_options.keys()))
        
        if selected_page_name:
            selected_page = page_options[selected_page_name]
            
            # 체크리스트 조회 및 표시
            show_page_checklist_detailed(client, selected_page)
        
    except Exception as e:
        st.error(f"체크리스트 관리 실패: {str(e)}")


def show_page_checklist_detailed(client: BackendAPIClient, page: dict):
    """선택된 페이지의 상세 체크리스트 표시"""
    
    notion_page_id = page.get('notion_page_id')
    page_title = page.get('title', '제목 없음')
    
    st.markdown(f"### 📋 {page_title} 체크리스트")
    
    # 동기화 버튼
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("🔄 동기화", key=f"sync_detailed_{page.get('id')}"):
            sync_page_todos(client, page)
    
    with col2:
        st.info("동기화 버튼을 클릭하여 Notion에서 최신 체크리스트를 가져옵니다.")
    
    try:
        # 데이터베이스에서 체크리스트 조회
        todos = client.get_page_todos_from_db(notion_page_id)
        
        if todos:
            st.markdown(f"**총 {len(todos)}개의 체크리스트 항목**")
            
            # 체크리스트 표시
            for i, todo in enumerate(todos):
                col1, col2, col3 = st.columns([1, 8, 1])
                
                with col1:
                    checked = todo.get('checked') == 'true'
                    status_emoji = "✅" if checked else "⬜"
                    st.markdown(f"**{status_emoji}**")
                
                with col2:
                    content = todo.get('content', '내용 없음')
                    st.markdown(f"**{content}**")
                
                with col3:
                    block_id = todo.get('block_id', 'N/A')
                    st.markdown(f"ID: {block_id[:8]}...")
                
                st.markdown("---")
        else:
            st.info("체크리스트가 없습니다. 동기화를 실행해보세요.")
            
    except Exception as e:
        st.error(f"체크리스트 조회 실패: {str(e)}")


def show_page_checklist(client: BackendAPIClient, page: dict):
    """페이지 체크리스트 간단 표시 (팝업용)"""
    
    notion_page_id = page.get('notion_page_id')
    page_title = page.get('title', '제목 없음')
    
    try:
        todos = client.get_page_todos_from_db(notion_page_id)
        
        if todos:
            st.success(f"📋 {page_title} - {len(todos)}개 항목")
            for todo in todos[:5]:  # 최대 5개만 표시
                checked = "✅" if todo.get('checked') == 'true' else "⬜"
                st.markdown(f"{checked} {todo.get('content', '내용 없음')}")
            
            if len(todos) > 5:
                st.markdown(f"... 외 {len(todos) - 5}개 항목")
        else:
            st.info(f"📋 {page_title} - 체크리스트 없음")
            
    except Exception as e:
        st.error(f"체크리스트 조회 실패: {str(e)}")


def sync_page_todos(client: BackendAPIClient, page: dict):
    """페이지 체크리스트 동기화"""
    
    notion_page_id = page.get('notion_page_id')
    page_title = page.get('title', '제목 없음')
    
    try:
        with st.spinner(f"{page_title} 동기화 중..."):
            result = client.sync_notion_todos_to_db(notion_page_id)
            
            if result.get('success'):
                synced_count = result.get('synced_count', 0)
                st.success(f"✅ {page_title} 동기화 완료! ({synced_count}개 항목)")
            else:
                st.error(f"❌ 동기화 실패: {result.get('message', '알 수 없는 오류')}")
                
    except Exception as e:
        st.error(f"❌ 동기화 실패: {str(e)}")


def toggle_page_status(client: BackendAPIClient, page: dict, new_status: bool):
    """페이지 활성화 상태 토글"""
    
    notion_page_id = page.get('notion_page_id')
    page_title = page.get('title', '제목 없음')
    is_active_str = "true" if new_status else "false"
    
    try:
        result = client.update_page_active_status(notion_page_id, is_active_str)
        
        if result.get('success'):
            status_text = "활성화" if new_status else "비활성화"
            st.success(f"✅ {page_title} {status_text} 완료!")
            st.rerun()
        else:
            st.error(f"❌ 상태 변경 실패: {result.get('message', '알 수 없는 오류')}")
            
    except Exception as e:
        st.error(f"❌ 상태 변경 실패: {str(e)}")


if __name__ == "__main__":
    main()
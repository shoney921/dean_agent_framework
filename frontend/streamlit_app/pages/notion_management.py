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
    
    st.title("Notion Management")
    
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

def show_registered_pages(client: BackendAPIClient):
    """등록된 페이지 목록 표시"""
    
    st.subheader("Notion Pages List")
    
    try:
        # 등록된 페이지 목록 조회
        pages = client.get_notion_pages_list()
        
        if not pages:
            st.info("등록된 페이지가 없습니다.")
            return

        # 계층 트리 렌더링: 부모-자식 관계를 고려하여 들여쓰기 출력 (제목, URL만 표시)
        def build_hierarchy(page_list):
            id_to_page = {p.get('page_id'): p for p in page_list}
            children_map = {}
            for p in page_list:
                parent_id = p.get('parent_id')
                if parent_id:
                    children_map.setdefault(parent_id, []).append(p)
            # 루트: 워크스페이스 소속이거나 부모가 없거나, 부모가 목록에 없는 경우
            all_ids = set(id_to_page.keys())
            roots = [
                p for p in page_list
                if p.get('parent_type') == 'workspace' or not p.get('parent_id') or p.get('parent_id') not in all_ids
            ]
            return roots, children_map

        def render_row(node, children_map, depth, is_root):
            title = node.get('title', '제목 없음')
            url = node.get('url')
            page_id = node.get('page_id')
            batch_status = node.get('batch_status')
            bullet = (
                '<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#2ea043;margin-right:8px;"></span>'
                if is_root else
                '<span style="display:inline-block;width:10px;height:10px;border-radius:50%;border:1px solid #999;background:transparent;margin-right:8px;"></span>'
            )
            indent_px = 18 * depth
            name_html = f'<span style="margin-left:{indent_px}px">{bullet}{title}</span>'

            col1, col2, col3 = st.columns([6, 10, 4])
            with col1:
                st.markdown(name_html, unsafe_allow_html=True)
            with col2:
                if url:
                    st.markdown(f'<a href="{url}" target="_blank">{url}</a>', unsafe_allow_html=True)
                else:
                    st.markdown('-')
            with col3:
                st.button(f'{batch_status}상태가져오면됨', key=f"execute_{page_id}")

            for child in sorted(children_map.get(page_id, []), key=lambda x: x.get('title', '')):
                render_row(child, children_map, depth + 1, False)

        page_list = pages.get('pages', [])
        roots, children_map = build_hierarchy(page_list)
        roots_sorted = sorted(roots, key=lambda x: x.get('title', ''))

        # 헤더 라인
        h1, h2, h3 = st.columns([6, 10, 4])
        with h1:
            st.markdown('**페이지명**')
        with h2:
            st.markdown('**URL**')
        with h3:
            st.markdown('**배치실행**')

        for root in roots_sorted:
            render_row(root, children_map, depth=0, is_root=True)
        
    except Exception as e:
        st.error(f"등록된 페이지 조회 실패: {str(e)}")


if __name__ == "__main__":
    main()
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

        def render_tree_html(node, children_map):
            title = node.get('title', '제목 없음')
            url = node.get('url')
            link_html = f'<a href="{url}" target="_blank">{title}</a>' if url else title
            child_nodes = sorted(children_map.get(node.get('page_id'), []), key=lambda x: x.get('title', ''))
            if child_nodes:
                children_html = ''.join(render_tree_html(child, children_map) for child in child_nodes)
                return f'<li>{link_html}<ul>{children_html}</ul></li>'
            else:
                return f'<li>{link_html}</li>'

        page_list = pages.get('pages', [])
        roots, children_map = build_hierarchy(page_list)
        roots_sorted = sorted(roots, key=lambda x: x.get('title', ''))
        html = '<ul>' + ''.join(render_tree_html(root, children_map) for root in roots_sorted) + '</ul>'
        st.markdown(html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"등록된 페이지 조회 실패: {str(e)}")


if __name__ == "__main__":
    main()
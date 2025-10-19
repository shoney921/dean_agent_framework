import os
import time
from typing import Any, Dict, List, Optional

import streamlit as st

from services.api import BackendAPIClient


def format_run_title(run: Dict[str, Any]) -> str:
    team = run.get("team_name") or "UnknownTeam"
    task = (run.get("task") or "").strip()
    status = run.get("status") or "unknown"
    run_id = run.get("id")
    return f"#{run_id} [{team}] {task[:40]}{'...' if len(task) > 40 else ''} ({status})"


def init_state() -> None:
    if "selected_run_id" not in st.session_state:
        st.session_state.selected_run_id = None


def main() -> None:
    st.set_page_config(page_title="Agent Framework Dashboard", layout="wide")

    init_state()
    api = BackendAPIClient()

    # 사이드바 네비게이션
    st.sidebar.title("Menu")
    if st.sidebar.button("🏠 대시보드", use_container_width=True, help="대시보드로 이동"):
        show_dashboard(api)
    if st.sidebar.button("📝 Agent 로그", use_container_width=True, help="Agent 로그로 이동"):
        show_agent_logs(api)
    if st.sidebar.button("📋 Notion 관리", use_container_width=True, help="Notion 관리로 이동"):
        show_notion_management(api)


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


def show_agent_logs(api: BackendAPIClient) -> None:
    """Agent 로그 페이지를 표시합니다."""
    st.title("📝 Agent 실행 로그")
    
    # 쿼리 파라미터에서 run_id를 읽어 채팅방처럼 진입/이탈 상태를 제어
    query_params = {}
    try:
        # Streamlit 최신 API
        query_params = dict(st.query_params)
    except Exception:  # noqa: BLE001
        # 구버전 호환
        query_params = st.experimental_get_query_params()  # type: ignore[attr-defined]

    selected_from_query: Optional[int] = None
    if query_params.get("run_id"):
        try:
            # run_id=["123"] 형태 또는 "123"
            raw = query_params["run_id"]
            selected_from_query = int(raw[0] if isinstance(raw, list) else raw)
        except Exception:  # noqa: BLE001
            selected_from_query = None

    # 사이드바: 필터는 목록 화면에서만 표시
    team_filter: Optional[str] = None
    limit: int = 50
    if not selected_from_query:
        st.header("필터")
        team_filter = st.text_input("팀 이름", value="")
        limit = st.slider("최대 개수", min_value=10, max_value=200, value=50, step=10)

    def navigate_to_run(run_id: int) -> None:
        """URL 쿼리파라미터에 run_id를 설정하고 리렌더링."""
        try:
            st.query_params["run_id"] = str(run_id)
        except Exception:  # noqa: BLE001
            st.experimental_set_query_params(run_id=str(run_id))  # type: ignore[attr-defined]
        st.rerun()

    def clear_run_and_go_back() -> None:
        """쿼리파라미터에서 run_id 제거하고 목록으로 복귀."""
        try:
            current = dict(st.query_params)
            current.pop("run_id", None)
            st.query_params.clear()
            for k, v in current.items():
                st.query_params[k] = v
        except Exception:  # noqa: BLE001
            st.experimental_set_query_params()  # type: ignore[attr-defined]
        st.rerun()

    # 1) 목록 화면 (채팅방 리스트처럼)
    if not selected_from_query:
        st.subheader("실행 목록")
        try:
            runs: List[Dict[str, Any]] = api.list_runs(team_name=team_filter or None, limit=limit)
        except Exception as e:  # noqa: BLE001
            st.error(f"실행 목록을 불러오지 못했습니다: {e}")
            runs = []

        if not runs:
            st.info("실행 기록이 없습니다.")
            return

        # 카카오톡 채팅방 리스트 느낌으로 버튼 렌더링
        for run in runs:
            label = format_run_title(run)
            if st.button(label, use_container_width=True, key=f"run-list-{run['id']}"):
                st.session_state.selected_run_id = run["id"]
                navigate_to_run(run["id"])  # URL 변경 후 재실행

        return

    # 2) 상세 화면 (대화 형식)
    run_id: int = selected_from_query
    top_cols = st.columns([1, 1, 1, 1, 1])
    with top_cols[0]:
        if st.button("⬅ 목록으로", use_container_width=True):
            clear_run_and_go_back()
    with top_cols[1]:
        st.metric("Run ID", str(run_id))

    # 실행 상세 조회
    try:
        run = api.get_run_full(run_id)
    except Exception as e:  # noqa: BLE001
        st.error(f"실행 상세를 불러오지 못했습니다: {e}")
        return

    if not run:
        st.warning("선택한 실행을 찾을 수 없습니다.")
        return

    meta = {
        "team": run.get("team_name") or "-",
        "status": run.get("status") or "-",
        "model": run.get("model") or "-",
    }

    with st.expander("메타 정보", expanded=False):
        meta_cols = st.columns(3)
        meta_cols[0].metric("Team", meta["team"])
        meta_cols[1].metric("Status", meta["status"])
        meta_cols[2].metric("Model", meta["model"])

    st.markdown("---")

    messages: List[Dict[str, Any]] = run.get("messages") or []
    if not messages:
        st.info("메시지가 없습니다.")
        return

    # 대화 형식으로 렌더링: st.chat_message 이용
    for msg in messages:
        role_raw = (msg.get("role") or "").lower().strip()
        role: str
        if role_raw in {"user", "human"}:
            role = "user"
        elif role_raw in {"assistant", "ai", "agent"}:
            role = "assistant"
        elif role_raw == "system":
            role = "system"
        else:
            role = "assistant"

        agent_name = msg.get("agent_name") or ""
        tool_name = msg.get("tool_name") or ""
        content = msg.get("content") or ""

        header_parts: List[str] = []
        if agent_name:
            header_parts.append(agent_name)
        if tool_name:
            header_parts.append(f"tool: {tool_name}")
        header = " | ".join(header_parts)

        with st.chat_message(role):
            if header:
                st.caption(header)
            st.write(content)


def show_notion_management(api: BackendAPIClient) -> None:
    """Notion 관리 페이지를 표시합니다."""
    st.title("📋 Notion 관리")
    
    # 세션 상태 초기화
    if "selected_pages" not in st.session_state:
        st.session_state.selected_pages = []
    
    st.subheader("📄 Notion 페이지 목록")
    
    # Notion 페이지 목록 조회
    try:
        with st.spinner("Notion 페이지 목록을 불러오는 중..."):
            pages_result = api.get_notion_pages_list(page_size=50)
            
        if pages_result["success"]:
            pages = pages_result["pages"]
            st.toast(f"{pages_result['count']}개의 페이지를 찾았습니다.", icon="✅")
            
            if pages:
                
                # 체크박스로 페이지 선택
                selected_pages = []
                for page in pages:
                    # API 응답에서는 'page_id'를 사용하므로 이를 'id'로 매핑
                    page_id = page.get("page_id", page.get("id", ""))
                    page_title = page.get("title", "제목 없음")
                    page_url = page.get("url", "")
                    
                    # 체크박스 생성
                    is_selected = st.checkbox(
                        f"📄 {page_title}",
                        value=page_id in st.session_state.selected_pages,
                        key=f"page_checkbox_{page_id}"
                    )
                    
                    if is_selected:
                        selected_pages.append(page_id)
                        if page_url:
                            st.caption(f"🔗 {page_url}")
                    else:
                        if page_id in st.session_state.selected_pages:
                            st.session_state.selected_pages.remove(page_id)
                
                # 선택된 페이지 상태 업데이트
                st.session_state.selected_pages = selected_pages
                
                st.markdown("---")
                
                # AI 배치 실행 섹션
                st.subheader("🤖 AI 배치 실행")
                
                if selected_pages:
                    st.info(f"선택된 페이지: {len(selected_pages)}개")
                    
                    col1, col2, col3 = st.columns([1, 1, 2])
                    
                    with col1:
                        if st.button("📥 선택된 페이지 등록", type="primary"):
                            success_count = 0
                            error_count = 0
                            
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            for i, page_id in enumerate(selected_pages):
                                try:
                                    # 페이지 정보 찾기 (page_id 또는 id로 찾기)
                                    page_info = next((p for p in pages if p.get("page_id", p.get("id", "")) == page_id), None)
                                    if page_info:
                                        result = api.register_notion_page_for_ai_batch(
                                            notion_page_id=page_id,
                                            title=page_info.get("title", "제목 없음"),
                                            url=page_info.get("url"),
                                            is_active="true"
                                        )
                                        if result["success"]:
                                            success_count += 1
                                        else:
                                            error_count += 1
                                    else:
                                        error_count += 1
                                except Exception as e:
                                    error_count += 1
                                    st.error(f"페이지 {page_id} 등록 실패: {str(e)}")
                                
                                # 진행률 업데이트
                                progress = (i + 1) / len(selected_pages)
                                progress_bar.progress(progress)
                                status_text.text(f"진행률: {i + 1}/{len(selected_pages)}")
                            
                            if success_count > 0:
                                st.success(f"✅ {success_count}개 페이지가 성공적으로 등록되었습니다.")
                            if error_count > 0:
                                st.error(f"❌ {error_count}개 페이지 등록에 실패했습니다.")
                    
                    with col2:
                        if st.button("🔄 투두리스트 동기화"):
                            success_count = 0
                            error_count = 0
                            
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            for i, page_id in enumerate(selected_pages):
                                try:
                                    result = api.sync_notion_todos_to_db(page_id)
                                    if result["success"]:
                                        success_count += 1
                                    else:
                                        error_count += 1
                                except Exception as e:
                                    error_count += 1
                                    st.error(f"페이지 {page_id} 동기화 실패: {str(e)}")
                                
                                # 진행률 업데이트
                                progress = (i + 1) / len(selected_pages)
                                progress_bar.progress(progress)
                                status_text.text(f"진행률: {i + 1}/{len(selected_pages)}")
                            
                            if success_count > 0:
                                st.success(f"✅ {success_count}개 페이지의 투두리스트가 동기화되었습니다.")
                            if error_count > 0:
                                st.error(f"❌ {error_count}개 페이지 동기화에 실패했습니다.")
                    
                    with col3:
                        if st.button("🚀 AI 배치 실행", type="primary"):
                            st.info("AI 배치 실행 기능은 추후 구현 예정입니다.")
                            st.write("선택된 페이지들에 대해 AI 에이전트가 자동으로 작업을 수행합니다.")
                else:
                    st.warning("AI 배치를 실행할 페이지를 선택해주세요.")
                    
            else:
                st.info("Notion 워크스페이스에 페이지가 없습니다.")
                
        else:
            st.error(f"❌ 페이지 목록 조회 실패: {pages_result.get('message', '')}")
            
    except Exception as e:
        st.error(f"❌ 페이지 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    st.markdown("---")
    
    # 등록된 페이지 관리
    st.subheader("📊 등록된 페이지 관리")
    
    try:
        registered_pages = api.get_registered_pages()
        
        if registered_pages:
            st.success(f"✅ {len(registered_pages)}개의 등록된 페이지가 있습니다.")
            
            for page in registered_pages:
                with st.expander(f"📄 {page['title']} ({'활성' if page['is_active'] == 'true' else '비활성'})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**페이지 ID:** {page['notion_page_id']}")
                        if page.get('url'):
                            st.write(f"**URL:** {page['url']}")
                        st.write(f"**등록일:** {page.get('created_at', 'N/A')}")
                        st.write(f"**마지막 동기화:** {page.get('last_synced_at', 'N/A')}")
                    
                    with col2:
                        if page['is_active'] == 'true':
                            if st.button("비활성화", key=f"deactivate_{page['id']}"):
                                try:
                                    result = api.update_page_active_status(page['notion_page_id'], "false")
                                    if result["success"]:
                                        st.success("페이지가 비활성화되었습니다.")
                                        st.rerun()
                                    else:
                                        st.error(f"비활성화 실패: {result['message']}")
                                except Exception as e:
                                    st.error(f"비활성화 오류: {str(e)}")
                        else:
                            if st.button("활성화", key=f"activate_{page['id']}"):
                                try:
                                    result = api.update_page_active_status(page['notion_page_id'], "true")
                                    if result["success"]:
                                        st.success("페이지가 활성화되었습니다.")
                                        st.rerun()
                                    else:
                                        st.error(f"활성화 실패: {result['message']}")
                                except Exception as e:
                                    st.error(f"활성화 오류: {str(e)}")
        else:
            st.info("등록된 페이지가 없습니다.")
            
    except Exception as e:
        st.error(f"등록된 페이지 조회 중 오류가 발생했습니다: {str(e)}")


if __name__ == "__main__":
    main()



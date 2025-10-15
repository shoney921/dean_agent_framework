import os
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
    st.set_page_config(page_title="Agent Logs Viewer", layout="wide")

    init_state()
    api = BackendAPIClient()

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
        st.sidebar.header("필터")
        team_filter = st.sidebar.text_input("팀 이름", value="")
        limit = st.sidebar.slider("최대 개수", min_value=10, max_value=200, value=50, step=10)
        with st.sidebar:
            st.markdown("---")
            st.caption(f"API: {api.base_url}")

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


if __name__ == "__main__":
    main()



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

    st.sidebar.header("필터")
    team_filter = st.sidebar.text_input("팀 이름", value="")
    limit = st.sidebar.slider("최대 개수", min_value=10, max_value=200, value=50, step=10)

    with st.sidebar:
        st.markdown("---")
        st.caption(f"API: {api.base_url}")

    col1, col2 = st.columns([1, 2], gap="large")

    # 좌측: 실행 목록
    with col1:
        st.subheader("실행 목록")
        try:
            runs: List[Dict[str, Any]] = api.list_runs(team_name=team_filter or None, limit=limit)
        except Exception as e:  # noqa: BLE001
            st.error(f"실행 목록을 불러오지 못했습니다: {e}")
            runs = []

        if not runs:
            st.info("실행 기록이 없습니다.")
        else:
            for run in runs:
                label = format_run_title(run)
                if st.button(label, use_container_width=True, key=f"run-btn-{run['id']}"):
                    st.session_state.selected_run_id = run["id"]

    # 우측: 메시지 상세
    with col2:
        st.subheader("메시지")
        run_id: Optional[int] = st.session_state.selected_run_id
        if not run_id:
            st.info("왼쪽에서 실행을 선택하세요.")
            return

        try:
            run = api.get_run_full(run_id)
        except Exception as e:  # noqa: BLE001
            st.error(f"실행 상세를 불러오지 못했습니다: {e}")
            return

        if not run:
            st.warning("선택한 실행을 찾을 수 없습니다.")
            return

        # 상단 메타 정보
        meta_cols = st.columns(4)
        meta_cols[0].metric("Run ID", str(run.get("id")))
        meta_cols[1].metric("Team", run.get("team_name") or "-")
        meta_cols[2].metric("Status", run.get("status") or "-")
        meta_cols[3].metric("Model", run.get("model") or "-")

        st.markdown("---")

        messages: List[Dict[str, Any]] = run.get("messages") or []
        if not messages:
            st.info("메시지가 없습니다.")
            return

        for i, msg in enumerate(messages, start=1):
            role = msg.get("role") or ""
            agent_name = msg.get("agent_name") or ""
            tool_name = msg.get("tool_name") or ""
            content = msg.get("content") or ""

            header = f"[{i}] {role} - {agent_name}"
            if tool_name:
                header += f" (tool: {tool_name})"

            with st.expander(header, expanded=True):
                st.write(content)


if __name__ == "__main__":
    main()



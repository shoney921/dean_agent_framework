import os
from typing import Any, Dict, List, Optional

import requests


def get_api_base_url() -> str:
    """프론트 전용 환경변수에서 API 베이스 URL을 가져옵니다.
    기본값은 v1 하위의 agent-logs 네임스페이스로 설정합니다.
    """
    return os.getenv("API_BASE_URL", "http://localhost:8000/api/v1/agent-logs")


def get_notion_api_base_url() -> str:
    """Notion API 베이스 URL을 가져옵니다."""
    return os.getenv("NOTION_API_BASE_URL", "http://localhost:8000/api/v1/notion")


class BackendAPIClient:
    """백엔드 REST API 호출 클라이언트"""

    def __init__(self, base_url: Optional[str] = None) -> None:
        self.base_url = base_url or get_api_base_url()
        self.notion_base_url = get_notion_api_base_url()
        self.session = requests.Session()

    # ----------------------------- Runs ----------------------------------
    def list_runs(self, team_name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"limit": limit}
        if team_name:
            params["team_name"] = team_name
        resp = self.session.get(f"{self.base_url}/runs", params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_run(self, run_id: int) -> Dict[str, Any]:
        resp = self.session.get(f"{self.base_url}/runs/{run_id}", timeout=15)
        resp.raise_for_status()
        return resp.json()

    # --------------------------- Messages ---------------------------------
    def list_messages_by_run(self, run_id: int | str) -> List[Dict[str, Any]]:
        # run_id를 정수로 변환
        if isinstance(run_id, str):
            try:
                run_id = int(run_id)
            except ValueError:
                raise ValueError(f"Invalid run_id format: {run_id}")
        
        resp = self.session.get(f"{self.base_url}/runs/{run_id}/messages", timeout=15)
        resp.raise_for_status()
        return resp.json()

    # --------------------------- Notion ---------------------------------
    def get_notion_pages_list(
        self, 
        page_size: int = 100, 
        filter_type: str = "page", 
        sort_direction: str = "descending"
    ) -> Dict[str, Any]:
        """Notion 페이지 목록을 조회합니다."""
        params = {
            "page_size": page_size,
            "filter_type": filter_type,
            "sort_direction": sort_direction
        }
        resp = self.session.get(f"{self.notion_base_url}/pages", params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_registered_pages(self) -> List[Dict[str, Any]]:
        """등록된 Notion 페이지 목록을 조회합니다."""
        resp = self.session.get(f"{self.notion_base_url}/pages/registered", timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_active_pages(self) -> List[Dict[str, Any]]:
        """활성화된 Notion 페이지 목록을 조회합니다."""
        resp = self.session.get(f"{self.notion_base_url}/pages/active", timeout=15)
        resp.raise_for_status()
        return resp.json()

    def update_batch_status(self, notion_page_id: str, status: str) -> Dict[str, Any]:
        """페이지의 AI 배치 동작 활성화 상태를 업데이트합니다."""
        params = {"status": status}
        resp = self.session.put(f"{self.notion_base_url}/pages/{notion_page_id}/batch-status", params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
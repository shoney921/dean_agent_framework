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

    def get_run_full(self, run_id: int) -> Dict[str, Any]:
        resp = self.session.get(f"{self.base_url}/runs/{run_id}/full", timeout=15)
        resp.raise_for_status()
        return resp.json()

    # --------------------------- Messages ---------------------------------
    def list_messages_by_run(self, run_id: int) -> List[Dict[str, Any]]:
        resp = self.session.get(f"{self.base_url}/runs/{run_id}/messages", timeout=15)
        resp.raise_for_status()
        return resp.json()

    # --------------------------- Notion ---------------------------------
    def test_notion_connection(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Notion API 연결을 테스트합니다."""
        data = {"api_key": api_key} if api_key else {}
        resp = self.session.post(f"{self.notion_base_url}/test-connection", json=data, timeout=15)
        resp.raise_for_status()
        return resp.json()

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

    def register_notion_page_for_ai_batch(
        self,
        notion_page_id: str,
        title: str,
        url: Optional[str] = None,
        parent_page_id: Optional[str] = None,
        is_active: str = "true"
    ) -> Dict[str, Any]:
        """AI 배치 동작할 Notion 페이지를 등록합니다."""
        data = {
            "notion_page_id": notion_page_id,
            "title": title,
            "url": url,
            "parent_page_id": parent_page_id,
            "is_active": is_active
        }
        resp = self.session.post(f"{self.notion_base_url}/pages/register", json=data, timeout=15)
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

    def get_notion_todos_from_page(self, notion_page_id: str) -> Dict[str, Any]:
        """특정 Notion 페이지의 투두리스트를 조회합니다."""
        resp = self.session.get(f"{self.notion_base_url}/pages/{notion_page_id}/todos", timeout=15)
        resp.raise_for_status()
        return resp.json()

    def sync_notion_todos_to_db(self, notion_page_id: str) -> Dict[str, Any]:
        """Notion 페이지의 투두리스트를 데이터베이스에 동기화합니다."""
        resp = self.session.post(f"{self.notion_base_url}/pages/{notion_page_id}/todos/sync", timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_page_todos_from_db(self, notion_page_id: str) -> List[Dict[str, Any]]:
        """데이터베이스에서 특정 페이지의 투두리스트를 조회합니다."""
        resp = self.session.get(f"{self.notion_base_url}/pages/{notion_page_id}/todos/db", timeout=15)
        resp.raise_for_status()
        return resp.json()

    def update_page_active_status(self, notion_page_id: str, is_active: str) -> Dict[str, Any]:
        """페이지의 AI 배치 동작 활성화 상태를 업데이트합니다."""
        params = {"is_active": is_active}
        resp = self.session.put(f"{self.notion_base_url}/pages/{notion_page_id}/active-status", params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()



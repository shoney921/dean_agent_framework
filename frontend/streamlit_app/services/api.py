import os
from typing import Any, Dict, List, Optional

import requests


def get_api_base_url() -> str:
    """프론트 전용 환경변수에서 API 베이스 URL을 가져옵니다.
    기본값은 v1 하위의 agent-logs 네임스페이스로 설정합니다.
    """
    return os.getenv("API_BASE_URL", "http://localhost:8000/api/v1/agent-logs")


class BackendAPIClient:
    """백엔드 REST API 호출 클라이언트"""

    def __init__(self, base_url: Optional[str] = None) -> None:
        self.base_url = base_url or get_api_base_url()
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



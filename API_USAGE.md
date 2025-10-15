# Dean Framework API 사용 가이드

## 🚀 서버 실행

```bash
# 가상환경 활성화
source venv/bin/activate

# FastAPI 서버 실행
python app.py
```

서버가 실행되면 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📋 API 엔드포인트 목록

### 1. 에이전트 실행 기록 관리

#### 새로운 실행 기록 생성

```http
POST /api/v1/agent-logs/runs
Content-Type: application/json

{
  "team_name": "SelectorGroupChat",
  "task": "LG CNS 주식 전망 분석",
  "model": "gemini-1.5-flash"
}
```

#### 실행 기록 목록 조회

```http
GET /api/v1/agent-logs/runs?team_name=SelectorGroupChat&limit=10
```

#### 특정 실행 기록 조회 (메시지 포함)

```http
GET /api/v1/agent-logs/runs/{run_id}
```

#### 실행 기록 완료 처리

```http
PATCH /api/v1/agent-logs/runs/{run_id}/finish?status=completed
```

### 2. 메시지 관리

#### 새로운 메시지 추가

```http
POST /api/v1/agent-logs/messages
Content-Type: application/json

{
  "run_id": 1,
  "agent_name": "web_search_agent",
  "role": "assistant",
  "content": "웹 검색을 통해 LG CNS 관련 정보를 수집했습니다.",
  "tool_name": "web_search"
}
```

#### 특정 실행의 메시지 목록 조회

```http
GET /api/v1/agent-logs/runs/{run_id}/messages
```

### 3. 통계 및 분석

#### 팀별 통계 정보 조회

```http
GET /api/v1/agent-logs/teams/{team_name}/statistics
```

응답 예시:

```json
{
  "team_name": "SelectorGroupChat",
  "total_runs": 15,
  "completed_runs": 12,
  "running_runs": 2,
  "failed_runs": 1,
  "average_duration": 45.67,
  "total_messages": 156
}
```

## 🔧 사용 예시

### Python 클라이언트 예시

```python
import requests

# 서버 URL
BASE_URL = "http://localhost:8000/api/v1/agent-logs"

# 1. 새로운 실행 기록 생성
run_data = {
    "team_name": "SelectorGroupChat",
    "task": "삼성전자 주식 분석",
    "model": "gemini-1.5-flash"
}
response = requests.post(f"{BASE_URL}/runs", json=run_data)
run = response.json()
run_id = run["id"]

# 2. 메시지 추가
message_data = {
    "run_id": run_id,
    "agent_name": "web_search_agent",
    "role": "assistant",
    "content": "삼성전자 관련 뉴스를 검색했습니다.",
    "tool_name": "web_search"
}
requests.post(f"{BASE_URL}/messages", json=message_data)

# 3. 실행 완료 처리
requests.patch(f"{BASE_URL}/runs/{run_id}/finish", params={"status": "completed"})

# 4. 실행 기록 조회
response = requests.get(f"{BASE_URL}/runs/{run_id}")
full_run_data = response.json()
print(f"실행 ID: {full_run_data['id']}")
print(f"태스크: {full_run_data['task']}")
print(f"메시지 수: {len(full_run_data['messages'])}")
```

### cURL 예시

```bash
# 실행 기록 생성
curl -X POST "http://localhost:8000/api/v1/agent-logs/runs" \
  -H "Content-Type: application/json" \
  -d '{
    "team_name": "SelectorGroupChat",
    "task": "네이버 주식 분석",
    "model": "gemini-1.5-flash"
  }'

# 실행 기록 목록 조회
curl "http://localhost:8000/api/v1/agent-logs/runs?limit=5"

# 팀 통계 조회
curl "http://localhost:8000/api/v1/agent-logs/teams/SelectorGroupChat/statistics"
```

## 📊 데이터 모델

### AgentRun (실행 기록)

- `id`: 실행 ID (자동 생성)
- `team_name`: 팀 이름
- `task`: 실행할 태스크
- `started_at`: 시작 시간
- `ended_at`: 종료 시간 (완료 시)
- `status`: 상태 (running, completed, failed)
- `model`: 사용된 모델
- `messages`: 관련 메시지 목록

### AgentMessage (메시지)

- `id`: 메시지 ID (자동 생성)
- `run_id`: 실행 ID (외래키)
- `agent_name`: 에이전트 이름
- `role`: 역할 (user, assistant, tool, system)
- `content`: 메시지 내용
- `tool_name`: 사용된 도구 이름 (선택사항)
- `created_at`: 생성 시간

## 🛠️ 개발 및 디버깅

### 로그 확인

서버 실행 시 콘솔에서 요청/응답 로그를 확인할 수 있습니다.

### 데이터베이스 확인

SQLite 데이터베이스 파일(`app.db`)을 직접 확인하거나 SQLite 브라우저를 사용할 수 있습니다.

### API 문서

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

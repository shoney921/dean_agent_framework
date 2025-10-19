# Dean Framework

AutoGen 기반 웹 검색, 데이터 분석 및 Notion 연동 에이전트 시스템

## 📂 프로젝트 구조

```
dean_framework/
├── src/                           # 소스 코드 루트
│   ├── api/                       # 🌐 API 계층 (라우터, 의존성)
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── agent_logs.py
│   │   │   │   └── notion.py      # Notion API 엔드포인트
│   │   │   └── api.py
│   │   └── deps.py
│   │
│   ├── services/                  # 🧠 비즈니스 로직 계층
│   │   ├── agent_log_service.py
│   │   └── notion_service.py      # Notion 서비스
│   │
│   ├── core/                      # ⚙️ 핵심 설정 및 데이터 모델
│   │   ├── config.py             # 환경 설정 및 상수
│   │   ├── models.py             # ORM 모델
│   │   └── schemas.py            # Pydantic 스키마 (Notion 포함)
│   │
│   ├── repositories/              # 🗄️ 데이터베이스 추상화 계층
│   │   └── agent_logs.py
│   │
│   └── ai/                        # 🤖 AI 컴포넌트 패키지
│       ├── agents/                # 🧑‍💻 개별 AI 에이전트 정의
│       │   ├── base.py
│       │   ├── web_search_agent.py
│       │   ├── data_analyst_agent.py
│       │   ├── analysis_agent.py
│       │   ├── insight_agent.py
│       │   └── summary_agent.py
│       │
│       ├── tools/                 # 🛠️ AI 에이전트용 도구 세트
│       │   ├── web_search_tool.py
│       │   ├── data_analysis_tool.py
│       │   ├── notion_tools.py    # 기존 Notion 도구
│       │   └── notion_client.py   # 새로운 Notion 클라이언트
│       │
│       └── orchestrator/          # 🔗 에이전트 상호작용 및 흐름 제어
│           ├── team.py
│           ├── advanced_team.py
│           ├── hierarchical_team.py
│           └── team_config.py
│
├── frontend/                      # 🎨 프론트엔드 (Streamlit)
│   └── streamlit_app/
│       ├── app.py
│       └── services/
│           └── api.py
│
├── tests/                         # 🧪 테스트 코드
├── main.py                        # 🚀 애플리케이션 시작점
├── app.py                         # FastAPI 애플리케이션
├── requirements.txt               # 프로젝트 의존성
├── notion_example.py              # Notion API 사용 예시
├── .env                          # 환경변수 파일 (gitignore)
└── README.md                     # 프로젝트 문서

```

## 🏗️ 아키텍처 설계 원칙

이 프로젝트는 확장성과 유지보수성을 극대화하기 위해 다음 원칙을 따릅니다:

### 1. **계층 분리 (Separation of Concerns)**

- **core**: 시스템 전반의 설정 및 공통 데이터 구조
- **ai/agents**: 에이전트의 '정체성' 정의
- **ai/tools**: 에이전트의 '능력' 정의
- **ai/orchestrator**: 에이전트의 '협업 방식' 정의

### 2. **AI 패키지 구조**

```
ai/
├── agents/       # "누가" - 에이전트의 역할과 프롬프트 정의
├── tools/        # "무엇을" - 외부 세계와 상호작용하는 도구
└── orchestrator/ # "어떻게" - 에이전트 간 협업 흐름 제어
```

## 🚀 시작하기

### 1. 가상환경 활성화

```bash
source venv/bin/activate
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 필요한 API 키를 설정하세요:

```env
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
NOTION_API_KEY=your_notion_api_key
```

### 3. 애플리케이션 실행

#### AutoGen 에이전트 실행

```bash
python main.py
```

#### FastAPI 서버 실행

```bash
python app.py
```

#### Streamlit 웹 애플리케이션 실행

```bash
python run_streamlit.py
```

또는 직접 실행:

```bash
streamlit run frontend/streamlit_app/app.py
```

브라우저에서 `http://localhost:8501`로 접속하여 웹 인터페이스를 사용할 수 있습니다.

#### Notion API 사용 예시

```bash
python notion_example.py
```

## 🧪 개별 컴포넌트 테스트

### 웹 검색 에이전트 테스트

```bash
python -m src.ai.agents.web_search_agent
```

### 데이터 분석 에이전트 테스트

```bash
python -m src.ai.agents.data_analyst_agent
```

### 팀 협업 테스트

```bash
python -m src.ai.orchestrator.team
```

## 📝 주요 컴포넌트

### AI Agents (에이전트)

- **WebSearchAgent**: 웹 검색을 통해 정보를 수집하는 에이전트
- **DataAnalystAgent**: 데이터 분석 및 통계 계산을 수행하는 에이전트

### AI Tools (도구)

- **search_web_tool**: Tavily API를 사용한 웹 검색
  - 🔍 검색 쿼리 로깅 기능 포함
- **percentage_change_tool**: 퍼센트 변화 계산
  - 📊 계산 과정 로깅 기능 포함
- **notion_tools**: Notion API 연동 도구들 (기존)
- **notion_client**: 체계적인 Notion API 클라이언트 (신규)

### Notion API 기능

새로 구현된 Notion API 클라이언트는 다음과 같은 기능을 제공합니다:

#### 📄 페이지 관리

- **GET** `/api/v1/notion/pages/{page_id}` - 페이지 조회
- **POST** `/api/v1/notion/pages` - 페이지 생성
- **PUT** `/api/v1/notion/pages/{page_id}` - 페이지 업데이트

#### 🗄️ 데이터베이스 관리

- **GET** `/api/v1/notion/databases/{database_id}` - 데이터베이스 조회
- **POST** `/api/v1/notion/databases/{database_id}/query` - 데이터베이스 쿼리
- **POST** `/api/v1/notion/databases/{database_id}/items` - 데이터베이스 항목 생성

#### 🔧 블록 관리

- **GET** `/api/v1/notion/blocks/{block_id}` - 블록 조회
- **POST** `/api/v1/notion/blocks` - 블록 추가

#### 🔍 검색 기능

- **POST** `/api/v1/notion/search` - Notion 워크스페이스 검색

#### 🛠️ 유틸리티

- **GET** `/api/v1/notion/health` - API 상태 확인
- **GET** `/api/v1/notion/info` - API 정보 조회

### Orchestrator (오케스트레이터)

- **team.py**: 멀티 에이전트 팀 생성 및 관리

### Streamlit 웹 애플리케이션

프로젝트에는 사용자 친화적인 웹 인터페이스가 포함되어 있습니다:

#### 🏠 홈 페이지 (모니터링)

- **실시간 상태 대시보드**: 활성 실행, 완료된 실행, 등록된 노션 페이지 수 표시
- **최근 실행 기록**: 최신 10개 실행 기록 테이블
- **실행 상태 분포**: 파이 차트로 상태별 분포 시각화
- **시간대별 실행 트렌드**: 일별 실행 횟수 라인 차트
- **팀별 통계**: 팀별 실행 횟수 및 완료율 표시

#### 📋 실행 로그 페이지

- **실행 목록 조회**: 팀, 상태별 필터링 가능
- **실행 상세 정보**: 선택된 실행의 상세 정보 및 메시지 표시
- **메시지 탐색**: 에이전트별 메시지 그룹화 및 상세 내용 확인
- **실시간 업데이트**: 최신 실행 상태 및 메시지 확인

#### 📝 노션 관리 페이지

- **등록된 페이지 관리**: 등록된 노션 페이지 목록 및 상태 관리
- **페이지 등록**: 새로운 노션 페이지를 AI 배치 대상으로 등록
- **체크리스트 관리**: 노션 페이지의 투두리스트 동기화 및 관리
- **API 연결 테스트**: Notion API 연결 상태 확인

#### 🌐 URL 라우팅

각 페이지는 고유한 URL을 가지며, 사이드바에서 쉽게 이동할 수 있습니다:

- 홈: `http://localhost:8501` (기본)
- 실행 로그: 사이드바에서 "실행 로그" 선택
- 노션 관리: 사이드바에서 "노션 관리" 선택

## 🔍 디버깅 및 로깅

모든 AI 도구는 실행 과정을 로깅합니다:

### 웹 검색 로그

```
🔍 [웹 검색 시도] 검색 쿼리: 'lg cns 주식 전망'
✅ [검색 성공] 5개의 결과를 찾았습니다.
```

### 데이터 분석 로그

```
📊 [퍼센트 변화 계산] 시작 값: 61900, 종료 값: 64600
✅ [계산 완료] 퍼센트 변화: 4.36%
```

이를 통해 에이전트가 어떤 쿼리로 검색하고, 어떤 값으로 계산하는지 실시간으로 확인할 수 있습니다.

## 🔧 설정 변경

모델 변경이나 시스템 설정 변경은 `src/core/config.py`에서 수정하세요:

```python
DEFAULT_MODEL = "gemini-2.5-flash"  # 사용할 모델 변경
MAX_MESSAGES = 25                    # 최대 메시지 수
MAX_SEARCH_RESULTS = 5              # 검색 결과 개수
```

## 📚 참고 자료

- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [Gemini API](https://ai.google.dev/)
- [Tavily Search API](https://tavily.com/)
- [Notion API](https://developers.notion.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 기여 가이드

새로운 에이전트나 도구를 추가할 때는 다음 구조를 따라주세요:

1. **새 에이전트 추가**: `src/ai/agents/` 에 생성
2. **새 도구 추가**: `src/ai/tools/` 에 생성
3. **협업 로직 수정**: `src/ai/orchestrator/` 에서 관리

## 📄 라이선스

이 프로젝트는 개인 학습 및 연구 목적으로 제작되었습니다.

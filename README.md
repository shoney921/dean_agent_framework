# Dean Framework

AutoGen 기반 웹 검색 및 데이터 분석 에이전트 시스템

## 📂 프로젝트 구조

```
dean_framework/
├── src/                           # 소스 코드 루트
│   ├── core/                      # ⚙️ 핵심 설정 및 데이터 모델
│   │   ├── __init__.py
│   │   └── config.py             # 환경 설정 및 상수
│   │
│   └── ai/                        # 🤖 AI 컴포넌트 패키지
│       ├── __init__.py
│       ├── agents/                # 🧑‍💻 개별 AI 에이전트 정의
│       │   ├── __init__.py
│       │   ├── base.py           # 기본 에이전트 설정
│       │   ├── web_search_agent.py
│       │   └── data_analyst_agent.py
│       │
│       ├── tools/                 # 🛠️ AI 에이전트용 도구 세트
│       │   ├── __init__.py
│       │   ├── web_search_tool.py
│       │   ├── data_analysis_tool.py
│       │   └── notion_tools.py
│       │
│       └── orchestrator/          # 🔗 에이전트 상호작용 및 흐름 제어
│           ├── __init__.py
│           └── team.py
│
├── tests/                         # 🧪 테스트 코드
├── autogen_chat_example/         # 📦 기존 코드 백업 (레거시)
├── main.py                        # 🚀 애플리케이션 시작점
├── requirements.txt               # 프로젝트 의존성
├── .env                          # 환경변수 파일 (gitignore)
├── .cursorrules                  # 커서 룰
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

```bash
python main.py
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
- **notion_tools**: Notion API 연동 도구들

### Orchestrator (오케스트레이터)

- **team.py**: 멀티 에이전트 팀 생성 및 관리

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

## 🤝 기여 가이드

새로운 에이전트나 도구를 추가할 때는 다음 구조를 따라주세요:

1. **새 에이전트 추가**: `src/ai/agents/` 에 생성
2. **새 도구 추가**: `src/ai/tools/` 에 생성
3. **협업 로직 수정**: `src/ai/orchestrator/` 에서 관리

## 📄 라이선스

이 프로젝트는 개인 학습 및 연구 목적으로 제작되었습니다.

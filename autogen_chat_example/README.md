# AutoGen 멀티 에이전트 시스템

Gemini 모델을 사용하여 웹 검색과 데이터 분석을 수행하는 멀티 에이전트 시스템입니다.

## 프로젝트 구조

```
autogen_chat_example/
├── config.py                 # 시스템 설정 및 상수 정의
├── tools.py                  # 공통 도구 함수들
├── main.py                   # 메인 실행 파일
├── team.py                   # 팀 관리 및 실행 유틸리티
├── agents/                   # 에이전트 모듈
│   ├── __init__.py
│   ├── base.py              # 공통 기본 설정
│   ├── web_search_agent.py  # 웹 검색 에이전트
│   └── data_analyst_agent.py # 데이터 분석 에이전트
└── autogen_agent_backup.py  # 기존 통합 파일 (백업)
```

## 주요 컴포넌트

### 1. config.py

- API 키 및 모델 설정
- 시스템 제한 설정 (최대 메시지 수, 검색 결과 수)
- 에이전트 시스템 메시지 정의

### 2. tools.py

- `search_web_tool`: Tavily API를 사용한 웹 검색
- `percentage_change_tool`: 퍼센트 변화 계산

### 3. agents/

#### base.py

- `create_model_client`: Gemini 모델 클라이언트 생성
- `print_model_info`: 사용 가능한 모델 정보 출력

#### web_search_agent.py

- 웹 검색에 특화된 에이전트
- 독립 실행 및 테스트 가능

#### data_analyst_agent.py

- 데이터 분석 및 계산에 특화된 에이전트
- 독립 실행 및 테스트 가능

### 4. team.py

- `create_team`: 여러 에이전트로 구성된 팀 생성
- `run_team_task`: 팀 작업 실행 및 스트리밍 출력
- 독립 실행 및 테스트 가능

### 5. main.py

- 전체 시스템을 통합하여 실행하는 메인 파일

## 실행 방법

### 1. 전체 시스템 실행

```bash
cd autogen_chat_example
python main.py
```

### 2. 개별 에이전트 테스트

#### 웹 검색 에이전트만 테스트

```bash
cd autogen_chat_example
python -m agents.web_search_agent
```

#### 데이터 분석 에이전트만 테스트

```bash
cd autogen_chat_example
python -m agents.data_analyst_agent
```

### 3. 팀 기능 테스트

```bash
cd autogen_chat_example
python team.py
```

## 환경 설정

`.env` 파일에 다음 환경 변수를 설정하세요:

```env
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

## 모델 변경

`config.py` 파일에서 `DEFAULT_MODEL` 상수를 변경하여 다른 Gemini 모델을 사용할 수 있습니다:

```python
DEFAULT_MODEL = "gemini-2.5-flash"  # 원하는 모델로 변경
```

사용 가능한 모델 목록은 `AVAILABLE_GEMINI_MODELS`에서 확인할 수 있습니다.

## 작업 예시

```python
# main.py에서 task 변수를 수정하여 다양한 질문 가능
task = "lg cns 주식 전망은 어떤지 알아봐줘"
```

## 주요 개선 사항

1. **모듈화**: 각 에이전트가 독립적인 파일로 분리되어 유지보수가 쉬움
2. **독립 테스트**: 각 에이전트를 개별적으로 테스트 가능
3. **재사용성**: 공통 기능을 base.py와 tools.py로 분리하여 재사용 가능
4. **확장성**: 새로운 에이전트를 쉽게 추가할 수 있는 구조
5. **명확한 책임**: 각 모듈이 명확한 역할을 가짐

## 문제 해결

### Import 오류 발생 시

각 에이전트 파일에서 상위 디렉토리를 Python 경로에 추가하는 코드가 포함되어 있습니다:

```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### SSL 인증서 오류 발생 시

`main.py`와 각 에이전트 테스트 코드에 SSL 검증 비활성화 설정이 포함되어 있습니다.

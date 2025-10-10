# 실행 가이드

리팩토링 후 에이전트를 개별적으로 또는 팀으로 실행할 수 있습니다.

## 실행 방법

### 방법 1: 직접 파일 실행 (프로젝트 루트에서)

```bash
# 가상환경 활성화
source venv/bin/activate

# 웹 검색 에이전트 테스트
python3 autogen_chat_example/agents/web_search_agent.py

# 데이터 분석 에이전트 테스트
python3 autogen_chat_example/agents/data_analyst_agent.py

# 팀 실행 테스트
python3 autogen_chat_example/team.py

# 메인 프로그램 실행
python3 autogen_chat_example/main.py
```

### 방법 2: 모듈로 실행 (autogen_chat_example 디렉토리에서)

```bash
# 가상환경 활성화
source venv/bin/activate

cd autogen_chat_example

# 웹 검색 에이전트 테스트
python -m agents.web_search_agent

# 데이터 분석 에이전트 테스트
python -m agents.data_analyst_agent

# 팀 실행
python team.py

# 메인 프로그램 실행
python main.py
```

## 테스트 예시

### 1. 웹 검색 에이전트 단독 테스트

```bash
python3 autogen_chat_example/agents/web_search_agent.py
```

- "lg cns 주식 전망은 어떤지 알아봐줘" 질문에 대한 웹 검색 결과를 반환합니다.

### 2. 데이터 분석 에이전트 단독 테스트

```bash
python3 autogen_chat_example/agents/data_analyst_agent.py
```

- 퍼센트 변화 계산 등 데이터 분석 기능을 테스트합니다.

### 3. 팀 통합 테스트

```bash
python3 autogen_chat_example/team.py
```

- 웹 검색과 데이터 분석 에이전트가 협업하여 작업을 수행합니다.

### 4. 전체 시스템 실행

```bash
python3 autogen_chat_example/main.py
```

- 전체 멀티 에이전트 시스템을 실행합니다.

## 주의사항

1. **가상환경 활성화**: 항상 먼저 가상환경을 활성화해야 합니다.

   ```bash
   source venv/bin/activate
   ```

2. **현재 디렉토리**: 프로젝트 루트 디렉토리(`dean_framework`)에서 실행하는 것을 권장합니다.

3. **환경 변수**: `.env` 파일이 올바르게 설정되어 있는지 확인하세요.
   - `GEMINI_API_KEY`
   - `TAVILY_API_KEY`

## 문제 해결

### ImportError 발생 시

- 프로젝트 루트 디렉토리에서 실행하고 있는지 확인
- 가상환경이 활성화되어 있는지 확인

### SSL 오류 발생 시

- 각 파일에 SSL 검증 비활성화 코드가 포함되어 있습니다.
- 필요시 config.py에서 추가 설정을 조정할 수 있습니다.

# Notion Tools 빠른 설정 가이드

## 1. 패키지 설치

```bash
cd /Users/a80613/Documents/dean_framework
pip install notion-client
```

또는:

```bash
pip install -r requirements.txt
```

## 2. Notion Integration 생성

1. [Notion Developers 페이지](https://www.notion.so/my-integrations) 접속
2. **"+ New integration"** 클릭
3. Integration 정보 입력:
   - **Name**: AutoGen Notion Bot (원하는 이름)
   - **Associated workspace**: 사용할 워크스페이스 선택
   - **Type**: Internal
4. **"Submit"** 클릭
5. **Internal Integration Secret** 복사 (이것이 API 키입니다)

## 3. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가:

```env
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 4. Notion 페이지/데이터베이스 연결

Integration이 Notion 페이지나 데이터베이스에 접근하려면 연결이 필요합니다:

### 방법 1: 페이지에서 연결

1. Notion 페이지 열기
2. 오른쪽 상단의 **"..."** 메뉴 클릭
3. **"Connections"** → **"Add connection"** 선택
4. 생성한 Integration 선택 (예: AutoGen Notion Bot)

### 방법 2: 데이터베이스에서 연결

1. 데이터베이스 페이지 열기
2. 동일하게 **"..."** → **"Connections"** → Integration 선택

## 5. 페이지/데이터베이스 ID 확인

### 페이지 ID

페이지를 브라우저에서 열면 URL이 다음과 같습니다:

```
https://www.notion.so/페이지제목-{32자리ID}?...
```

예시:

```
https://www.notion.so/My-Project-abc123def456...
                           ^^^^^^^^^^^^^^^^ 이 부분이 ID
```

### 데이터베이스 ID

데이터베이스의 경우:

```
https://www.notion.so/{32자리ID}?v=...
```

## 6. 테스트

간단한 테스트 스크립트:

```python
from notion_tools import search_notion

# Notion 워크스페이스에서 페이지 검색
result = search_notion(query="", filter_type="page")

if result["success"]:
    print(f"접근 가능한 페이지: {result['count']}개")
    for page in result["results"]:
        print(f"  - {page.get('title', 'No title')}")
        print(f"    ID: {page['id']}")
else:
    print(f"오류: {result['message']}")
```

터미널에서 실행:

```bash
cd /Users/a80613/Documents/dean_framework/autogen_chat_example
python -c "from notion_tools import search_notion; result = search_notion(''); print(f\"Success: {result['success']}\")"
```

## 7. 예제 실행

제공된 예제 파일 실행:

```bash
python notion_example.py
```

예제 파일 내의 주석을 해제하고 실제 ID로 변경하여 다양한 기능을 테스트할 수 있습니다.

## 문제 해결

### "Unauthorized" 오류

- `.env` 파일의 `NOTION_API_KEY`가 올바른지 확인
- Integration이 페이지/데이터베이스에 연결되어 있는지 확인

### "Object not found" 오류

- 페이지/데이터베이스 ID가 올바른지 확인
- Integration이 해당 페이지에 접근 권한이 있는지 확인

### "Invalid request" 오류

- 데이터베이스 항목 생성 시 properties 구조가 스키마와 일치하는지 확인
- `get_database_schema()` 함수로 스키마를 먼저 확인

## 다음 단계

1. `NOTION_TOOLS_GUIDE.md` - 상세한 함수 사용 가이드
2. `notion_example.py` - 다양한 사용 예제
3. AutoGen Agent와 통합하여 자동화된 Notion 관리 구현

## 유용한 링크

- [Notion API 공식 문서](https://developers.notion.com/)
- [notion-client Python SDK](https://github.com/ramnes/notion-sdk-py)
- [Notion API Reference](https://developers.notion.com/reference)

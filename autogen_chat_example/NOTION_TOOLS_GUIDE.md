# Notion Tools 사용 가이드

이 가이드는 `notion_tools.py`에서 제공하는 Notion API 도구들의 사용 방법을 설명합니다.

## 설치 및 설정

### 1. 패키지 설치

```bash
pip install notion-client
```

또는 requirements.txt를 통해 설치:

```bash
pip install -r requirements.txt
```

### 2. Notion API 키 설정

1. [Notion Developers](https://www.notion.so/my-integrations)에서 새로운 Integration을 생성합니다.
2. API 키를 복사합니다.
3. `.env` 파일에 다음을 추가합니다:

```env
NOTION_API_KEY=your_notion_api_key_here
```

### 3. Notion 페이지/데이터베이스 연결

생성한 Integration을 사용하려는 Notion 페이지나 데이터베이스에 연결해야 합니다:

1. Notion 페이지 또는 데이터베이스를 엽니다
2. 오른쪽 상단의 "..." 메뉴 클릭
3. "Connections" → "Add connection" 선택
4. 생성한 Integration을 선택

## 주요 함수

### 1. create_notion_page()

새로운 Notion 페이지를 생성합니다.

```python
from notion_tools import create_notion_page

result = create_notion_page(
    parent_page_id="your-parent-page-id",
    title="새로운 페이지 제목",
    content="페이지 내용"
)

if result["success"]:
    print(f"페이지 생성 성공: {result['url']}")
```

**Parameters:**

- `parent_page_id` (str): 부모 페이지의 ID
- `title` (str): 페이지 제목
- `content` (str, optional): 페이지 내용

**Returns:**

```python
{
    "success": True,
    "page_id": "페이지 ID",
    "url": "페이지 URL",
    "message": "성공 메시지"
}
```

### 2. read_notion_page()

Notion 페이지 정보를 읽습니다.

```python
from notion_tools import read_notion_page

result = read_notion_page(page_id="your-page-id")

if result["success"]:
    print(f"제목: {result['title']}")
    print(f"내용: {result['content']}")
```

**Parameters:**

- `page_id` (str): 읽을 페이지의 ID

**Returns:**

```python
{
    "success": True,
    "page_id": "페이지 ID",
    "title": "페이지 제목",
    "content": "페이지 내용",
    "url": "페이지 URL",
    "created_time": "생성 시간",
    "last_edited_time": "최종 수정 시간"
}
```

### 3. update_notion_page()

Notion 페이지를 업데이트합니다.

```python
from notion_tools import update_notion_page

result = update_notion_page(
    page_id="your-page-id",
    title="새로운 제목"
)
```

**Parameters:**

- `page_id` (str): 업데이트할 페이지의 ID
- `title` (str, optional): 새로운 제목
- `archived` (bool, optional): 아카이브 여부

### 4. append_block_to_page()

페이지에 새로운 블록을 추가합니다.

```python
from notion_tools import append_block_to_page

# 문단 추가
result = append_block_to_page(
    page_id="your-page-id",
    content="추가할 내용",
    block_type="paragraph"
)

# 제목 추가
result = append_block_to_page(
    page_id="your-page-id",
    content="제목",
    block_type="heading_1"
)

# 불릿 리스트 추가
result = append_block_to_page(
    page_id="your-page-id",
    content="리스트 항목",
    block_type="bulleted_list_item"
)
```

**Parameters:**

- `page_id` (str): 페이지 ID
- `content` (str): 추가할 내용
- `block_type` (str): 블록 타입
  - `paragraph` (기본값)
  - `heading_1`, `heading_2`, `heading_3`
  - `bulleted_list_item`
  - `numbered_list_item`
  - `toggle`
  - `quote`
  - `callout`

### 5. query_notion_database()

Notion 데이터베이스를 쿼리합니다.

```python
from notion_tools import query_notion_database

# 기본 쿼리
result = query_notion_database(database_id="your-database-id")

# 필터가 있는 쿼리
filter_conditions = {
    "property": "Status",
    "select": {
        "equals": "In Progress"
    }
}

result = query_notion_database(
    database_id="your-database-id",
    filter_conditions=filter_conditions
)

# 정렬이 있는 쿼리
sorts = [
    {
        "property": "Created",
        "direction": "descending"
    }
]

result = query_notion_database(
    database_id="your-database-id",
    sorts=sorts
)

if result["success"]:
    print(f"총 {result['count']}개의 항목을 찾았습니다.")
    for item in result["results"]:
        print(f"- {item['properties']}")
```

**Parameters:**

- `database_id` (str): 데이터베이스 ID
- `filter_conditions` (Dict, optional): 필터 조건
- `sorts` (List[Dict], optional): 정렬 조건
- `page_size` (int): 페이지 크기 (기본값: 100)

### 6. create_database_item()

데이터베이스에 새로운 항목을 추가합니다.

```python
from notion_tools import create_database_item

properties = {
    "Name": {
        "title": [
            {
                "text": {
                    "content": "새로운 항목"
                }
            }
        ]
    },
    "Status": {
        "select": {
            "name": "In Progress"
        }
    },
    "Priority": {
        "number": 5
    },
    "Due Date": {
        "date": {
            "start": "2025-10-15"
        }
    }
}

result = create_database_item(
    database_id="your-database-id",
    properties=properties
)
```

**Parameters:**

- `database_id` (str): 데이터베이스 ID
- `properties` (Dict): 항목 속성 (데이터베이스 스키마에 맞춰 구성)

### 7. search_notion()

Notion 워크스페이스에서 페이지나 데이터베이스를 검색합니다.

```python
from notion_tools import search_notion

# 전체 검색
result = search_notion(query="프로젝트")

# 페이지만 검색
result = search_notion(
    query="프로젝트",
    filter_type="page"
)

# 데이터베이스만 검색
result = search_notion(
    query="작업",
    filter_type="database"
)

if result["success"]:
    for item in result["results"]:
        print(f"{item['title']} - {item['url']}")
```

**Parameters:**

- `query` (str): 검색 쿼리
- `filter_type` (str, optional): 필터 타입 ("page" 또는 "database")
- `sort_direction` (str): 정렬 방향 ("ascending" 또는 "descending")

### 8. get_database_schema()

데이터베이스의 스키마 정보를 가져옵니다.

```python
from notion_tools import get_database_schema

result = get_database_schema(database_id="your-database-id")

if result["success"]:
    print(f"데이터베이스: {result['title']}")
    print("속성:")
    for prop_name, prop_info in result["properties"].items():
        print(f"  - {prop_name}: {prop_info['type']}")
```

**Parameters:**

- `database_id` (str): 데이터베이스 ID

## 에러 처리

모든 함수는 성공 여부를 나타내는 `success` 필드를 반환합니다:

```python
result = read_notion_page(page_id="invalid-id")

if not result["success"]:
    print(f"에러: {result['message']}")
    print(f"상세 에러: {result['error']}")
```

## Notion ID 찾기

### 페이지 ID 찾기

1. Notion 페이지를 브라우저에서 엽니다
2. URL에서 ID를 확인합니다:
   ```
   https://www.notion.so/페이지제목-{PAGE_ID}?...
   ```
3. 하이픈(-)을 제거하지 말고 그대로 사용합니다

### 데이터베이스 ID 찾기

1. 데이터베이스를 브라우저에서 엽니다
2. URL에서 ID를 확인합니다:
   ```
   https://www.notion.so/{DATABASE_ID}?v=...
   ```

## AutoGen Agent와 통합

이 툴들을 AutoGen Agent에서 사용하는 예시:

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from notion_tools import create_notion_page, search_notion

# Agent 생성
notion_agent = AssistantAgent(
    name="notion_agent",
    model_client=model_client,
    tools=[create_notion_page, search_notion],
    system_message="당신은 Notion API를 사용하여 페이지를 관리하는 에이전트입니다."
)
```

## 주의사항

1. **API 키 보안**: `.env` 파일을 `.gitignore`에 추가하여 API 키가 노출되지 않도록 주의하세요.
2. **Rate Limiting**: Notion API는 요청 제한이 있으므로 과도한 요청을 피하세요.
3. **권한**: Integration이 접근하려는 페이지/데이터베이스에 연결되어 있는지 확인하세요.
4. **ID 형식**: Notion ID는 하이픈이 포함된 UUID 형식입니다.

## 예제: 완전한 워크플로우

```python
from notion_tools import (
    search_notion,
    create_notion_page,
    append_block_to_page,
    query_notion_database,
    create_database_item
)

# 1. 페이지 검색
search_result = search_notion(query="프로젝트 관리")
if search_result["success"] and search_result["results"]:
    parent_page_id = search_result["results"][0]["id"]

    # 2. 새 페이지 생성
    page_result = create_notion_page(
        parent_page_id=parent_page_id,
        title="새로운 작업",
        content="작업 설명"
    )

    if page_result["success"]:
        new_page_id = page_result["page_id"]

        # 3. 페이지에 블록 추가
        append_block_to_page(
            page_id=new_page_id,
            content="추가 정보",
            block_type="paragraph"
        )

        print(f"작업 완료! URL: {page_result['url']}")
```

## 참고 자료

- [Notion API 공식 문서](https://developers.notion.com/)
- [notion-client Python SDK](https://github.com/ramnes/notion-sdk-py)

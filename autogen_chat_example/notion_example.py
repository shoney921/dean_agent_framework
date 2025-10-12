"""
Notion Tools 사용 예제

이 파일은 notion_tools.py의 다양한 함수들을 사용하는 방법을 보여줍니다.
"""

import urllib3
import warnings

# ============================================================================
# 전역 SSL 검증 비활성화 설정
# ============================================================================
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

from notion_tools import (
    create_notion_page,
    read_notion_page,
    update_notion_page,
    append_block_to_page,
    append_block_children,
    append_multiple_blocks,
    query_notion_database,
    create_database_item,
    search_notion,
    get_database_schema
)


def example_search_and_create_page():
    """
    예제 1: 페이지 검색 후 새 페이지 생성
    """
    print("\n=== 예제 1: 페이지 검색 및 생성 ===")
    
    # 1. 페이지 검색
    search_result = search_notion(query="TO DO LIST", filter_type="page")
    
    if not search_result["success"]:
        print(f"검색 실패: {search_result['message']}")
        return
    
    print(f"검색 결과: {search_result['count']}개의 페이지를 찾았습니다.")
    
    if search_result["results"]:
        for item in search_result["results"]:
            print(f"  - {item.get('title', 'No title')} ({item['id']})")
        
        # 첫 번째 결과를 부모 페이지로 사용
        parent_page_id = search_result["results"][0]["id"]
        
        # 2. 새 페이지 생성
        create_result = create_notion_page(
            parent_page_id=parent_page_id,
            title="AutoGen으로 생성한 페이지",
            content="이 페이지는 notion_tools.py를 사용하여 자동으로 생성되었습니다."
        )
        
        if create_result["success"]:
            print(f"\n페이지 생성 성공!")
            print(f"  URL: {create_result['url']}")
            print(f"  ID: {create_result['page_id']}")
            
            # 3. 생성한 페이지에 블록 추가
            append_result = append_block_to_page(
                page_id=create_result['page_id'],
                content="추가된 문단입니다.",
                block_type="paragraph"
            )
            
            if append_result["success"]:
                print("  블록 추가 성공!")
        else:
            print(f"페이지 생성 실패: {create_result['message']}")


def example_read_page(page_id: str):
    """
    예제 2: 페이지 읽기
    
    Args:
        page_id: 읽을 페이지의 ID
    """
    print("\n=== 예제 2: 페이지 읽기 ===")
    
    result = read_notion_page(page_id=page_id)
    
    if result["success"]:
        print(f"제목: {result['title']}")
        print(f"페이지 ID: {result['page_id']}")
        print(f"URL: {result['url']}")
        print(f"생성 시간: {result['created_time']}")
        print(f"최종 수정: {result['last_edited_time']}")
        
        print(f"\n총 {len(result['blocks'])}개의 블록:")
        print("-" * 70)
        
        # 블록 순서대로 출력
        for block in result['blocks']:
            index = block['index']
            block_type = block['type']
            content = block.get('content', '')
            
            print(f"\n[{index}] {block_type.upper()}")
            print(f"    Block ID: {block['block_id']}")
            
            if block_type == 'to_do':
                # 할 일 항목
                checked = "✓" if block.get('checked', False) else "☐"
                print(f"    {checked} {content}")
                
            elif block_type == 'code':
                # 코드 블록
                language = block.get('language', 'plain text')
                print(f"    언어: {language}")
                print(f"    코드:\n{content}")
                
            elif block_type in ['heading_1', 'heading_2', 'heading_3']:
                # 제목
                print(f"    {content}")
                
            elif block_type == 'bulleted_list_item':
                # 글머리 기호 목록
                print(f"    • {content}")
                
            elif block_type == 'numbered_list_item':
                # 번호 목록
                print(f"    {index + 1}. {content}")
                
            elif block_type == 'quote':
                # 인용문
                print(f"    \"{content}\"")
                
            elif block_type == 'paragraph':
                # 일반 문단
                print(f"    {content}")
                
            else:
                # 기타 블록 타입
                print(f"    내용: {content}")
                if 'raw_type' in block:
                    print(f"    (지원되지 않는 타입: {block['raw_type']})")
        
        print("\n" + "-" * 70)
        
        # 할 일 항목만 별도로 요약
        todos = [b for b in result['blocks'] if b['type'] == 'to_do']
        if todos:
            print(f"\n📋 할 일 목록 요약 (총 {len(todos)}개):")
            for todo in todos:
                checked = "✓" if todo.get('checked', False) else "☐"
                print(f"  [{todo['index']}] {checked} {todo['content']}")
        
    else:
        print(f"페이지 읽기 실패: {result['message']}")


def example_update_page(page_id: str):
    """
    예제 3: 페이지 업데이트
    
    Args:
        page_id: 업데이트할 페이지의 ID
    """
    print("\n=== 예제 3: 페이지 업데이트 ===")
    
    result = update_notion_page(
        page_id=page_id,
        title="업데이트된 제목"
    )
    
    if result["success"]:
        print("페이지 업데이트 성공!")
    else:
        print(f"페이지 업데이트 실패: {result['message']}")


def example_query_database(database_id: str):
    """
    예제 4: 데이터베이스 쿼리
    
    Args:
        database_id: 쿼리할 데이터베이스의 ID
    """
    print("\n=== 예제 4: 데이터베이스 쿼리 ===")
    
    # 기본 쿼리
    result = query_notion_database(database_id=database_id, page_size=5)
    
    if result["success"]:
        print(f"총 {result['count']}개의 항목을 찾았습니다.")
        
        for i, item in enumerate(result["results"], 1):
            print(f"\n{i}. 항목 정보:")
            print(f"   ID: {item['page_id']}")
            print(f"   속성:")
            for prop_name, prop_value in item["properties"].items():
                print(f"     - {prop_name}: {prop_value}")
    else:
        print(f"데이터베이스 쿼리 실패: {result['message']}")


def example_filtered_query(database_id: str):
    """
    예제 5: 필터가 적용된 데이터베이스 쿼리
    
    Args:
        database_id: 쿼리할 데이터베이스의 ID
    """
    print("\n=== 예제 5: 필터 적용 쿼리 ===")
    
    # Status가 "In Progress"인 항목만 필터링
    filter_conditions = {
        "property": "Status",
        "select": {
            "equals": "In Progress"
        }
    }
    
    # 정렬 조건 (Created 날짜 기준 내림차순)
    sorts = [
        {
            "property": "Created",
            "direction": "descending"
        }
    ]
    
    result = query_notion_database(
        database_id=database_id,
        filter_conditions=filter_conditions,
        sorts=sorts
    )
    
    if result["success"]:
        print(f"'In Progress' 상태인 항목: {result['count']}개")
        for item in result["results"]:
            print(f"  - {item['properties']}")
    else:
        print(f"쿼리 실패: {result['message']}")


def example_create_database_item(database_id: str):
    """
    예제 6: 데이터베이스 항목 생성
    
    Args:
        database_id: 데이터베이스 ID
    """
    print("\n=== 예제 6: 데이터베이스 항목 생성 ===")
    
    # 데이터베이스 스키마를 먼저 확인하는 것이 좋습니다
    schema_result = get_database_schema(database_id=database_id)
    
    if not schema_result["success"]:
        print(f"스키마 조회 실패: {schema_result['message']}")
        return
    
    print(f"데이터베이스: {schema_result['title']}")
    print("속성:")
    for prop_name, prop_info in schema_result["properties"].items():
        print(f"  - {prop_name}: {prop_info['type']}")
    
    # 예시: 새 항목 생성 (실제 속성은 데이터베이스 스키마에 맞춰 수정해야 합니다)
    properties = {
        "Name": {  # Title 타입 속성
            "title": [
                {
                    "text": {
                        "content": "AutoGen으로 생성한 항목"
                    }
                }
            ]
        }
        # 추가 속성은 데이터베이스 스키마에 맞춰 추가하세요
        # 예:
        # "Status": {
        #     "select": {
        #         "name": "In Progress"
        #     }
        # },
        # "Priority": {
        #     "number": 5
        # }
    }
    
    result = create_database_item(
        database_id=database_id,
        properties=properties
    )
    
    if result["success"]:
        print(f"\n항목 생성 성공!")
        print(f"  URL: {result['url']}")
        print(f"  ID: {result['page_id']}")
    else:
        print(f"항목 생성 실패: {result['message']}")


def example_get_database_schema(database_id: str):
    """
    예제 7: 데이터베이스 스키마 조회
    
    Args:
        database_id: 데이터베이스 ID
    """
    print("\n=== 예제 7: 데이터베이스 스키마 조회 ===")
    
    result = get_database_schema(database_id=database_id)
    
    if result["success"]:
        print(f"데이터베이스: {result['title']}")
        print(f"URL: {result['url']}")
        print(f"생성 시간: {result['created_time']}")
        print("\n속성:")
        
        for prop_name, prop_info in result["properties"].items():
            print(f"  - {prop_name}")
            print(f"    타입: {prop_info['type']}")
            
            if "options" in prop_info:
                print(f"    옵션: {', '.join(prop_info['options'])}")
    else:
        print(f"스키마 조회 실패: {result['message']}")


def example_append_block_children(page_id: str):
    """
    예제 8: 특정 블록 아래에 자식 블록 추가
    
    Args:
        page_id: 페이지 ID
    """
    print("\n=== 예제 8: 블록 아래에 자식 블록 추가 ===")
    
    # 1. 먼저 페이지를 읽어서 블록 정보 가져오기
    page_result = read_notion_page(page_id=page_id)
    
    if not page_result["success"]:
        print(f"페이지 읽기 실패: {page_result['message']}")
        return
    
    print(f"페이지 제목: {page_result['title']}")
    print(f"총 {len(page_result['blocks'])}개의 블록")
    
    if not page_result['blocks']:
        print("블록이 없습니다. 먼저 블록을 추가해주세요.")
        return

    # 2. to_do 타입 블록 찾기
    todo_blocks = [block for block in page_result['blocks'] if block['type'] == 'to_do']
    print(f"할 일 블록: {todo_blocks}")
    if not todo_blocks:
        print("\n할 일(to_do) 블록이 없습니다.")
        return
    
    for todo_block in todo_blocks:
    # 3. 해당 블록 아래에 자식 블록 추가
        result = append_block_children(
            block_id=todo_block['block_id'],
            content="이것은 할 일 블록의 자식 블록입니다.",
            block_type="paragraph"
        )
        if result["success"]:
            print(f"\n자식 블록 추가 성공!")
            print(f"  - 생성된 블록 ID: {result['block_id']}")
            print(f"  - 부모 블록 ID: {result['parent_block_id']}")
        else:
            print(f"자식 블록 추가 실패: {result['message']}")


def example_append_multiple_blocks(page_id: str):
    """
    예제 9: 여러 블록을 한 번에 추가
    
    Args:
        page_id: 페이지 ID
    """
    print("\n=== 예제 9: 여러 블록 한 번에 추가 ===")
    
    # 추가할 블록들 정의
    blocks = [
        {"content": "제목: 작업 목록", "type": "heading_2"},
        {"content": "첫 번째 할 일", "type": "to_do", "checked": False},
        {"content": "두 번째 할 일", "type": "to_do", "checked": True},
        {"content": "설명 문단입니다.", "type": "paragraph"},
        {"content": "print('Hello, World!')", "type": "code", "language": "python"},
        {"content": "중요한 인용문", "type": "quote"},
        {"content": "글머리 기호 항목 1", "type": "bulleted_list_item"},
        {"content": "글머리 기호 항목 2", "type": "bulleted_list_item"},
    ]
    
    print(f"{len(blocks)}개의 블록을 추가합니다...")
    
    result = append_multiple_blocks(
        parent_id=page_id,
        blocks=blocks,
        is_page=True
    )
    
    if result["success"]:
        print(f"\n블록 추가 성공!")
        print(f"  - 추가된 블록 개수: {result['count']}")
        print(f"  - 부모 ID: {result['parent_id']}")
        print(f"\n생성된 블록 ID 목록:")
        for i, block_id in enumerate(result['block_ids'], 1):
            print(f"    {i}. {block_id}")
    else:
        print(f"블록 추가 실패: {result['message']}")


def example_nested_blocks(page_id: str):
    """
    예제 10: 중첩된 블록 구조 만들기
    
    Args:
        page_id: 페이지 ID
    """
    print("\n=== 예제 10: 중첩된 블록 구조 만들기 ===")
    
    # 1. 페이지에 부모 블록 추가
    parent_result = append_block_to_page(
        page_id=page_id,
        content="프로젝트 계획",
        block_type="heading_2"
    )
    
    if not parent_result["success"]:
        print(f"부모 블록 추가 실패: {parent_result['message']}")
        return
    
    parent_block_id = parent_result['block_id']
    print(f"부모 블록 생성 완료: {parent_block_id}")
    
    # 2. 부모 블록 아래에 여러 자식 블록 추가
    child_blocks = [
        {"content": "1단계: 기획", "type": "to_do", "checked": True},
        {"content": "2단계: 개발", "type": "to_do", "checked": False},
        {"content": "3단계: 테스트", "type": "to_do", "checked": False},
        {"content": "4단계: 배포", "type": "to_do", "checked": False},
    ]
    
    result = append_multiple_blocks(
        parent_id=parent_block_id,
        blocks=child_blocks,
        is_page=False
    )
    
    if result["success"]:
        print(f"\n중첩 구조 생성 완료!")
        print(f"  - 부모 블록: {parent_block_id}")
        print(f"  - 자식 블록 개수: {result['count']}")
        print(f"\n구조:")
        print(f"  📄 프로젝트 계획 (heading_2)")
        for i, block_id in enumerate(result['block_ids'], 1):
            print(f"    ├─ {child_blocks[i-1]['content']} (to_do)")
    else:
        print(f"자식 블록 추가 실패: {result['message']}")


def main():
    """
    메인 함수: 예제 실행
    
    사용하려면 실제 Notion 페이지/데이터베이스 ID로 변경하세요.
    """
    print("Notion Tools 예제 실행")
    print("=" * 50)
    
    # 주의: 아래의 ID들을 실제 Notion ID로 변경해야 합니다
    TEST_PAGE_ID = "2893d406-af73-80c2-a3dc-ee569c7ed46e"
    
    # 예제 1: 페이지 검색 및 생성
    # example_search_and_create_page()
    
    # 예제 2: 페이지 읽기 (페이지 ID 필요)
    example_read_page(page_id=TEST_PAGE_ID)
    
    # 예제 3: 페이지 업데이트 (페이지 ID 필요)
    # example_update_page(page_id=TEST_PAGE_ID)
    
    # 예제 4: 데이터베이스 쿼리 (데이터베이스 ID 필요)
    # example_query_database(database_id="your-database-id-here")
    
    # 예제 5: 필터 적용 쿼리 (데이터베이스 ID 필요)
    # example_filtered_query(database_id="your-database-id-here")
    
    # 예제 6: 데이터베이스 항목 생성 (데이터베이스 ID 필요)
    # example_create_database_item(database_id="your-database-id-here")
    
    # 예제 7: 데이터베이스 스키마 조회 (데이터베이스 ID 필요)
    # example_get_database_schema(database_id="your-database-id-here")
    
    # 예제 8: 특정 블록 아래에 자식 블록 추가
    example_append_block_children(page_id=TEST_PAGE_ID)
    
    # 예제 9: 여러 블록 한 번에 추가
    # example_append_multiple_blocks(page_id=TEST_PAGE_ID)
    
    # 예제 10: 중첩된 블록 구조 만들기
    # example_nested_blocks(page_id=TEST_PAGE_ID)
    
    print("\n" + "=" * 50)
    print("예제 실행 완료!")
    print("\n주의: 주석 처리된 예제를 실행하려면")
    print("실제 Notion 페이지/데이터베이스 ID로 변경해야 합니다.")


if __name__ == "__main__":
    main()


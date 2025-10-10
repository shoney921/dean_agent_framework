"""
Notion Tools 사용 예제

이 파일은 notion_tools.py의 다양한 함수들을 사용하는 방법을 보여줍니다.
"""

from notion_tools import (
    create_notion_page,
    read_notion_page,
    update_notion_page,
    append_block_to_page,
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
    search_result = search_notion(query="프로젝트", filter_type="page")
    
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
        print(f"내용: {result['content'][:100]}...")  # 처음 100자만 출력
        print(f"생성 시간: {result['created_time']}")
        print(f"최종 수정: {result['last_edited_time']}")
        print(f"URL: {result['url']}")
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


def main():
    """
    메인 함수: 예제 실행
    
    사용하려면 실제 Notion 페이지/데이터베이스 ID로 변경하세요.
    """
    print("Notion Tools 예제 실행")
    print("=" * 50)
    
    # 주의: 아래의 ID들을 실제 Notion ID로 변경해야 합니다
    
    # 예제 1: 페이지 검색 및 생성
    example_search_and_create_page()
    
    # 예제 2: 페이지 읽기 (페이지 ID 필요)
    # example_read_page(page_id="your-page-id-here")
    
    # 예제 3: 페이지 업데이트 (페이지 ID 필요)
    # example_update_page(page_id="your-page-id-here")
    
    # 예제 4: 데이터베이스 쿼리 (데이터베이스 ID 필요)
    # example_query_database(database_id="your-database-id-here")
    
    # 예제 5: 필터 적용 쿼리 (데이터베이스 ID 필요)
    # example_filtered_query(database_id="your-database-id-here")
    
    # 예제 6: 데이터베이스 항목 생성 (데이터베이스 ID 필요)
    # example_create_database_item(database_id="your-database-id-here")
    
    # 예제 7: 데이터베이스 스키마 조회 (데이터베이스 ID 필요)
    # example_get_database_schema(database_id="your-database-id-here")
    
    print("\n" + "=" * 50)
    print("예제 실행 완료!")
    print("\n주의: 주석 처리된 예제를 실행하려면")
    print("실제 Notion 페이지/데이터베이스 ID로 변경해야 합니다.")


if __name__ == "__main__":
    main()


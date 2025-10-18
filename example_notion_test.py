#!/usr/bin/env python3
"""
Notion API 클라이언트 간단한 사용 예제

이 파일은 notion_client.py의 기본적인 사용법을 보여줍니다.
"""

import os
import sys
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.client.notion_client import (
    search_notion,
    read_notion_page,
    append_block_to_page,
    create_notion_page
)

# 환경 변수 로드
load_dotenv()

def simple_test():
    """간단한 테스트 예제"""
    print("🔍 간단한 Notion API 테스트")
    print("=" * 40)
    
    # 1. 페이지 검색
    print("\n1. 페이지 검색")
    search_result = search_notion("테스트", filter_type="page")
    
    if search_result["success"] and search_result["results"]:
        page = search_result["results"][0]
        page_id = page["id"]
        page_title = page.get("title", "제목 없음")
        
        print(f"   찾은 페이지: {page_title}")
        print(f"   페이지 ID: {page_id}")
        
        # 2. 페이지 내용 읽기
        print("\n2. 페이지 내용 읽기")
        page_data = read_notion_page(page_id)
        
        if page_data["success"]:
            print(f"   페이지 제목: {page_data['title']}")
            print(f"   블록 수: {len(page_data['blocks'])}")
            
            # 처음 3개 블록만 출력
            for i, block in enumerate(page_data["blocks"][:3]):
                content = block.get("content", "")[:30] + "..." if len(block.get("content", "")) > 30 else block.get("content", "")
                print(f"   블록 {i+1} ({block['type']}): {content}")
        
        # 3. 블록 추가
        print("\n3. 블록 추가")
        append_result = append_block_to_page(
            page_id, 
            "🤖 AI 에이전트가 추가한 테스트 블록입니다!", 
            "paragraph"
        )
        
        if append_result["success"]:
            print("   ✅ 블록 추가 성공!")
        else:
            print(f"   ❌ 블록 추가 실패: {append_result.get('error', '알 수 없는 오류')}")
    
    else:
        print("   ❌ 검색 결과가 없습니다.")

def create_test_page_example():
    """새 페이지 생성 예제"""
    print("\n📝 새 페이지 생성 예제")
    print("=" * 40)
    
    # 부모 페이지 ID를 입력받아야 합니다
    parent_page_id = input("부모 페이지 ID를 입력하세요: ").strip()
    
    if not parent_page_id:
        print("❌ 부모 페이지 ID가 필요합니다.")
        return
    
    # 새 페이지 생성
    result = create_notion_page(
        parent_page_id=parent_page_id,
        title="AI 테스트 페이지",
        content="이 페이지는 AI 에이전트에 의해 생성되었습니다."
    )
    
    if result["success"]:
        print(f"✅ 페이지 생성 성공!")
        print(f"   페이지 ID: {result['page_id']}")
        print(f"   URL: {result['url']}")
        
        # 생성된 페이지에 블록 추가
        append_result = append_block_to_page(
            result["page_id"],
            "추가된 첫 번째 블록입니다.",
            "heading_2"
        )
        
        if append_result["success"]:
            print("✅ 블록 추가도 성공!")
    else:
        print(f"❌ 페이지 생성 실패: {result.get('error', '알 수 없는 오류')}")

if __name__ == "__main__":
    # 환경 변수 확인
    if not os.getenv("NOTION_API_KEY"):
        print("❌ NOTION_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("   .env 파일에 NOTION_API_KEY를 설정해주세요.")
        exit(1)
    
    print("Notion API 클라이언트 예제")
    print("1. 간단한 테스트")
    print("2. 새 페이지 생성")
    
    choice = input("\n실행할 예제를 선택하세요 (1 또는 2): ").strip()
    
    if choice == "1":
        simple_test()
    elif choice == "2":
        create_test_page_example()
    else:
        print("❌ 잘못된 선택입니다.")

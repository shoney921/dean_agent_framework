#!/usr/bin/env python3
"""
Notion API 클라이언트 테스트 스크립트

이 스크립트는 notion_client.py의 주요 기능들을 테스트합니다:
1. 페이지명으로 페이지 검색
2. 페이지 블록 조회
3. 블록 추가
4. 기타 Notion API 기능들
"""

import os
import sys
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.client.notion_client import (
    get_notion_client,
    search_notion,
    read_notion_page,
    append_block_to_page,
    create_notion_page,
    query_notion_database,
    get_database_schema,
    list_notion_pages,
    list_pages_by_parent
)

# 환경 변수 로드
load_dotenv()

class NotionTester:
    """Notion API 기능을 테스트하는 클래스"""
    
    def __init__(self):
        """테스터 초기화"""
        self.notion = None
        self.test_results = []
        
    def setup(self) -> bool:
        """테스트 환경 설정"""
        try:
            self.notion = get_notion_client()
            print("✅ Notion 클라이언트 초기화 성공")
            return True
        except Exception as e:
            print(f"❌ Notion 클라이언트 초기화 실패: {e}")
            return False
    
    def log_test_result(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """테스트 결과 로깅"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        if data and isinstance(data, dict) and data.get("error"):
            print(f"   오류: {data['error']}")
    
    def test_search_page_by_name(self, page_name: str) -> Optional[Dict]:
        """페이지명으로 페이지 검색 테스트"""
        print(f"\n🔍 페이지명 '{page_name}'으로 검색 중...")
        
        result = search_notion(query=page_name, filter_type="page")
        
        if result["success"]:
            pages = result["results"]
            if pages:
                print(f"   검색된 페이지 수: {len(pages)}")
                for i, page in enumerate(pages[:3]):  # 최대 3개만 표시
                    print(f"   {i+1}. {page.get('title', '제목 없음')} (ID: {page['id']})")
                
                # 첫 번째 페이지 반환
                return pages[0]
            else:
                print("   검색 결과가 없습니다.")
                return None
        else:
            print(f"   검색 실패: {result.get('error', '알 수 없는 오류')}")
            return None
    
    def test_read_page_blocks(self, page_id: str) -> bool:
        """페이지 블록 조회 테스트"""
        print(f"\n📖 페이지 블록 조회 중... (ID: {page_id})")
        
        result = read_notion_page(page_id)
        
        if result["success"]:
            print(f"   페이지 제목: {result['title']}")
            print(f"   블록 수: {len(result['blocks'])}")
            print(f"   URL: {result['url']}")
            
            # 블록 정보 출력 (최대 5개)
            blocks = result["blocks"]
            for block in blocks:
                block_type = block["type"]
                content = block.get("content", "")[:50] + "..." if len(block.get("content", "")) > 50 else block.get("content", "")
                print(f"   - [{block['index']}] {block_type}: {content}")
            
            self.log_test_result("페이지 블록 조회", True, f"{len(result['blocks'])}개 블록 조회 성공", result)
            return True
        else:
            self.log_test_result("페이지 블록 조회", False, "블록 조회 실패", result)
            return False
    
    def test_append_block(self, page_id: str, content: str, block_type: str = "paragraph") -> bool:
        """블록 추가 테스트"""
        print(f"\n➕ 블록 추가 중... (타입: {block_type})")
        print(f"   내용: {content[:50]}{'...' if len(content) > 50 else ''}")
        
        result = append_block_to_page(page_id, content, block_type)
        
        if result["success"]:
            print(f"   블록 ID: {result.get('block_id', 'N/A')}")
            self.log_test_result("블록 추가", True, "블록 추가 성공", result)
            return True
        else:
            self.log_test_result("블록 추가", False, "블록 추가 실패", result)
            return False
    
    def test_create_page(self, parent_page_id: str, title: str, content: str = None) -> Optional[str]:
        """페이지 생성 테스트"""
        print(f"\n📝 새 페이지 생성 중...")
        print(f"   제목: {title}")
        print(f"   부모 페이지 ID: {parent_page_id}")
        
        result = create_notion_page(parent_page_id, title, content)
        
        if result["success"]:
            print(f"   생성된 페이지 ID: {result['page_id']}")
            print(f"   URL: {result['url']}")
            self.log_test_result("페이지 생성", True, "페이지 생성 성공", result)
            return result["page_id"]
        else:
            self.log_test_result("페이지 생성", False, "페이지 생성 실패", result)
            return None
    
    def test_database_query(self, database_id: str) -> bool:
        """데이터베이스 쿼리 테스트"""
        print(f"\n🗄️ 데이터베이스 쿼리 중... (ID: {database_id})")
        
        result = query_notion_database(database_id, page_size=5)
        
        if result["success"]:
            print(f"   조회된 항목 수: {result['count']}")
            for i, item in enumerate(result["results"][:3]):
                print(f"   {i+1}. {item.get('properties', {}).get('Name', '제목 없음')} (ID: {item['page_id']})")
            
            self.log_test_result("데이터베이스 쿼리", True, f"{result['count']}개 항목 조회 성공", result)
            return True
        else:
            self.log_test_result("데이터베이스 쿼리", False, "데이터베이스 쿼리 실패", result)
            return False
    
    def test_database_schema(self, database_id: str) -> bool:
        """데이터베이스 스키마 조회 테스트"""
        print(f"\n📋 데이터베이스 스키마 조회 중... (ID: {database_id})")
        
        result = get_database_schema(database_id)
        
        if result["success"]:
            print(f"   데이터베이스 제목: {result['title']}")
            print(f"   속성 수: {len(result['properties'])}")
            for prop_name, prop_info in result["properties"].items():
                print(f"   - {prop_name}: {prop_info['type']}")
            
            self.log_test_result("데이터베이스 스키마 조회", True, f"{len(result['properties'])}개 속성 조회 성공", result)
            return True
        else:
            self.log_test_result("데이터베이스 스키마 조회", False, "스키마 조회 실패", result)
            return False
    
    def run_comprehensive_test(self, page_name: str):
        """종합 테스트 실행"""
        print("🚀 Notion API 종합 테스트 시작")
        print("=" * 50)
        
        # 1. 페이지 검색
        found_page = self.test_search_page_by_name(page_name)
        
        if found_page:
            page_id = found_page["id"]
            
            # 2. 페이지 블록 조회
            self.test_read_page_blocks(page_id)
            
            # 3. 블록 추가 테스트
            test_content = f"🤖 AI 에이전트가 추가한 테스트 블록입니다. (시간: {self._get_current_time()})"
            self.test_append_block(page_id, test_content, "paragraph")
            
            # 4. 다양한 블록 타입 추가 테스트
            self.test_append_block(page_id, "✅ 체크리스트 항목", "to_do")
            self.test_append_block(page_id, "인용구 테스트", "callout")
            
            # 5. 업데이트된 블록 다시 조회
            print(f"\n🔄 업데이트된 페이지 블록 재조회...")
            self.test_read_page_blocks(page_id)
        
        # 6. 새 페이지 생성 테스트 (부모 페이지 ID가 있는 경우)
        # if parent_page_id:
        #     test_title = f"AI 테스트 페이지 - {self._get_current_time()}"
        #     test_content = "이 페이지는 AI 에이전트에 의해 자동 생성된 테스트 페이지입니다."
        #     new_page_id = self.test_create_page(parent_page_id, test_title, test_content)
            
        #     if new_page_id:
        #         # 새로 생성된 페이지에 블록 추가
        #         self.test_append_block(new_page_id, "새 페이지에 추가된 첫 번째 블록입니다.", "paragraph")
        
        # # 7. 데이터베이스 테스트 (데이터베이스 ID가 있는 경우)
        # if database_id:
        #     self.test_database_schema(database_id)
        #     self.test_database_query(database_id)
        
        # 테스트 결과 요약
        self.print_test_summary()
    
    def print_test_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 50)
        print("📊 테스트 결과 요약")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - successful_tests
        
        print(f"총 테스트: {total_tests}")
        print(f"성공: {successful_tests} ✅")
        print(f"실패: {failed_tests} ❌")
        print(f"성공률: {(successful_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 실패한 테스트:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test_name']}: {result['message']}")
    
    def _get_current_time(self) -> str:
        """현재 시간을 문자열로 반환"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """메인 함수"""
    print("🔧 Notion API 클라이언트 테스트 도구")
    print("=" * 50)
    
    # 환경 변수 확인
    if not os.getenv("NOTION_API_KEY"):
        print("❌ NOTION_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("   .env 파일에 NOTION_API_KEY를 설정해주세요.")
        return
    
    # 테스터 초기화
    tester = NotionTester()
    
    if not tester.setup():
        return
    
    # 사용자 입력 받기
    print("\n📝 테스트 설정을 입력해주세요:")
    page_name = "to do list"
    
    if not page_name:
        print("❌ 페이지명을 입력해주세요.")
        return

    pages = list_notion_pages()

    for page in pages["pages"]:
        print(page["page_id"])
        print(page["title"])
        print(page["url"])

    # 종합 테스트 실행
    # tester.run_comprehensive_test(page_name)


if __name__ == "__main__":
    main()

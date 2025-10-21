"""
배치 시스템 테스트 스크립트
"""

import asyncio
import requests
import time
from datetime import datetime

# API 기본 URL
BASE_URL = "http://localhost:8000/api/v1"

def test_batch_system():
    """배치 시스템을 테스트합니다."""
    
    print("🚀 배치 시스템 테스트 시작")
    print("=" * 50)
    
    # 테스트용 notion_page_id (실제 값으로 변경 필요)
    test_page_id = "test-page-123"
    
    try:
        # 1. 배치 시작
        print("1️⃣ 배치 시작 테스트")
        start_response = requests.post(
            f"{BASE_URL}/batch/start",
            json={"notion_page_id": test_page_id}
        )
        
        if start_response.status_code == 200:
            result = start_response.json()
            print(f"✅ 배치 시작 성공: {result['message']}")
            print(f"   - 페이지 ID: {result['notion_page_id']}")
            print(f"   - 시작 시간: {result['start_time']}")
            print(f"   - 종료 예정: {result['end_time']}")
        else:
            print(f"❌ 배치 시작 실패: {start_response.text}")
            return
        
        # 2. 배치 상태 확인
        print("\n2️⃣ 배치 상태 확인")
        status_response = requests.get(f"{BASE_URL}/batch/status/{test_page_id}")
        
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"✅ 배치 상태 조회 성공")
            print(f"   - DB 상태: {status['db_status']}")
            print(f"   - 실행 중: {status['is_running']}")
            print(f"   - 마지막 실행: {status['db_last_run_at']}")
        else:
            print(f"❌ 배치 상태 조회 실패: {status_response.text}")
        
        # 3. 전체 배치 상태 확인
        print("\n3️⃣ 전체 배치 상태 확인")
        all_status_response = requests.get(f"{BASE_URL}/batch/status")
        
        if all_status_response.status_code == 200:
            all_status = all_status_response.json()
            print(f"✅ 전체 배치 상태 조회 성공")
            print(f"   - 실행 중인 배치: {all_status['running_batches']}")
            print(f"   - 실행 중인 배치 수: {all_status['running_count']}")
            print(f"   - 스케줄러 작업: {all_status['scheduler_jobs']}")
        else:
            print(f"❌ 전체 배치 상태 조회 실패: {all_status_response.text}")
        
        # 4. 잠시 대기 (배치가 실행되는 것을 확인)
        print("\n4️⃣ 배치 실행 대기 (10초)")
        time.sleep(10)
        
        # 5. 다시 상태 확인
        print("\n5️⃣ 배치 상태 재확인")
        status_response = requests.get(f"{BASE_URL}/batch/status/{test_page_id}")
        
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"✅ 배치 상태 재조회 성공")
            print(f"   - DB 상태: {status['db_status']}")
            print(f"   - 실행 중: {status['is_running']}")
            print(f"   - 마지막 실행: {status['db_last_run_at']}")
        else:
            print(f"❌ 배치 상태 재조회 실패: {status_response.text}")
        
        # 6. 배치 중지 (테스트용)
        print("\n6️⃣ 배치 중지 테스트")
        stop_response = requests.post(f"{BASE_URL}/batch/stop/{test_page_id}")
        
        if stop_response.status_code == 200:
            result = stop_response.json()
            print(f"✅ 배치 중지 성공: {result['message']}")
            print(f"   - 페이지 ID: {result['notion_page_id']}")
            print(f"   - 중지 시간: {result['end_time']}")
        else:
            print(f"❌ 배치 중지 실패: {stop_response.text}")
        
        # 7. 최종 상태 확인
        print("\n7️⃣ 최종 배치 상태 확인")
        final_status_response = requests.get(f"{BASE_URL}/batch/status/{test_page_id}")
        
        if final_status_response.status_code == 200:
            final_status = final_status_response.json()
            print(f"✅ 최종 배치 상태 조회 성공")
            print(f"   - DB 상태: {final_status['db_status']}")
            print(f"   - 실행 중: {final_status['is_running']}")
            print(f"   - 마지막 실행: {final_status['db_last_run_at']}")
        else:
            print(f"❌ 최종 배치 상태 조회 실패: {final_status_response.text}")
        
        print("\n🎉 배치 시스템 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    test_batch_system()

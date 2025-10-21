# 배치 시스템 사용 가이드

## 개요

이 배치 시스템은 Notion 페이지의 투두리스트를 자동으로 처리하는 시스템입니다. Python의 `APScheduler`를 사용하여 1분 주기로 실행되며, 15분 후 자동으로 종료됩니다.

## 주요 기능

- ✅ **자동 배치 실행**: 1분 주기로 pending 상태의 투두 항목 처리
- ✅ **자동 종료**: 15분 후 자동으로 배치 종료
- ✅ **상태 관리**: NotionBatchStatus 테이블을 통한 상태 추적
- ✅ **에러 처리**: 문제 발생 시 failed 상태로 변경
- ✅ **Notion 연동**: 완료된 작업을 Notion에 자동으로 기록

## API 엔드포인트

### 1. 배치 시작

```http
POST /api/v1/batch/start
Content-Type: application/json

{
    "notion_page_id": "your-notion-page-id"
}
```

**응답:**

```json
{
  "success": true,
  "message": "배치 작업이 시작되었습니다. 15분 후 자동 종료됩니다.",
  "notion_page_id": "your-notion-page-id",
  "start_time": "2024-01-01T10:00:00",
  "end_time": "2024-01-01T10:15:00"
}
```

### 2. 배치 중지

```http
POST /api/v1/batch/stop/{notion_page_id}
```

**응답:**

```json
{
  "success": true,
  "message": "배치 작업이 중지되었습니다.",
  "notion_page_id": "your-notion-page-id",
  "end_time": "2024-01-01T10:05:00"
}
```

### 3. 배치 상태 조회

```http
GET /api/v1/batch/status/{notion_page_id}
```

**응답:**

```json
{
  "success": true,
  "notion_page_id": "your-notion-page-id",
  "db_status": "running",
  "db_message": "배치 작업 진행 중 - 5개 항목 처리",
  "db_last_run_at": "2024-01-01T10:03:00",
  "is_running": true,
  "running_info": {
    "notion_page_id": "your-notion-page-id",
    "start_time": "2024-01-01T10:00:00",
    "end_time": "2024-01-01T10:15:00",
    "status": "running"
  }
}
```

### 4. 전체 배치 상태 조회

```http
GET /api/v1/batch/status
```

**응답:**

```json
{
  "success": true,
  "running_batches": ["page-1", "page-2"],
  "running_count": 2,
  "scheduler_jobs": ["batch_page-1", "batch_page-2"]
}
```

## 배치 처리 흐름

1. **배치 시작**: `NotionBatchStatus` 상태를 `running`으로 변경
2. **투두 조회**: 해당 페이지의 `status = pending`인 투두 항목들 조회
3. **작업 처리**: 각 투두 항목에 대해 실제 작업 수행
4. **상태 업데이트**: 완료된 투두의 상태를 `done`으로 변경
5. **Notion 연동**: 완료된 작업을 Notion 페이지에 기록
6. **자동 종료**: 15분 후 자동으로 배치 종료 및 상태를 `completed`로 변경

## 상태 관리

### NotionBatchStatus 상태

- `idle`: 대기 상태
- `running`: 실행 중
- `completed`: 정상 완료
- `failed`: 오류 발생

### NotionTodo 상태

- `pending`: 처리 대기
- `done`: 처리 완료
- `skipped`: 건너뜀

## 에러 처리

- 개별 투두 처리 실패 시 해당 항목만 건너뛰고 계속 진행
- 전체 배치 실패 시 `NotionBatchStatus` 상태를 `failed`로 변경
- Notion API 오류 시 배치를 중단하지 않고 로그만 기록

## 테스트

배치 시스템을 테스트하려면:

```bash
# 1. 서버 시작
python main.py

# 2. 다른 터미널에서 테스트 실행
python test_batch.py
```

## 주의사항

1. **동시 실행 제한**: 같은 페이지에 대해 동시에 여러 배치를 실행할 수 없습니다.
2. **자동 종료**: 배치는 15분 후 자동으로 종료되므로 장시간 실행이 필요한 경우 별도 처리가 필요합니다.
3. **Notion API 제한**: Notion API 호출 제한을 고려하여 적절한 간격으로 요청을 보냅니다.
4. **리소스 관리**: 배치 서비스 종료 시 모든 실행 중인 배치를 정리합니다.

## 확장 가능성

- **커스텀 작업 로직**: `_process_todo_item` 메서드를 수정하여 실제 작업 로직 구현
- **배치 시간 조정**: 스케줄러 설정을 통해 실행 주기 및 지속 시간 변경
- **알림 기능**: 배치 완료 시 슬랙, 이메일 등으로 알림 전송
- **모니터링**: 배치 실행 현황을 실시간으로 모니터링할 수 있는 대시보드 구현

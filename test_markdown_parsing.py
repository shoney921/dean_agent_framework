#!/usr/bin/env python3
"""
마크다운 파싱 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.client.notion_client import parse_markdown_to_notion_blocks, parse_rich_text_formatting
import json

def test_markdown_parsing():
    """
    마크다운 파싱 기능을 테스트합니다.
    """
    test_text = """# 메인 제목
## 서브 제목
### 소제목

일반 텍스트입니다.

- **볼드 텍스트**가 포함된 불릿 포인트
- *이탤릭 텍스트*가 포함된 불릿 포인트
- `코드 텍스트`가 포함된 불릿 포인트

1. 번호 리스트 첫 번째
2. 번호 리스트 두 번째

```python
def hello():
    print("Hello, World!")
```

**볼드 텍스트**와 *이탤릭 텍스트*가 섞인 문단입니다."""
    
    print("=== 마크다운 파싱 테스트 ===")
    print("원본 텍스트:")
    print(test_text)
    print("\n" + "="*50 + "\n")
    
    blocks = parse_markdown_to_notion_blocks(test_text)
    print("변환된 Notion 블록:")
    print(json.dumps(blocks, indent=2, ensure_ascii=False))
    
    return blocks

def test_rich_text_formatting():
    """
    Rich Text 포맷팅을 테스트합니다.
    """
    test_cases = [
        "**볼드 텍스트**",
        "*이탤릭 텍스트*", 
        "`코드 텍스트`",
        "~~취소선 텍스트~~",
        "**볼드**와 *이탤릭*이 섞인 텍스트",
        "`코드`와 **볼드**가 섞인 텍스트"
    ]
    
    print("\n=== Rich Text 포맷팅 테스트 ===")
    for test_case in test_cases:
        print(f"\n원본: {test_case}")
        rich_text = parse_rich_text_formatting(test_case)
        print(f"변환: {json.dumps(rich_text, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    # 마크다운 파싱 테스트 실행
    test_markdown_parsing()
    test_rich_text_formatting()

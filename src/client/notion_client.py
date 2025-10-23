"""
Notion API를 다루는 도구 함수들

이 모듈은 Notion API를 사용하여 페이지 생성, 읽기, 업데이트, 
데이터베이스 쿼리 등의 기능을 제공합니다.
"""

import datetime
from datetime import timezone
import os
from typing import Dict, List, Optional, Any
from notion_client import Client
from dotenv import load_dotenv
import httpx
import ssl

# 환경 변수 로드
load_dotenv()

# Notion API 클라이언트 초기화
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

def get_notion_client() -> Client:
    """Notion 클라이언트 인스턴스를 반환합니다. (SSL 검증 비활성화)"""
    if not NOTION_API_KEY:
        raise ValueError("NOTION_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
    
    # SSL 검증을 비활성화한 httpx 클라이언트 생성
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    http_client = httpx.Client(verify=False)
    
    return Client(auth=NOTION_API_KEY, client=http_client)


def create_notion_page(
    parent_page_id: str,
    title: str,
    content: Optional[str] = None
) -> Dict[str, Any]:
    """
    새로운 Notion 페이지를 생성합니다.
    
    Args:
        parent_page_id (str): 부모 페이지의 ID
        title (str): 페이지 제목
        content (str, optional): 페이지 내용
        
    Returns:
        Dict: 생성된 페이지 정보
    """
    try:
        notion = get_notion_client()
        
        # 페이지 속성 구성
        properties = {
            "title": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        }
        
        # 자식 블록 구성 (내용이 있는 경우)
        children = []
        if content:
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content
                            }
                        }
                    ]
                }
            })
        
        # 페이지 생성
        response = notion.pages.create(
            parent={"page_id": parent_page_id},
            properties=properties,
            children=children if children else None
        )
        
        return {
            "success": True,
            "page_id": response["id"],
            "url": response["url"],
            "message": f"페이지 '{title}'가 성공적으로 생성되었습니다."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"페이지 생성 중 오류가 발생했습니다: {str(e)}"
        }


def read_notion_page(page_id: str) -> Dict[str, Any]:
    """
    Notion 페이지 정보를 읽습니다.
    
    Args:
        page_id (str): 읽을 페이지의 ID
        
    Returns:
        Dict: 페이지 정보
            - success (bool): 성공 여부
            - page_id (str): 페이지 ID
            - title (str): 페이지 제목
            - blocks (List[Dict]): 블록 정보 리스트, 각 블록은 다음 정보를 포함:
                - index (int): 블록의 순서 (0부터 시작)
                - type (str): 블록 타입 (paragraph, to_do, heading_1, heading_2, heading_3, 
                             bulleted_list_item, numbered_list_item, code, quote 등)
                - block_id (str): 블록 ID
                - content (str): 블록의 텍스트 내용
                - checked (bool, to_do인 경우만): 체크 여부
                - language (str, code인 경우만): 코드 언어
            - url (str): 페이지 URL
            - created_time (str): 생성 시간
            - last_edited_time (str): 마지막 수정 시간
    """
    try:
        notion = get_notion_client()
        
        # 페이지 메타데이터 가져오기
        page = notion.pages.retrieve(page_id=page_id)
        
        # 페이지 블록 가져오기
        blocks = notion.blocks.children.list(block_id=page_id)
        
        # 제목 추출
        title = ""
        if "properties" in page:
            for prop_name, prop_value in page["properties"].items():
                if prop_value.get("type") == "title":
                    title_array = prop_value.get("title", [])
                    if title_array:
                        title = title_array[0].get("plain_text", "")
                    break
        
        # 블록 내용 추출 (인덱스 정보 포함)
        structured_blocks = []
        
        for index, block in enumerate(blocks.get("results", [])):
            block_type = block.get("type")
            block_data = {
                "index": index,
                "type": block_type,
                "block_id": block.get("id", "")
            }
            
            if block_type == "paragraph":
                text_array = block.get("paragraph", {}).get("rich_text", [])
                text_content = "".join([text_obj.get("plain_text", "") for text_obj in text_array])
                block_data["content"] = text_content
                
            elif block_type == "to_do":
                todo_text = block.get("to_do", {}).get("rich_text", [])
                text_content = "".join([text_obj.get("plain_text", "") for text_obj in todo_text])
                block_data["content"] = text_content
                block_data["checked"] = block.get("to_do", {}).get("checked", False)
                
            elif block_type == "heading_1":
                text_array = block.get("heading_1", {}).get("rich_text", [])
                text_content = "".join([text_obj.get("plain_text", "") for text_obj in text_array])
                block_data["content"] = text_content
                
            elif block_type == "heading_2":
                text_array = block.get("heading_2", {}).get("rich_text", [])
                text_content = "".join([text_obj.get("plain_text", "") for text_obj in text_array])
                block_data["content"] = text_content
                
            elif block_type == "heading_3":
                text_array = block.get("heading_3", {}).get("rich_text", [])
                text_content = "".join([text_obj.get("plain_text", "") for text_obj in text_array])
                block_data["content"] = text_content
                
            elif block_type == "bulleted_list_item":
                text_array = block.get("bulleted_list_item", {}).get("rich_text", [])
                text_content = "".join([text_obj.get("plain_text", "") for text_obj in text_array])
                block_data["content"] = text_content
                
            elif block_type == "numbered_list_item":
                text_array = block.get("numbered_list_item", {}).get("rich_text", [])
                text_content = "".join([text_obj.get("plain_text", "") for text_obj in text_array])
                block_data["content"] = text_content
                
            elif block_type == "code":
                text_array = block.get("code", {}).get("rich_text", [])
                text_content = "".join([text_obj.get("plain_text", "") for text_obj in text_array])
                block_data["content"] = text_content
                block_data["language"] = block.get("code", {}).get("language", "plain text")
                
            elif block_type == "quote":
                text_array = block.get("quote", {}).get("rich_text", [])
                text_content = "".join([text_obj.get("plain_text", "") for text_obj in text_array])
                block_data["content"] = text_content

            elif block_type == "callout":
                text_array = block.get("callout", {}).get("rich_text", [])
                text_content = "".join([text_obj.get("plain_text", "") for text_obj in text_array])
                block_data["content"] = text_content
                block_data["color"] = block.get("callout", {}).get("color", "default")
                
            elif block_type == "divider":
                block_data["content"] = ""
                block_data["raw_type"] = block_type
                
            elif block_type == "embed":
                block_data["content"] = ""
                block_data["raw_type"] = block_type
            else:
                # 기타 블록 타입 처리
                block_data["content"] = ""
                block_data["raw_type"] = block_type
            
            structured_blocks.append(block_data)
        
        return {
            "success": True,
            "page_id": page["id"],
            "title": title,
            "blocks": structured_blocks,
            "url": page.get("url", ""),
            "created_time": page.get("created_time", ""),
            "last_edited_time": page.get("last_edited_time", "")
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"페이지 읽기 중 오류가 발생했습니다: {str(e)}"
        }


def update_notion_page(
    page_id: str,
    title: Optional[str] = None,
    archived: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Notion 페이지를 업데이트합니다.
    
    Args:
        page_id (str): 업데이트할 페이지의 ID
        title (str, optional): 새로운 제목
        archived (bool, optional): 아카이브 여부
        
    Returns:
        Dict: 업데이트 결과
    """
    try:
        notion = get_notion_client()
        
        update_data = {}
        
        # 제목 업데이트
        if title:
            update_data["properties"] = {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            }
        
        # 아카이브 상태 업데이트
        if archived is not None:
            update_data["archived"] = archived
        
        response = notion.pages.update(page_id=page_id, **update_data)
        
        return {
            "success": True,
            "page_id": response["id"],
            "message": "페이지가 성공적으로 업데이트되었습니다."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"페이지 업데이트 중 오류가 발생했습니다: {str(e)}"
        }


def append_block_to_page(
    page_id: str,
    content: str,
    block_type: str = "paragraph"
) -> Dict[str, Any]:
    """
    Notion 페이지에 새로운 블록을 추가합니다.
    
    Args:
        page_id (str): 페이지 ID
        content (str): 추가할 내용
        block_type (str): 블록 타입 (paragraph, heading_1, heading_2, heading_3, bulleted_list_item 등)
        
    Returns:
        Dict: 추가 결과
    """
    try:
        notion = get_notion_client()
        
        # 블록 구성
        block_data = {
            "object": "block",
            "type": block_type,
            block_type: {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": content
                        }
                    }
                ]
            }
        }
        
        response = notion.blocks.children.append(
            block_id=page_id,
            children=[block_data]
        )
        
        return {
            "success": True,
            "message": f"블록이 성공적으로 추가되었습니다.",
            "block_id": response["results"][0]["id"] if response.get("results") else None
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"블록 추가 중 오류가 발생했습니다: {str(e)}"
        }


def query_notion_database(
    database_id: str,
    filter_conditions: Optional[Dict] = None,
    sorts: Optional[List[Dict]] = None,
    page_size: int = 100
) -> Dict[str, Any]:
    """
    Notion 데이터베이스를 쿼리합니다.
    
    Args:
        database_id (str): 데이터베이스 ID
        filter_conditions (Dict, optional): 필터 조건
        sorts (List[Dict], optional): 정렬 조건
        page_size (int): 페이지 크기 (기본값: 100)
        
    Returns:
        Dict: 쿼리 결과
    """
    try:
        notion = get_notion_client()
        
        query_params = {"page_size": page_size}
        
        if filter_conditions:
            query_params["filter"] = filter_conditions
        
        if sorts:
            query_params["sorts"] = sorts
        
        response = notion.databases.query(
            database_id=database_id,
            **query_params
        )
        
        # 결과 파싱
        results = []
        for page in response.get("results", []):
            page_data = {
                "page_id": page["id"],
                "url": page.get("url", ""),
                "properties": {}
            }
            
            # 속성 추출
            for prop_name, prop_value in page.get("properties", {}).items():
                prop_type = prop_value.get("type")
                
                if prop_type == "title":
                    title_array = prop_value.get("title", [])
                    page_data["properties"][prop_name] = title_array[0].get("plain_text", "") if title_array else ""
                
                elif prop_type == "rich_text":
                    text_array = prop_value.get("rich_text", [])
                    page_data["properties"][prop_name] = text_array[0].get("plain_text", "") if text_array else ""
                
                elif prop_type == "number":
                    page_data["properties"][prop_name] = prop_value.get("number")
                
                elif prop_type == "select":
                    select_obj = prop_value.get("select")
                    page_data["properties"][prop_name] = select_obj.get("name", "") if select_obj else ""
                
                elif prop_type == "date":
                    date_obj = prop_value.get("date")
                    page_data["properties"][prop_name] = date_obj.get("start", "") if date_obj else ""
                
                elif prop_type == "checkbox":
                    page_data["properties"][prop_name] = prop_value.get("checkbox", False)
            
            results.append(page_data)
        
        return {
            "success": True,
            "count": len(results),
            "results": results,
            "has_more": response.get("has_more", False)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"데이터베이스 쿼리 중 오류가 발생했습니다: {str(e)}"
        }


def create_database_item(
    database_id: str,
    properties: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Notion 데이터베이스에 새로운 항목을 추가합니다.
    
    Args:
        database_id (str): 데이터베이스 ID
        properties (Dict): 항목 속성 (데이터베이스 스키마에 맞춰 구성)
        
    Returns:
        Dict: 생성 결과
    """
    try:
        notion = get_notion_client()
        
        response = notion.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        
        return {
            "success": True,
            "page_id": response["id"],
            "url": response.get("url", ""),
            "message": "데이터베이스 항목이 성공적으로 생성되었습니다."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"데이터베이스 항목 생성 중 오류가 발생했습니다: {str(e)}"
        }


def search_notion(
    query: str,
    filter_type: Optional[str] = None,
    sort_direction: str = "descending"
) -> Dict[str, Any]:
    """
    Notion 워크스페이스에서 페이지나 데이터베이스를 검색합니다.
    
    Args:
        query (str): 검색 쿼리
        filter_type (str, optional): 필터 타입 ("page" 또는 "database")
        sort_direction (str): 정렬 방향 ("ascending" 또는 "descending")
        
    Returns:
        Dict: 검색 결과
    """
    try:
        notion = get_notion_client()
        
        search_params = {
            "query": query,
            "sort": {
                "direction": sort_direction,
                "timestamp": "last_edited_time"
            }
        }
        
        if filter_type:
            search_params["filter"] = {
                "value": filter_type,
                "property": "object"
            }
        
        response = notion.search(**search_params)
        
        # 결과 파싱
        results = []
        for item in response.get("results", []):
            item_data = {
                "id": item["id"],
                "object": item.get("object"),
                "url": item.get("url", ""),
                "last_edited_time": item.get("last_edited_time", "")
            }
            
            # 제목 추출
            if item.get("object") == "page":
                for prop_name, prop_value in item.get("properties", {}).items():
                    if prop_value.get("type") == "title":
                        title_array = prop_value.get("title", [])
                        item_data["title"] = title_array[0].get("plain_text", "") if title_array else ""
                        break
            elif item.get("object") == "database":
                title_array = item.get("title", [])
                item_data["title"] = title_array[0].get("plain_text", "") if title_array else ""
            
            results.append(item_data)
        
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"검색 중 오류가 발생했습니다: {str(e)}"
        }


def get_database_schema(database_id: str) -> Dict[str, Any]:
    """
    Notion 데이터베이스의 스키마 정보를 가져옵니다.
    
    Args:
        database_id (str): 데이터베이스 ID
        
    Returns:
        Dict: 데이터베이스 스키마 정보
    """
    try:
        notion = get_notion_client()
        
        database = notion.databases.retrieve(database_id=database_id)
        
        # 속성 정보 추출
        properties = {}
        for prop_name, prop_value in database.get("properties", {}).items():
            properties[prop_name] = {
                "type": prop_value.get("type"),
                "id": prop_value.get("id")
            }
            
            # 추가 정보 (select, multi_select 옵션 등)
            if prop_value.get("type") == "select":
                options = prop_value.get("select", {}).get("options", [])
                properties[prop_name]["options"] = [opt.get("name") for opt in options]
            
            elif prop_value.get("type") == "multi_select":
                options = prop_value.get("multi_select", {}).get("options", [])
                properties[prop_name]["options"] = [opt.get("name") for opt in options]
        
        # 제목 추출
        title_array = database.get("title", [])
        title = title_array[0].get("plain_text", "") if title_array else ""
        
        return {
            "success": True,
            "database_id": database["id"],
            "title": title,
            "url": database.get("url", ""),
            "properties": properties,
            "created_time": database.get("created_time", ""),
            "last_edited_time": database.get("last_edited_time", "")
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"데이터베이스 스키마 조회 중 오류가 발생했습니다: {str(e)}"
        }


def list_notion_pages(
    page_size: int = 100,
    filter_type: str = "page",
    sort_direction: str = "descending"
) -> Dict[str, Any]:
    """
    Notion 워크스페이스에서 모든 페이지 목록을 가져옵니다.
    
    Args:
        page_size (int): 페이지 크기 (기본값: 100)
        filter_type (str): 필터 타입 ("page" 또는 "database", 기본값: "page")
        sort_direction (str): 정렬 방향 ("ascending" 또는 "descending", 기본값: "descending")
        
    Returns:
        Dict: 페이지 목록 정보
            - success (bool): 성공 여부
            - count (int): 페이지 개수
            - pages (List[Dict]): 페이지 목록, 각 페이지는 다음 정보를 포함:
                - page_id (str): 페이지 ID
                - title (str): 페이지 제목
                - url (str): 페이지 URL
                - object (str): 객체 타입 ("page" 또는 "database")
                - created_time (str): 생성 시간
                - last_edited_time (str): 마지막 수정 시간
                - archived (bool): 아카이브 여부
                - parent_type (str): 부모 타입 ("page_id", "database_id", "workspace")
                - parent_id (str): 부모 ID
    """
    try:
        notion = get_notion_client()
        
        # 빈 쿼리로 모든 페이지 검색
        search_params = {
            "page_size": page_size,
            "sort": {
                "direction": sort_direction,
                "timestamp": "last_edited_time"
            },
            "filter": {
                "value": filter_type,
                "property": "object"
            }
        }
        
        response = notion.search(**search_params)
        
        # 결과 파싱
        pages = []
        for item in response.get("results", []):
            page_data = {
                "page_id": item["id"],
                "url": item.get("url", ""),
                "object": item.get("object"),
                "created_time": item.get("created_time", ""),
                "last_edited_time": item.get("last_edited_time", ""),
                "archived": item.get("archived", False)
            }
            
            # 부모 정보 추출
            parent = item.get("parent", {})
            page_data["parent_type"] = parent.get("type", "")
            page_data["parent_id"] = parent.get("page_id") or parent.get("database_id") or ""
            
            # 제목 추출
            title = ""
            if item.get("object") == "page":
                # 페이지의 경우 properties에서 제목 추출
                for prop_name, prop_value in item.get("properties", {}).items():
                    if prop_value.get("type") == "title":
                        title_array = prop_value.get("title", [])
                        title = title_array[0].get("plain_text", "") if title_array else ""
                        break
            elif item.get("object") == "database":
                # 데이터베이스의 경우 title 필드에서 추출
                title_array = item.get("title", [])
                title = title_array[0].get("plain_text", "") if title_array else ""
            
            page_data["title"] = title
            pages.append(page_data)
        
        return {
            "success": True,
            "count": len(pages),
            "pages": pages,
            "has_more": response.get("has_more", False),
            "next_cursor": response.get("next_cursor", "")
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"페이지 목록 조회 중 오류가 발생했습니다: {str(e)}"
        }


def list_pages_by_parent(
    parent_id: str,
    parent_type: str = "page",
    page_size: int = 100
) -> Dict[str, Any]:
    """
    특정 부모 페이지나 데이터베이스 하위의 페이지 목록을 가져옵니다.
    
    Args:
        parent_id (str): 부모 페이지 또는 데이터베이스 ID
        parent_type (str): 부모 타입 ("page" 또는 "database", 기본값: "page")
        page_size (int): 페이지 크기 (기본값: 100)
        
    Returns:
        Dict: 하위 페이지 목록 정보
            - success (bool): 성공 여부
            - count (int): 페이지 개수
            - pages (List[Dict]): 페이지 목록
            - parent_info (Dict): 부모 정보
    """
    try:
        notion = get_notion_client()
        
        if parent_type == "database":
            # 데이터베이스의 경우 쿼리 사용
            response = notion.databases.query(
                database_id=parent_id,
                page_size=page_size
            )
            
            # 부모 정보 가져오기
            parent_info = get_database_schema(parent_id)
            
        else:
            # 페이지의 경우 자식 블록에서 페이지 타입만 필터링
            response = notion.blocks.children.list(
                block_id=parent_id,
                page_size=page_size
            )
            
            # 부모 페이지 정보 가져오기
            parent_page = notion.pages.retrieve(page_id=parent_id)
            parent_info = {
                "success": True,
                "page_id": parent_page["id"],
                "title": "",
                "url": parent_page.get("url", "")
            }
            
            # 부모 페이지 제목 추출
            for prop_name, prop_value in parent_page.get("properties", {}).items():
                if prop_value.get("type") == "title":
                    title_array = prop_value.get("title", [])
                    parent_info["title"] = title_array[0].get("plain_text", "") if title_array else ""
                    break
        
        # 결과 파싱
        pages = []
        for item in response.get("results", []):
            # 페이지 타입인 경우만 포함
            if item.get("type") == "child_page":
                page_data = {
                    "page_id": item["id"],
                    "title": item.get("child_page", {}).get("title", ""),
                    "url": "",  # child_page는 URL이 없음 default
                    "object": "page",
                    "created_time": item.get("created_time", ""),
                    "last_edited_time": item.get("last_edited_time", ""),
                    "archived": item.get("archived", False),
                    "parent_type": parent_type,
                    "parent_id": parent_id
                }
                pages.append(page_data)
            
            elif item.get("object") == "page":
                # 데이터베이스 쿼리 결과인 경우
                page_data = {
                    "page_id": item["id"],
                    "url": item.get("url", ""),
                    "object": "page",
                    "created_time": item.get("created_time", ""),
                    "last_edited_time": item.get("last_edited_time", ""),
                    "archived": item.get("archived", False),
                    "parent_type": parent_type,
                    "parent_id": parent_id
                }
                
                # 제목 추출
                title = ""
                for prop_name, prop_value in item.get("properties", {}).items():
                    if prop_value.get("type") == "title":
                        title_array = prop_value.get("title", [])
                        title = title_array[0].get("plain_text", "") if title_array else ""
                        break
                
                page_data["title"] = title
                pages.append(page_data)
        
        return {
            "success": True,
            "count": len(pages),
            "pages": pages,
            "parent_info": parent_info,
            "has_more": response.get("has_more", False),
            "next_cursor": response.get("next_cursor", "")
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"하위 페이지 목록 조회 중 오류가 발생했습니다: {str(e)}"
        }


def append_completion_message(block_id: str, completion_text: str = None) -> dict:
    """
    Notion 블록 아래에 완료 메시지를 추가합니다.
    
    Args:
        block_id (str): 완료 메시지를 추가할 블록 ID
        completion_text (str, optional): 사용자 정의 완료 메시지. 없으면 기본 메시지 사용
        
    Returns:
        dict: API 응답 결과
    """
    try:
        if not completion_text:
            completion_text = f" 작업 완료: {datetime.datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}"
        
        response = get_notion_client().blocks.children.append(
            block_id=block_id,
            children=[
                {
                    "type": "callout",
                    "callout": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": completion_text
                                }
                            }
                        ],
                        "icon": {
                            "emoji": "🤖"
                        },
                        "color": "gray_background"
                    }
                }
            ]
        )
        return {
            "success": True,
            "block_id": response.get("id"),
            "message": "완료 메시지가 성공적으로 추가되었습니다."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"완료 메시지 추가 중 오류가 발생했습니다: {str(e)}"
        }

def parse_rich_text_formatting(text: str) -> list:
    """
    텍스트에서 마크다운 포맷팅을 파싱하여 Notion rich_text 형식으로 변환합니다.
    
    Args:
        text (str): 마크다운 텍스트
        
    Returns:
        list: Notion rich_text 배열
    """
    import re
    
    rich_text = []
    current_pos = 0
    
    # 정규식 패턴들
    patterns = [
        (r'\*\*(.*?)\*\*', 'bold'),      # **볼드**
        (r'\*(.*?)\*', 'italic'),        # *이탤릭*
        (r'`(.*?)`', 'code'),            # `코드`
        (r'~~(.*?)~~', 'strikethrough'), # ~~취소선~~
    ]
    
    # 모든 매치 찾기
    matches = []
    for pattern, format_type in patterns:
        for match in re.finditer(pattern, text):
            matches.append((match.start(), match.end(), match.group(1), format_type))
    
    # 위치순으로 정렬
    matches.sort(key=lambda x: x[0])
    
    for start, end, content, format_type in matches:
        # 매치 전 텍스트 추가
        if current_pos < start:
            plain_text = text[current_pos:start]
            if plain_text:
                rich_text.append({"type": "text", "text": {"content": plain_text}})
        
        # 포맷된 텍스트 추가
        annotations = {}
        if format_type == 'bold':
            annotations['bold'] = True
        elif format_type == 'italic':
            annotations['italic'] = True
        elif format_type == 'code':
            annotations['code'] = True
        elif format_type == 'strikethrough':
            annotations['strikethrough'] = True
        
        rich_text.append({
            "type": "text",
            "text": {"content": content},
            "annotations": annotations
        })
        
        current_pos = end
    
    # 남은 텍스트 추가
    if current_pos < len(text):
        remaining_text = text[current_pos:]
        if remaining_text:
            rich_text.append({"type": "text", "text": {"content": remaining_text}})
    
    # 매치가 없으면 전체 텍스트를 그대로 반환
    if not matches:
        return [{"type": "text", "text": {"content": text}}]
    
    return rich_text


def parse_markdown_to_notion_blocks(text: str) -> list:
    """
    마크다운 텍스트를 Notion 블록으로 변환합니다.
    
    Args:
        text (str): 마크다운 텍스트
        
    Returns:
        list: Notion 블록 리스트
    """
    import re
    
    blocks = []
    lines = text.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
            
        # 헤딩 처리
        if line.startswith('### ') or line.startswith('#### '):
            content = line[4:]
            rich_text = parse_rich_text_formatting(content)
            blocks.append({
                "type": "heading_3",
                "heading_3": {
                    "rich_text": rich_text
                }
            })
        elif line.startswith('## '):
            content = line[3:]
            rich_text = parse_rich_text_formatting(content)
            blocks.append({
                "type": "heading_2", 
                "heading_2": {
                    "rich_text": rich_text
                }
            })
        elif line.startswith('# '):
            content = line[2:]
            rich_text = parse_rich_text_formatting(content)
            blocks.append({
                "type": "heading_1",
                "heading_1": {
                    "rich_text": rich_text
                }
            })
        # 불릿 포인트 처리
        elif line.startswith('- ') or line.startswith('* '):
            content = line[2:]
            rich_text = parse_rich_text_formatting(content)
            blocks.append({
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": rich_text
                }
            })
        # 번호 리스트 처리
        elif re.match(r'^\d+\. ', line):
            content = re.sub(r'^\d+\. ', '', line)
            rich_text = parse_rich_text_formatting(content)
            blocks.append({
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": rich_text
                }
            })
        # 구분선 처리
        elif line == '---' or line == '***' or line == '___':
            blocks.append({
                "type": "divider",
                "divider": {}
            })
        # 코드 블록 처리
        elif line.startswith('```'):
            # 코드 블록 시작
            language = line[3:].strip() or "plain text"
            code_content = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_content.append(lines[i])
                i += 1
            blocks.append({
                "type": "code",
                "code": {
                    "rich_text": [{"type": "text", "text": {"content": '\n'.join(code_content)}}],
                    "language": language
                }
            })
        # 일반 텍스트 처리
        else:
            rich_text = parse_rich_text_formatting(line)
            blocks.append({
                "type": "paragraph",
                "paragraph": {
                    "rich_text": rich_text
                }
            })
        
        i += 1
    
    return blocks


def append_completion_message_with_toggle(block_id: str, toggle_title: str, url: str, completion_text: str = None) -> dict:
    """
    Notion 블록 아래에 완료 메시지를 토글 형태로 추가합니다.
    마크다운 헤딩(## 제목)과 포맷팅을 지원합니다.
    
    Args:
        block_id (str): 완료 메시지를 추가할 블록 ID
        completion_text (str, optional): 사용자 정의 완료 메시지. 없으면 기본 메시지 사용
        
    Returns:
        dict: API 응답 결과
    """
    try:
        if not completion_text:
            completion_text = f" 작업 완료: {datetime.datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 마크다운을 Notion 블록으로 변환
        notion_blocks = parse_markdown_to_notion_blocks(completion_text)
        
        # URL이 있으면 링크 블록 추가
        if url:
            notion_blocks.append({
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "🔗 링크: ",
                            }
                        },
                        {
                            "type": "text",
                            "text": {
                                "content": url,
                                "link": {"url": url}
                            }
                        }
                    ]
                }
            })
        
        response = get_notion_client().blocks.children.append(
            block_id=block_id,
            children=[
                {
                    "type": "toggle",
                    "toggle": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"🤖 {toggle_title}"
                                }
                            }
                        ],
                        "color": "gray_background",
                        "children": notion_blocks
                    }
                }
            ]
        )
        return {
            "success": True,
            "block_id": response.get("id"),
            "message": "완료 메시지가 성공적으로 추가되었습니다."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"완료 메시지 추가 중 오류가 발생했습니다: {str(e)}"
        }
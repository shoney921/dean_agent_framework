"""
Notion API를 다루는 도구 함수들

이 모듈은 Notion API를 사용하여 페이지 생성, 읽기, 업데이트, 
데이터베이스 쿼리 등의 기능을 제공합니다.
"""

import os
from typing import Dict, List, Optional, Any
from notion_client import Client
from dotenv import load_dotenv
import httpx
import ssl

# 환경 변수 로드
load_dotenv()

# Notion API 클라이언트 초기화
from src.core.config import NOTION_API_KEY


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
                block_data["icon"] = block.get("callout", {}).get("icon", {}).get("emoji", "💡")
                block_data["content"] = block_data["icon"] + " " + text_content
                
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
    Notion 페이지에 새로운 블록을 추가합니다. (페이지 끝에 추가)
    
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


def append_block_children(
    block_id: str,
    content: str,
    block_type: str = "paragraph"
) -> Dict[str, Any]:
    """
    특정 블록 아래에 자식 블록을 추가합니다.
    
    Args:
        block_id (str): 부모 블록 ID (자식을 추가할 블록)
        content (str): 추가할 내용
        block_type (str): 블록 타입 (paragraph, heading_1, heading_2, heading_3, 
                         bulleted_list_item, numbered_list_item, to_do, code, quote 등)
        
    Returns:
        Dict: 추가 결과
            - success (bool): 성공 여부
            - message (str): 결과 메시지
            - block_id (str): 생성된 블록의 ID
            - parent_block_id (str): 부모 블록 ID
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
        
        # to_do 타입인 경우 checked 필드 추가
        if block_type == "to_do":
            block_data[block_type]["checked"] = False
        
        response = notion.blocks.children.append(
            block_id=block_id,
            children=[block_data]
        )
        
        created_block_id = response["results"][0]["id"] if response.get("results") else None
        
        return {
            "success": True,
            "message": f"블록이 성공적으로 추가되었습니다.",
            "block_id": created_block_id,
            "parent_block_id": block_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"블록 추가 중 오류가 발생했습니다: {str(e)}"
        }


def append_multiple_blocks(
    parent_id: str,
    blocks: List[Dict[str, str]],
    is_page: bool = True
) -> Dict[str, Any]:
    """
    페이지 또는 블록에 여러 개의 블록을 한 번에 추가합니다.
    
    Args:
        parent_id (str): 부모 페이지 또는 블록 ID
        blocks (List[Dict]): 추가할 블록들의 리스트
            각 블록은 {"content": "내용", "type": "블록타입"} 형태
            예: [
                {"content": "문단 내용", "type": "paragraph"},
                {"content": "할 일", "type": "to_do"},
                {"content": "제목", "type": "heading_2"}
            ]
        is_page (bool): True이면 페이지에 추가, False이면 블록에 추가
        
    Returns:
        Dict: 추가 결과
            - success (bool): 성공 여부
            - message (str): 결과 메시지
            - block_ids (List[str]): 생성된 블록들의 ID 리스트
            - count (int): 추가된 블록 개수
    """
    try:
        notion = get_notion_client()
        
        # 블록 데이터 구성
        children = []
        for block_info in blocks:
            content = block_info.get("content", "")
            block_type = block_info.get("type", "paragraph")
            
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
            
            # to_do 타입인 경우 checked 필드 추가
            if block_type == "to_do":
                checked = block_info.get("checked", False)
                block_data[block_type]["checked"] = checked
            
            # code 타입인 경우 language 필드 추가
            if block_type == "code":
                language = block_info.get("language", "plain text")
                block_data[block_type]["language"] = language
            
            children.append(block_data)
        
        response = notion.blocks.children.append(
            block_id=parent_id,
            children=children
        )
        
        block_ids = [block["id"] for block in response.get("results", [])]
        
        return {
            "success": True,
            "message": f"{len(block_ids)}개의 블록이 성공적으로 추가되었습니다.",
            "block_ids": block_ids,
            "count": len(block_ids),
            "parent_id": parent_id
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


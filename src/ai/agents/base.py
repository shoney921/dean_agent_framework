"""
에이전트 기본 설정 및 공통 함수

이 모듈은 모든 에이전트가 공통으로 사용하는 모델 클라이언트 생성 등의 기능을 제공합니다.
"""

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo

from src.core.config import DEFAULT_MODEL, GEMINI_API_KEY, AVAILABLE_GEMINI_MODELS


def create_model_client(model: str = DEFAULT_MODEL, api_key: str = GEMINI_API_KEY) -> OpenAIChatCompletionClient:
    """
    Gemini 모델 클라이언트를 생성합니다.
    
    Args:
        model (str): 사용할 Gemini 모델 이름
        api_key (str): Gemini API 키
        
    Returns:
        OpenAIChatCompletionClient: 설정된 모델 클라이언트
    """
    return OpenAIChatCompletionClient(
        model=model,
        model_info=ModelInfo(
            vision=True,
            function_calling=True,
            json_output=True,
            family="unknown",
            structured_output=True
        ),
        api_key=api_key,
    )


def print_model_info(current_model: str = DEFAULT_MODEL) -> None:
    """
    사용 가능한 Gemini 모델 정보를 출력합니다.
    
    Args:
        current_model: 현재 사용 중인 모델 이름
    """
    print("=" * 80)
    print("모델 정보 확인")
    print("=" * 80)
    print("📋 일반적으로 사용 가능한 Gemini 모델들:")
    print("-" * 50)
    
    for i, model in enumerate(AVAILABLE_GEMINI_MODELS, 1):
        status = "✅ 현재 사용 중" if model == current_model else "   "
        print(f"{status} {i}. {model}")
    
    print("-" * 50)
    print(f"현재 사용 중인 모델: {current_model}")
    print("💡 다른 모델을 사용하려면 src/core/config.py에서 DEFAULT_MODEL 상수를 변경하세요.")
    print("=" * 80)


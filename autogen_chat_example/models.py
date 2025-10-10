from autogen_core.models import UserMessage
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
import asyncio

async def main() -> None:
    az_model_client = AzureOpenAIChatCompletionClient(
        azure_deployment="gpt-4.1",
        model="gpt-4.1",
        api_version="2024-12-01-preview",
        azure_endpoint="https://innovationstudio-chatgpt.openai.azure.com/",
        api_key="f0f8a55a2d214c2e8620450153193918",  # API 키 기반 인증 사용
    )

    result = await az_model_client.create([UserMessage(content="What is the capital of France?", source="user")])
    print(result)
    await az_model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
from dataclasses import dataclass
import os
import asyncio
import certifi
import tempfile


from autogen_core import (
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TopicId,
    message_handler,
    type_subscription,
)
from autogen_core.models import ChatCompletionClient, SystemMessage, UserMessage
from autogen_ext.models.azure import AzureAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential
import os 

@dataclass
class Message:
    content: str

concept_extractor_topic_type = "ConceptExtractorAgent"
writer_topic_type = "WriterAgent"
format_proof_topic_type = "FormatProofAgent"
user_topic_type = "User"


@type_subscription(topic_type=concept_extractor_topic_type)
class ConceptExtractorAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__("A concept extractor agent.")
        self._system_message = SystemMessage(
            content=(
                "You are a marketing analyst. Given a product description, identify:\n"
                "- Key features\n"
                "- Target audience\n"
                "- Unique selling points\n\n"
            )
        )
        self._model_client = model_client

    @message_handler
    async def handle_user_description(self, message: Message, ctx: MessageContext) -> None:
        prompt = f"Product description: {message.content}"
        llm_result = await self._model_client.create(
            messages=[self._system_message, UserMessage(content=prompt, source=self.id.key)],
            cancellation_token=ctx.cancellation_token,
        )
        response = llm_result.content
        assert isinstance(response, str)
        print(f"{'-'*80}\n{self.id.type}:\n{response}")

        await self.publish_message(Message(response), topic_id=TopicId(writer_topic_type, source=self.id.key))


@type_subscription(topic_type=writer_topic_type)
class WriterAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__("A writer agent.")
        self._system_message = SystemMessage(
            content=(
                "You are a marketing copywriter. Given a block of text describing features, audience, and USPs, "
                "compose a compelling marketing copy (like a newsletter section) that highlights these points. "
                "Output should be short (around 150 words), output just the copy as a single text block."
            )
        )
        self._model_client = model_client

    @message_handler
    async def handle_intermediate_text(self, message: Message, ctx: MessageContext) -> None:
        prompt = f"Below is the info about the product:\n\n{message.content}"

        llm_result = await self._model_client.create(
            messages=[self._system_message, UserMessage(content=prompt, source=self.id.key)],
            cancellation_token=ctx.cancellation_token,
        )
        response = llm_result.content
        assert isinstance(response, str)
        print(f"{'-'*80}\n{self.id.type}:\n{response}")

        await self.publish_message(Message(response), topic_id=TopicId(format_proof_topic_type, source=self.id.key))

@type_subscription(topic_type=format_proof_topic_type)
class FormatProofAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__("A format & proof agent.")
        self._system_message = SystemMessage(
            content=(
                "You are an editor. Given the draft copy, correct grammar, improve clarity, ensure consistent tone, "
                "give format and make it polished. Output the final improved copy as a single text block."
            )
        )
        self._model_client = model_client

    @message_handler
    async def handle_intermediate_text(self, message: Message, ctx: MessageContext) -> None:
        prompt = f"Draft copy:\n{message.content}."
        llm_result = await self._model_client.create(
            messages=[self._system_message, UserMessage(content=prompt, source=self.id.key)],
            cancellation_token=ctx.cancellation_token,
        )
        response = llm_result.content
        assert isinstance(response, str)
        print(f"{'-'*80}\n{self.id.type}:\n{response}")

        await self.publish_message(Message(response), topic_id=TopicId(user_topic_type, source=self.id.key))

@type_subscription(topic_type=user_topic_type)
class UserAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("A user agent that outputs the final copy to the user.")

    @message_handler
    async def handle_final_copy(self, message: Message, ctx: MessageContext) -> None:
        print(f"\n{'-'*80}\n{self.id.type} received final copy:\n{message.content}")


def _configure_ssl_cert_chain() -> None:
    # 기본 CA: certifi
    certifi_path = certifi.where()
    extra_ca_path = os.getenv("EXTRA_CA_CERTS")  # 사내/프록시 CA PEM 경로

    if extra_ca_path and os.path.exists(extra_ca_path):
        with open(certifi_path, "rb") as f:
            base = f.read()
        with open(extra_ca_path, "rb") as f:
            extra = f.read()
        merged_fd, merged_path = tempfile.mkstemp(prefix="merged-ca-", suffix=".pem")
        try:
            with os.fdopen(merged_fd, "wb") as out:
                out.write(base)
                if not base.endswith(b"\n"):
                    out.write(b"\n")
                out.write(extra)
                out.write(b"\n")
        except Exception:
            # 병합 실패 시 certifi만 사용
            os.close(merged_fd)
            os.environ.setdefault("SSL_CERT_FILE", certifi_path)
            return
        os.environ["SSL_CERT_FILE"] = merged_path
    else:
        # 추가 CA가 없으면 certifi만 사용
        os.environ.setdefault("SSL_CERT_FILE", certifi_path)


async def main() -> None:
    # SSL 인증서 체인 구성 (사내 프록시/자체 CA 대응)
    _configure_ssl_cert_chain()

    model_client = AzureAIChatCompletionClient(
        endpoint=os.getenv("AZURE_AI_ENDPOINT", "https://models.github.ai/inference"),
        credential=AzureKeyCredential(os.getenv("GITHUB_TOKEN", "")),
        model=os.getenv("AZURE_AI_MODEL", "Phi-4"),
        model_info={
            "json_output": False,
            "function_calling": False,
            "vision": False,
            "family": "unknown",
            "structured_output": False,
        },
    )

    runtime = SingleThreadedAgentRuntime()

    await ConceptExtractorAgent.register(
        runtime, type=concept_extractor_topic_type, factory=lambda: ConceptExtractorAgent(model_client=model_client)
    )

    await WriterAgent.register(runtime, type=writer_topic_type, factory=lambda: WriterAgent(model_client=model_client))

    await FormatProofAgent.register(
        runtime, type=format_proof_topic_type, factory=lambda: FormatProofAgent(model_client=model_client)
    )

    await UserAgent.register(runtime, type=user_topic_type, factory=lambda: UserAgent())

    runtime.start()

    await runtime.publish_message(
        Message(content="An eco-friendly stainless steel water bottle that keeps drinks cold for 24 hours"),
        topic_id=TopicId(concept_extractor_topic_type, source="default"),
    )

    await runtime.stop_when_idle()
    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())

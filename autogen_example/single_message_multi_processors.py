from dataclasses import dataclass
from autogen_core import DefaultTopicId, MessageContext, RoutedAgent, default_subscription, message_handler
import asyncio
from autogen_core import SingleThreadedAgentRuntime


@dataclass
class Task:
    task_id: str


@default_subscription
class Processor(RoutedAgent):
    # def __init__(self, description: str) -> None:
    #     super().__init__(description)
    #     self._description = description

    @message_handler
    async def on_task(self, message: Task, ctx: MessageContext) -> None:
        print(f"{self._description} starting task {message.task_id}")
        await asyncio.sleep(2)
        print(f"{self._description} finished task {message.task_id}")


async def main() -> None:
    runtime = SingleThreadedAgentRuntime()

    await Processor.register(runtime, "agent_1", lambda: Processor("Agent 1"))
    await Processor.register(runtime, "agent_2", lambda: Processor("Agent 2"))

    runtime.start()

    await runtime.publish_message(Task(task_id="task-1"), topic_id=DefaultTopicId())
    await runtime.stop_when_idle()


"""
단일 메시지 및 다중 프로세서 
첫 번째 패턴은 단일 메시지가 여러 에이전트에 의해 동시에 처리되는 방식을 보여줍니다.
기본 주제에 메시지를 게시할 때 모든 등록된 에이전트는 독립적으로 메시지를 처리합니다.
"""
if __name__ == "__main__":
    asyncio.run(main())

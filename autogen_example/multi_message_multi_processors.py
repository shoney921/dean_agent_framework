from dataclasses import dataclass
import asyncio
from autogen_core import MessageContext, RoutedAgent, message_handler, type_subscription, TopicId, SingleThreadedAgentRuntime
from autogen_core import DefaultTopicId, MessageContext, RoutedAgent, default_subscription, message_handler, TopicId, type_subscription
import asyncio
from autogen_core import SingleThreadedAgentRuntime


TASK_RESULTS_TOPIC_TYPE = "task-results"
task_results_topic_id = TopicId(type=TASK_RESULTS_TOPIC_TYPE, source="default")


@dataclass
class Task:
    task_id: str


@dataclass
class TaskResponse:
    task_id: str
    result: str

@type_subscription(topic_type="urgent")
class UrgentProcessor(RoutedAgent):
    @message_handler
    async def on_task(self, message: Task, ctx: MessageContext) -> None:
        print(f"Urgent processor starting task {message.task_id}")
        await asyncio.sleep(1)  # Simulate work
        print(f"Urgent processor finished task {message.task_id}")

        task_response = TaskResponse(task_id=message.task_id, result="Results by Urgent Processor")
        await self.publish_message(task_response, topic_id=task_results_topic_id)

@type_subscription(topic_type="normal")
class NormalProcessor(RoutedAgent):
    @message_handler
    async def on_task(self, message: Task, ctx: MessageContext) -> None:
        print(f"Normal processor starting task {message.task_id}")
        await asyncio.sleep(3)  # Simulate work
        print(f"Normal processor finished task {message.task_id}")

        task_response = TaskResponse(task_id=message.task_id, result="Results by Normal Processor")
        await self.publish_message(task_response, topic_id=task_results_topic_id)

async def main() -> None:
    runtime = SingleThreadedAgentRuntime()

    await UrgentProcessor.register(runtime, "urgent_processor", lambda: UrgentProcessor("Urgent Processor"))
    await NormalProcessor.register(runtime, "normal_processor", lambda: NormalProcessor("Normal Processor"))

    runtime.start()

    await runtime.publish_message(Task(task_id="normal-1"), topic_id=TopicId(type="normal", source="default"))
    await runtime.publish_message(Task(task_id="urgent-1"), topic_id=TopicId(type="urgent", source="default"))

    await runtime.stop_when_idle()

if __name__ == "__main__":
    asyncio.run(main())
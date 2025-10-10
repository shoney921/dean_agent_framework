from dataclasses import dataclass
from typing import Callable

from autogen_core import DefaultTopicId, MessageContext, RoutedAgent, default_subscription, message_handler


@dataclass
class Message:
    content: int


@default_subscription
class Modifier(RoutedAgent):
    def __init__(self, modify_val: Callable[[int], int]) -> None:
        super().__init__("A modifier agent.")
        self._modify_val = modify_val

    @message_handler
    async def handle_message(self, message: Message, ctx: MessageContext) -> None:
        val = self._modify_val(message.content)
        print(f"{'-'*80}\nModifier:\nModified {message.content} to {val}")
        await self.publish_message(Message(content=val), DefaultTopicId())  # type: ignore


@default_subscription
class Checker(RoutedAgent):
    def __init__(self, run_until: Callable[[int], bool]) -> None:
        super().__init__("A checker agent.")
        self._run_until = run_until

    @message_handler
    async def handle_message(self, message: Message, ctx: MessageContext) -> None:
        if not self._run_until(message.content):
            print(f"{'-'*80}\nChecker:\n{message.content} passed the check, continue.")
            await self.publish_message(Message(content=message.content), DefaultTopicId())
        else:
            print(f"{'-'*80}\nChecker:\n{message.content} failed the check, stopping.")


@default_subscription
class Logger(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("A logger agent that tracks message flow.")
        self._message_count = 0

    @message_handler
    async def handle_message(self, message: Message, ctx: MessageContext) -> None:
        self._message_count += 1
        print(f"{'-'*80}\nLogger:\nMessage #{self._message_count}: Value = {message.content}")
        # 로거는 메시지를 다시 발행하지 않음 (무한 루프 방지)


class DirectMessenger(RoutedAgent):
    def __init__(self, target_agent_id: str) -> None:
        super().__init__("A direct messenger agent.")
        self._target_agent_id = target_agent_id
        self._message_count = 0

    @message_handler
    async def handle_message(self, message: Message, ctx: MessageContext) -> None:
        self._message_count += 1
        print(f"{'-'*80}\nDirectMessenger:\nReceived message #{self._message_count}: {message.content}")
        
        # 특정 에이전트에게 직접 메시지 전달
        if message.content > 1:
            # 메시지를 1 감소시켜서 타겟 에이전트에게 직접 전달
            new_message = Message(content=message.content - 1)
            print(f"DirectMessenger: Sending {new_message.content} directly to {self._target_agent_id}")
            await self.send_message(new_message, AgentId(self._target_agent_id, "default"))
        else:
            print(f"DirectMessenger: Value {message.content} is <= 1, stopping direct messaging.")


import asyncio
from autogen_core import AgentId, SingleThreadedAgentRuntime

async def main():
    # Create a local embedded runtime.
    runtime = SingleThreadedAgentRuntime()

    # Register the modifier and checker agents by providing
    # their agent types, the factory functions for creating instance and subscriptions.
    await Modifier.register(
        runtime,
        "modifier",
        # Modify the value by subtracting 1
        lambda: Modifier(modify_val=lambda x: x - 1),
    )

    await Checker.register(
        runtime,
        "checker",
        # Run until the value is less than or equal to 1
        lambda: Checker(run_until=lambda x: x <= 1),
    )

    await Logger.register(
        runtime,
        "logger",
        # Logger agent for tracking message flow
        lambda: Logger(),
    )

    await DirectMessenger.register(
        runtime,
        "direct_messenger",
        # DirectMessenger that sends messages directly to checker
        lambda: DirectMessenger(target_agent_id="checker"),
    )

    # Start the runtime and send a direct message to test direct messaging.
    runtime.start()
    print("=== Testing Direct Messaging ===")
    await runtime.send_message(Message(5), AgentId("direct_messenger", "default"))
    await runtime.stop_when_idle()

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from autogen_core import AgentId, SingleThreadedAgentRuntime
from autogen_example import Modifier, Checker, Message

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

    # Start the runtime and send a direct message to the checker.
    runtime.start()
    await runtime.send_message(Message(10), AgentId("checker", "default"))
    await runtime.stop_when_idle()

if __name__ == "__main__":
    asyncio.run(main())
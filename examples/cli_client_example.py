import asyncio
import json
from typing import Any

import aioconsole
from websockets import WebSocketClientProtocol

from datadivr.client import WebSocketClient
from datadivr.utils.messages import Message

EXAMPLE_JSON = """{"event_name": "sum_event", "payload": {"numbers": [5, 7]}}"""


async def handle_sum_result(message: Message, websocket: WebSocketClientProtocol) -> None:
    print(f"*** handle_sum_result(): Received response: '{message.message}'")


async def get_user_input() -> Any:
    while True:
        try:
            user_input = await aioconsole.ainput()
            if user_input.lower() == "quit":
                return None
            data = json.loads(user_input)
        except json.JSONDecodeError:
            print("X Invalid JSON. Please try again.")
        else:
            return data


async def input_loop(client: WebSocketClient) -> None:
    while True:
        try:
            data = await get_user_input()
            if data is None:
                break
            event_name = data.get("event_name") or "message"
            to_value = data.get("to") or "others"
            await client.send_message(payload=data.get("payload"), event_name=event_name, to=to_value)
        except Exception as e:
            print(f"X Error sending message: {e}")


async def main() -> None:
    client = WebSocketClient("ws://localhost:8000/ws")
    client.register_handler("sum_handler_result", handle_sum_result)

    print("- Connecting to websocket...")
    await client.connect()
    print("- Connected!")
    print(f"* Example JSON format: {EXAMPLE_JSON}")
    print("* Enter JSON message (or 'quit' to exit):")

    # Create tasks for both receiving messages and handling user input
    receive_task = asyncio.create_task(client.receive_messages())
    input_task = asyncio.create_task(input_loop(client))

    try:
        # Wait for either task to complete
        await asyncio.gather(receive_task, input_task)
    except KeyboardInterrupt:
        print("\n- Disconnecting...")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

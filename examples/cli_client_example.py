import asyncio
import json
from typing import Any, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from rich.console import Console

# from websockets import WebSocketClientProtocol
from datadivr.client import WebSocketClient
from datadivr.handlers.sum_handler import sum_handler
from datadivr.utils.messages import Message

EXAMPLE_JSON = """EXAMPLES:
{"event_name": "sum_event", "payload": {"numbers": [5, 7]}}
{"event_name": "msg", "to": "all", "message": "hello"}
"""

console = Console()


# some custom handlers
async def handle_sum_result(message: Message) -> Optional[Message]:
    print(f"*** handle_sum_result(): {message.from_id}: '{message.payload}'")
    return None


async def msg_handler(message: Message) -> Optional[Message]:
    print(f">> {message.from_id}({message.event_name}): '{message.message}'")
    return None


async def get_user_input(session: PromptSession) -> Any:
    while True:
        try:
            with patch_stdout():
                user_input = await session.prompt_async("Enter JSON > ")
            if user_input.lower() == "quit":
                return None
            data = json.loads(user_input)
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON. Please try again.[/red]")
            continue
        except EOFError:
            return None
        else:
            return data


async def input_loop(client: WebSocketClient) -> None:
    session: PromptSession = PromptSession()
    while True:
        try:
            data = await get_user_input(session)
            if data is None:
                return
            event_name = data.get("event_name", "msg") # if unset use msg by default
            to_value = data.get("to", "others") # d
            message_value = data.get("message", None)
            await client.send_message(payload=data.get("payload"), event_name=event_name, to=to_value, message=message_value)
        except Exception as e:
            console.print(f"[red]Error sending message: {e}[/red]")


async def main() -> None:
    client = WebSocketClient("ws://localhost:8000/ws")
    client.register_handler("sum_handler_result", handle_sum_result)
    client.register_handler("client_sum", sum_handler)
    client.register_handler("msg", msg_handler)

    console.print("[blue]Connecting to websocket...[/blue]")
    await client.connect()

    console.print(f"Example JSON format: {EXAMPLE_JSON}")

    # Create tasks for both receiving messages and handling user input
    tasks = [asyncio.create_task(client.receive_messages()), asyncio.create_task(input_loop(client))]

    try:
        await asyncio.gather(*tasks)
    except (asyncio.CancelledError, EOFError):
        console.print("\n[yellow]Disconnecting...[/yellow]")
    finally:
        for task in tasks:
            task.cancel()
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

"""Client-side CLI functionality."""

import asyncio
import json
from typing import Any

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from rich.console import Console

from datadivr.exceptions import InputLoopInterrupted
from datadivr.handlers import client_handlers  # noqa: F401
from datadivr.transport.client import WebSocketClient
from datadivr.utils.logging import get_logger, setup_logging

console = Console()
logger = get_logger(__name__)

EXAMPLE_JSON = """EXAMPLES:
{"event_name": "sum_event", "payload": {"numbers": [391, 29]}}
{"event_name": "msg", "to": "all", "message": "hello"}
{"event_name": "msg", "to": "others", "message": "hello"}
"""


async def get_user_input(session: PromptSession[Any]) -> Any:
    """Get JSON input from the user."""
    while True:
        try:
            with patch_stdout():
                user_input = await session.prompt_async("Enter JSON > ")
            if user_input.lower() == "quit":
                return None
            return json.loads(user_input)
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON. Please try again.[/red]")
        except EOFError:
            return None


async def input_loop(client: WebSocketClient) -> None:
    """Run the main input loop for the WebSocket client."""
    session: PromptSession[Any] = PromptSession()
    while True:
        try:
            data = await get_user_input(session)
            if data is None:
                return
            await client.send_message(
                payload=data.get("payload"),
                event_name=data.get("event_name", "msg"),
                to=data.get("to", "others"),
                msg=data.get("message"),
            )
        except KeyboardInterrupt as err:
            raise InputLoopInterrupted() from err
        except Exception as e:
            console.print(f"[red]Error sending message: {e}[/red]")


async def run_client(host: str, port: int) -> None:
    """Run the WebSocket client."""
    client = WebSocketClient(f"ws://{host}:{port}/ws")
    try:
        await client.connect()
        console.print(f"Example JSON format: {EXAMPLE_JSON}")
        await asyncio.gather(client.receive_messages(), input_loop(client))
    except OSError as e:
        logger.error("websocket_connection_failed", error=str(e))  # noqa: TRY400
    except InputLoopInterrupted:
        logger.info("input loop interrupted, exiting ...")
    except Exception as e:
        logger.error("client_error", error=str(e))  # noqa: TRY400
    finally:
        await client.disconnect()


def start_client_app(host: str, port: int, log_level: str = "INFO") -> None:
    """Start the WebSocket client application."""
    setup_logging()

    logger.info("client_starting", host=host, port=port)
    asyncio.run(run_client(host, port))

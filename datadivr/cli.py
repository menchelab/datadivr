import asyncio
import json
from typing import Any

import typer
import uvicorn
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from rich.console import Console

from datadivr.handlers.builtin import sum_handler  # noqa: F401
from datadivr.transport.client import WebSocketClient
from datadivr.transport.server import app

app_cli = typer.Typer()
console = Console()

EXAMPLE_JSON = """EXAMPLES:
{"event_name": "sum_event", "payload": {"numbers": [391, 29]}}
{"event_name": "msg", "to": "all", "message": "hello"}
{"event_name": "msg", "to": "others", "message": "hello"}
{"event_name": "sum_event_client", "payload": {"numbers": [57, 12]}}
"""


# Custom exception for input loop interruption
class InputLoopInterrupted(Exception):
    pass


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
            event_name = data.get("event_name", "msg")  # if unset use msg by default
            to_value = data.get("to", "others")  # default to "others"
            message_value = data.get("message", None)
            await client.send_message(
                payload=data.get("payload"), event_name=event_name, to=to_value, msg=message_value
            )
        except KeyboardInterrupt:  # Handle Ctrl+C gracefully
            raise InputLoopInterrupted() from None  # Raise custom exception with context
        except Exception as e:
            console.print(f"[red]Error sending message: {e}[/red]")


# Define global options
@app_cli.callback()
def common_options(
    port: int = typer.Option(8765, help="Port to run the WebSocket server or connect the client to."),
    host: str = typer.Option("127.0.0.1", help="Host address for the WebSocket server or client."),
) -> None:
    """Common options for all commands."""
    pass


@app_cli.command()
def start_server(port: int = 8765, host: str = "127.0.0.1") -> None:
    """Start the WebSocket server."""

    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server_instance = uvicorn.Server(config)
    asyncio.run(server_instance.serve())


@app_cli.command()
def start_client(port: int = 8765, host: str = "127.0.0.1") -> None:
    """Start the WebSocket client."""
    console.print("[blue]starting client...[/blue]")

    async def run_client() -> None:
        client = WebSocketClient(f"ws://{host}:{port}/ws")

        console.print("[blue]Connecting to websocket...[/blue]")
        try:
            await client.connect()
        except OSError as e:
            console.print(f"[red]Failed to connect to websocket: {e}[/red]")
            return

        console.print(f"Example JSON format: {EXAMPLE_JSON}")

        tasks = [
            asyncio.create_task(client.receive_messages()),
            asyncio.create_task(input_loop(client)),
        ]

        try:
            await asyncio.gather(*tasks)
        except InputLoopInterrupted:
            console.print("\n[yellow]Input loop interrupted. Exiting...[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        finally:
            for task in tasks:
                task.cancel()
            await client.disconnect()

    asyncio.run(run_client())


if __name__ == "__main__":
    app_cli()

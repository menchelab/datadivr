import asyncio
import json
from typing import Any

import typer
import uvicorn
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from rich.console import Console

from datadivr.exceptions import InputLoopInterrupted
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


async def get_user_input(session: PromptSession) -> Any:
    """Get JSON input from the user.

    Args:
        session: The prompt session to use for input

    Returns:
        The parsed JSON data or None if the user wants to quit

    Raises:
        json.JSONDecodeError: If the input is not valid JSON
    """
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
    """Run the main input loop for the WebSocket client.

    Args:
        client: The WebSocket client to use for sending messages
    """
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
            raise InputLoopInterrupted() from None
        except Exception as e:
            console.print(f"[red]Error sending message: {e}[/red]")


@app_cli.callback()
def common_options(
    port: int = typer.Option(8765, help="Port to run the WebSocket server or connect the client to."),
    host: str = typer.Option("127.0.0.1", help="Host address for the WebSocket server or client."),
) -> None:
    """Common options for all CLI commands."""
    pass


@app_cli.command()
def start_server(port: int = 8765, host: str = "127.0.0.1") -> None:
    """Start the WebSocket server.

    Args:
        port: The port to listen on
        host: The host address to bind to
    """
    print("run server")
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server_instance = uvicorn.Server(config)
    asyncio.run(server_instance.serve())


async def run_client(host: str, port: int) -> None:
    """Run the WebSocket client.

    Args:
        host: The host to connect to
        port: The port to connect to
    """
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


@app_cli.command()
def start_client(port: int = 8765, host: str = "127.0.0.1") -> None:
    """Start an interactive WebSocket client.

    Args:
        port: The port to connect to
        host: The host address to connect to
    """
    console.print("[blue]starting client...[/blue]")
    asyncio.run(run_client(host, port))


if __name__ == "__main__":
    app_cli()  # This will show the help message by default

"""Command-line interface for DataDivr."""

from typing import Optional

import typer

from datadivr.commandlineinterface.client import start_client_app
from datadivr.commandlineinterface.server import start_server_app

app_cli = typer.Typer()


@app_cli.command()
def start_server(
    port: int = 8765,
    host: str = "127.0.0.1",
    static_dir: Optional[str] = "./static",
    log_level: str = "INFO",
    pretty: bool = True,
) -> None:
    """Start the WebSocket and static file server."""
    start_server_app(host, port, static_dir, log_level, pretty)


@app_cli.command()
def start_client(port: int = 8765, host: str = "127.0.0.1", log_level: str = "INFO") -> None:
    """Start an interactive WebSocket client."""
    start_client_app(host, port, log_level)


if __name__ == "__main__":
    app_cli()

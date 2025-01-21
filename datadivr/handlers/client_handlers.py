"""Client-side WebSocket event handlers."""

from typing import Optional

from rich.console import Console

from datadivr.handlers.registry import HandlerType, websocket_handler
from datadivr.transport.models import WebSocketMessage

console = Console()


@websocket_handler("INFO_UPDATE", HandlerType.CLIENT)
async def handle_info_update(message: WebSocketMessage) -> Optional[WebSocketMessage]:
    """Handle updates about client information.

    Args:
        message: WebSocket message containing client information
    """
    payload = message.payload

    # Print information about the update
    console.print(
        f"\n[bold blue]Client Update:[/bold blue] "
        f"({payload['latitude']:.4f}, {payload['longitude']:.4f}) "
        f"Alt: {payload['altitude']}m Dir: {payload['direction']}°"
    )

    return None

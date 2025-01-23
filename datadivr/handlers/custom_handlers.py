import numpy as np

from datadivr.handlers.registry import HandlerType, websocket_handler
from datadivr.project.project_manager import ProjectManager
from datadivr.transport.models import WebSocketMessage
from datadivr.utils.logging import get_logger

logger = get_logger(__name__)


@websocket_handler("client_overview", HandlerType.CLIENT)
async def handle_client_overview(message: WebSocketMessage) -> None:
    """Handle client overview messages."""
    if not message.payload:
        return

    overview = message.payload
    logger.info(
        "Client Overview Update: ",
        clients=len(overview["client_ids"]),
        ids=overview["client_ids"],
        time=overview["timestamp"],
    )


@websocket_handler("get_node_info", HandlerType.SERVER)
async def get_node_info_handler(message: WebSocketMessage) -> WebSocketMessage:
    """Handle requests to get information about a specific node."""
    node_index = message.payload.get("index") if message.payload else None
    current_project = ProjectManager.get_current_project()

    if current_project is None:
        return WebSocketMessage(
            event_name="get_node_info_result", payload={"error": "No project is currently open"}, to=message.from_id
        )

    if node_index is None:
        return WebSocketMessage(
            event_name="get_node_info_result", payload={"error": "Node index not provided"}, to=message.from_id
        )

    try:
        node_data = (
            current_project.nodes_data.get_attributes_by_index(node_index) if current_project.nodes_data else None
        )

        if node_data is None:
            return WebSocketMessage(
                event_name="get_node_info_result", payload={"error": "Node data not found"}, to=message.from_id
            )

        # Convert all float32 values to float
        node_data = {k: float(v) if isinstance(v, np.float32) else v for k, v in node_data.items()}

        return WebSocketMessage(event_name="get_node_info_result", payload=node_data, to=message.from_id)
    except IndexError as e:
        return WebSocketMessage(event_name="get_node_info_result", payload={"error": str(e)}, to=message.from_id)
    except Exception as e:
        return WebSocketMessage(event_name="get_node_info_result", payload={"error": str(e)}, to=message.from_id)

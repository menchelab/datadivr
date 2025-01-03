import asyncio
import math

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.concurrency import asynccontextmanager

from datadivr.handlers.registry import HandlerType, websocket_handler
from datadivr.transport.models import WebSocketMessage
from datadivr.transport.web_server import add_static_routes
from datadivr.utils.logging import get_logger

logger = get_logger(__name__)

# Store client data
clients: dict[WebSocket, tuple[str, float, float, float, float]] = {}  # (name, lat, lon, alt, direction)


@websocket_handler("INFO_UPDATE", HandlerType.SERVER)
async def info_update_handler(message: WebSocketMessage, websocket: WebSocket) -> None:
    """Handle INFO_UPDATE events from clients."""
    try:
        data = message.payload
        if not isinstance(data, dict):
            logger.error("Invalid payload format")
            return

        lat = data.get("latitude")
        lon = data.get("longitude")
        alt = data.get("altitude")
        direction = data.get("direction")

        if not all(isinstance(x, (int, float)) for x in [lat, lon, alt, direction]):
            logger.error("Invalid data types in payload")
            return

        # Preserve the existing name when updating position
        current_name = clients[websocket][0] if websocket in clients else str(websocket)
        clients[websocket] = (current_name, lat, lon, alt, direction)
        logger.debug("Updated client info", client_id=message.from_id, data=data)
    except Exception as e:
        logger.exception("Error handling INFO_UPDATE", error=str(e))


async def broadcast_updates() -> None:
    """Broadcast updates to clients within 100km range."""
    while True:
        logger.debug("Starting broadcast cycle")

        # Get current state of clients to avoid modification during iteration
        current_clients = {ws: data for ws, data in clients.items() if not isinstance(ws, str)}

        for websocket, (name1, lat1, lon1, _alt1, _direction1) in current_clients.items():
            # Skip clients that haven't sent their position yet
            if lat1 == 0 and lon1 == 0:
                continue

            nearby_clients = []
            for other_socket, (name2, lat2, lon2, alt2, direction2) in current_clients.items():
                # Skip other clients that haven't sent their position yet
                if lat2 == 0 and lon2 == 0 or websocket == other_socket:
                    continue

                if is_within_range(lat1, lon1, lat2, lon2):
                    nearby_clients.append({
                        "name": name2,
                        "latitude": lat2,
                        "longitude": lon2,
                        "altitude": alt2,
                        "direction": direction2,
                    })

            # Only send update if there are nearby clients
            if nearby_clients:
                try:
                    await websocket.send_json({
                        "event_name": "NEARBY_UPDATE",
                        "payload": {"nearby_clients": nearby_clients},
                    })
                    logger.debug("Sent nearby update", client_id=name1, nearby_count=len(nearby_clients))
                except Exception as e:
                    logger.exception("Error sending update to client", error=str(e))

        await asyncio.sleep(10)


def is_within_range(lat1: float, lon1: float, lat2: float, lon2: float, range_km: float = 10) -> bool:
    """Check if two points are within a specified range in kilometers."""
    # Haversine formula to calculate the distance between two points on the Earth
    R = 6371  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance <= range_km


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    try:
        broadcast_task = asyncio.create_task(broadcast_updates())
        logger.info("Broadcast updates task started")
        yield
    finally:
        broadcast_task.cancel()
        try:
            await broadcast_task
        except asyncio.CancelledError:
            logger.info("Broadcast updates task cancelled")


app = FastAPI(lifespan=lifespan)

# Add static file serving
static_dir_path = "./static"
add_static_routes(app, static_dir=static_dir_path)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Handle incoming WebSocket connections."""
    await websocket.accept()
    default_name = str(websocket)
    clients[websocket] = (default_name, 0, 0, 0, 0)  # Initialize with default name and values
    logger.info("Client connected", client_id=default_name)

    try:
        while True:
            data = await websocket.receive_json()
            message = WebSocketMessage.model_validate(data)
            message.from_id = str(websocket)  # Just for logging/identification

            # Route messages to appropriate handlers based on event_name
            if message.event_name == "INFO_UPDATE":
                await info_update_handler(message, websocket)
            elif message.event_name == "SET_NAME":
                await set_name_handler(message, websocket)
            else:
                logger.warning("Unknown event type", event=message.event_name)

    except WebSocketDisconnect:
        del clients[websocket]
        logger.info("Client disconnected", client_id=str(websocket))
    except Exception as e:
        logger.exception("WebSocket error", error=str(e), client_id=str(websocket))


@websocket_handler("SET_NAME", HandlerType.SERVER)
async def set_name_handler(message: WebSocketMessage, websocket: WebSocket) -> None:
    """Handle SET_NAME events from clients."""
    try:
        name = message.payload.get("name", "")
        if not isinstance(name, str) or not name.strip():
            logger.error("Invalid name format")
            return

        # Just update the name component of the tuple
        if websocket in clients:
            clients[websocket] = (name.strip(), *clients[websocket][1:])
            logger.debug("Updated client name", client_id=str(websocket), name=name)
    except Exception as e:
        logger.exception("Error handling SET_NAME", error=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8765)

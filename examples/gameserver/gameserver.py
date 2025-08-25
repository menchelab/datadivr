from math import asin, cos, radians, sin, sqrt

from datadivr import BackgroundTasks, app
from datadivr.handlers.registry import HandlerType, websocket_handler
from datadivr.transport.messages import create_message, send_message
from datadivr.transport.models import WebSocketMessage
from datadivr.transport.server import clients, get_client_state, update_client_state
from datadivr.utils.logging import get_logger, setup_logging

# Initialize logging first, before getting the logger
setup_logging()
logger = get_logger(__name__)


# example messages
# {"event_name": "GAMESERVER_SET_NAME", "to": "others", "payload": {"name": "CLI" } }
# {"event_name": "GAMESERVER_INFO_UPDATE", "to": "others", "payload": {"latitude": 48.23747967660676, "longitude": 16.416320800781254, "altitude": 500, "direction": 90}}


def is_within_range(lat1: float, lon1: float, lat2: float, lon2: float, max_range_km: float = 100.0) -> bool:
    """
    Determine if two geographical points are within a specified range.

    This function calculates the great-circle distance between two points
    on the Earth's surface given their latitude and longitude in degrees.
    It returns True if the distance is less than or equal to the specified
    maximum range in kilometers.

    Parameters:
    - lat1 (float): Latitude of the first point in degrees.
    - lon1 (float): Longitude of the first point in degrees.
    - lat2 (float): Latitude of the second point in degrees.
    - lon2 (float): Longitude of the second point in degrees.
    - max_range_km (float): Maximum range in kilometers. Default is 10.0 km.

    Returns:
    - bool: True if the distance between the two points is within the specified range, False otherwise.
    """
    lat1, lon1 = radians(lat1), radians(lon1)
    lat2, lon2 = radians(lat2), radians(lon2)
    R = 6371.0
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    distance = R * c
    return distance <= max_range_km


@websocket_handler("GAMESERVER_CLIENT_UPDATE_STATE", HandlerType.SERVER)
async def info_update_handler(message: WebSocketMessage) -> None:
    """
    Handle position updates from clients.

    This handler processes incoming WebSocket messages containing
    geographical data from clients. It updates the client's position
    information in the server's client registry.

    Example message format:
    {
        "event_name": "GAMESERVER_CLIENT_UPDATE",
        "to": "others",
        "payload": {
            "lat: 48.210033,
            "long": 16.363449,
            "alt": 2345,
            "rot_x": 0.3,
            "rot_y": 0.4,
            "rot_z": 0.5,
            "type": 1,
            "anim": 2
        }
    }

    Parameters:
    - message (WebSocketMessage): The incoming WebSocket message containing
      the client's position data.
    """
    try:
        data = message.payload
        print("info_update_handler payload:", message.payload)
        latitude = data.get("lat")
        longitude = data.get("long")
        altitude = data.get("alt")
        rotation_x = data.get("rot_x")
        rotation_y = data.get("rot_y")
        rotation_z = data.get("rot_z")
        aircraft_type = data.get("type")
        animation_state = data.get("anim")

        if not all(
            isinstance(x, int | float)
            for x in [latitude, longitude, altitude, rotation_x, rotation_y, rotation_z, aircraft_type, animation_state]
        ):
            for x in [
                latitude,
                longitude,
                altitude,
                rotation_x,
                rotation_y,
                rotation_z,
                aircraft_type,
                animation_state,
            ]:
                print(x, type(x))

            logger.error("Invalid data types in payload")
            return

        # Retrieve the current name or use a default if not set
        state = get_client_state(message.from_id)
        current_name = state.get("name", "Unknown") if state else "Unknown"

        # Update client state
        update_client_state(
            message.from_id,
            name=current_name,
            lat=latitude,
            long=longitude,
            alt=altitude,
            rot_x=rotation_x,
            rot_y=rotation_y,
            rot_z=rotation_z,
            type=aircraft_type,
            anim=animation_state,
        )
        logger.debug("Updated client info", client_id=message.from_id, data=data)
    except Exception as e:
        logger.exception("Error handling GAMESERVER_CLIENT_UPDATE", error=str(e))


@BackgroundTasks.periodic(interval=1, name="GAMESERVER_broadcast_nearby_clients")
async def broadcast_updates() -> None:
    """
    Periodically broadcast updates about nearby clients to each connected client.

    This function runs every second and performs the following steps for each client:
    1. Gets the client's current position
    2. Finds all other clients within the specified range
    3. Sends a GAMESERVER_NEARBY_UPDATE message containing information about nearby clients

    The message format sent to each client is:
    {
        "event_name": "GAMESERVER_NEARBY_UPDATE",
        "payload": {
            "nearby_clients": [
                {
                    "client_id": "uuid",
                    "name": "Client Name",
                    "lat": float,
                    "long": float,
                    "alt": float,
                    "rot_x": float,
                    "rot_y": float,
                    "rot_z": float,
                    "type": int,
                    "anim": int
                },
                ...
            ]
        }
    }
    """
    logger.debug("Starting broadcast cycle")

    # Iterate through all connected clients
    for client_id, client_data in clients.items():
        state = client_data["state"]

        # Get current client's position
        lat1, lon1 = state.get("lat", 0), state.get("long", 0)

        # Skip clients without valid position data
        if lat1 == 0 and lon1 == 0:
            continue

        nearby_clients = []

        # Check distance to all other clients
        for other_id, other_data in clients.items():
            # Skip self
            if client_id == other_id:
                continue

            other_state = other_data["state"]
            lat2, lon2 = other_state.get("lat", 0), other_state.get("long", 0)
            # Skip clients without valid position data
            if lat2 == 0 and lon2 == 0:
                continue

            # If client is within range, add their info to the nearby list
            if is_within_range(lat1, lon1, lat2, lon2):
                nearby_clients.append({
                    "client_id": other_id,
                    "name": other_state.get("name"),
                    "lat": lat2,
                    "long": lon2,
                    "alt": other_state.get("alt"),
                    "rot_x": other_state.get("rot_x"),
                    "rot_y": other_state.get("rot_y"),
                    "rot_z": other_state.get("rot_z"),
                    "type": other_state.get("type"),
                    "anim": other_state.get("anim"),
                })

        # also send if no nearby clients, to potentially clean old clients, could be improved:
        # TODO: check if last update was already empty for this client, if so, skip

        # if nearby_clients: # only send if there are nearby clients

        message = create_message(
            event_name="GAMESERVER_NEARBY_UPDATE", payload={"nearby_clients": nearby_clients}, to=client_id
        )
        await send_message(client_data["websocket"], message)


@websocket_handler("GAMESERVER_CLIENT_SETNAME", HandlerType.SERVER)
async def set_name_handler(message: WebSocketMessage) -> None:
    """
    Handle the GAMESERVER_CLIENT_SETNAME event from clients.

    This handler allows clients to update their display name on the server.
    It processes incoming WebSocket messages containing the new name and
    updates the client's information in the server's client registry.

    Example message format:
    {
        "event_name": "GAMESERVER_CLIENT_SETNAME",
        "to": "others",
        "payload": {
            "name": "Timmey"
        }
    }

    Parameters:
    - message (WebSocketMessage): The incoming WebSocket message containing
      the client's new name.
    """
    try:
        name = message.payload.get("name", "")
        if not isinstance(name, str) or not name.strip():
            logger.error("Invalid name format")
            return

        # Get existing state to preserve other fields
        existing_state = get_client_state(message.from_id) or {}

        # Create new state dict with updated name
        new_state = existing_state.copy()
        new_state["name"] = name.strip()

        # Update state with all fields
        update_client_state(message.from_id, **new_state)
        logger.debug("Updated client name", client_id=message.from_id, name=name)



    except Exception as e:
        logger.exception("Error handling GAMESERVER_CLIENT_SETNAME", error=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8765)

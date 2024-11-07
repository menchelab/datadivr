import json
import uuid
from typing import Callable

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


class WebSocketServer:
    def __init__(self) -> None:
        self.connected_clients: set[WebSocket] = set()
        self.client_ids: dict[WebSocket, str] = {}
        self.handlers: dict[str, Callable] = {}

    async def handle_connection(self, websocket: WebSocket) -> None:
        await websocket.accept()
        client_id = str(uuid.uuid4())
        self.client_ids[websocket] = client_id
        print(f"New client connected with ID {client_id}")

        self.connected_clients.add(websocket)

        try:
            while True:
                message = await websocket.receive_text()
                event_data = json.loads(message)
                event_data["from"] = client_id
                await self.handle_msg(event_data, websocket)
        except WebSocketDisconnect:
            pass
        finally:
            self.connected_clients.remove(websocket)
            del self.client_ids[websocket]
            print(f"* Client with ID {client_id} disconnected.")

    async def handle_msg(self, event_data: dict, websocket: WebSocket) -> None:
        event_name = event_data["event_name"]
        print(f"< received message: {event_data}")

        if event_name in self.handlers:
            print(f"* Found handler for event: {event_name}")
            handler = self.handlers[event_name]
            await handler(event_data, websocket)
        else:
            # By default just do message routing if no event handler fits
            print(f"* no handler for event: {event_name}, forwarding message ...")
            await self.forward_message(event_data, websocket)

    def register_handler(self, event_name: str, handler: Callable) -> None:
        self.handlers[event_name] = handler

    async def forward_message(self, event_data: dict, sender_websocket: WebSocket) -> None:
        to = event_data.get("to")
        from_ = event_data.get("from")

        # Create the message payload once
        message_data = {
            "event_name": event_data["event_name"],
            "message": event_data.get("message"),
            "from": from_,
            "to": to,
            "payload": event_data.get("payload"),
        }

        # Determine recipients based on 'to' field
        recipients = []
        if to == "all":
            recipients = list(self.connected_clients)
        elif to == "others":
            recipients = [client for client in self.connected_clients if client != sender_websocket]
        elif to:  # specific client ID
            recipient = self.get_client_by_id(to)
            if recipient:
                recipients = [recipient]
            else:
                print(f"W Warning: Recipient {to} not found")
                return

        # Send to all determined recipients
        message_str = json.dumps(message_data)
        for recipient in recipients:
            print(f"< sending message (to={to}) to {recipient}")
            await recipient.send_text(message_str)

    def get_client_by_id(self, client_id: str) -> WebSocket | None:
        # Find client by its ID
        for client, client_id_ in self.client_ids.items():
            if client_id_ == client_id:
                return client
        return None


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    server = WebSocketServer()
    await server.handle_connection(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

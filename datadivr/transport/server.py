"""WebSocket server implementation for datadivr.

This module provides a FastAPI-based WebSocket server that handles client
connections, message routing, and event handling.

Example:
    ```python
    import uvicorn
    from datadivr import app

    uvicorn.run(app, host="127.0.0.1", port=8765)
    ```
"""

import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import File, Form, UploadFile, Request, FastAPI, HTTPException
from os import listdir

from fastapi.responses import HTMLResponse
from datadivr.core.tasks import BackgroundTasks
from datadivr.exceptions import InvalidMessageFormat
from datadivr.handlers.registry import HandlerType, get_handlers
from datadivr.transport.models import WebSocketMessage
from datadivr.utils.logging import get_logger
import json
import string
import random



logger = get_logger(__name__)

# Module-level state
clients: dict[str, dict[str, Any]] = {}  # Use client_id as the key
global userdb
userdb = {}

taskdata = {}
with open('bischlingPinzgau.json', 'r', encoding='utf-8') as f:
    taskdata = json.load(f)

import os

static_dir = os.path.join(os.path.dirname(__file__),  'tasks')
taskfiles = {"tasks": os.listdir(static_dir)}

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def searchUser (name,pw):
    for user in userdb["users"]:
        if user["name"] == name:
            if user["pw"] == pw:
                return user
    return None 

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Handle startup and shutdown events."""
    logger.debug("startup_initiated")
    with open('users.json', 'r', encoding='utf-8') as f:
        global userdb 
        userdb = json.load(f)
    f.close()
    print(userdb)
    server_handlers = get_handlers(HandlerType.SERVER)
    logger.info("registered_server_handlers", handlers=list(server_handlers.keys()))

    await BackgroundTasks.start_all()
    try:
        yield
    finally:
        logger.debug("shutdown_initiated", num_clients=len(clients))
        with open('users.json', 'w') as f:
            json.dump(userdb, f)
        f.close()
        for client_id in list(clients.keys()):
            try:
                await close_client_connection(client_id)
                logger.debug("closed_client_connection", client_id=client_id)
            except Exception as e:
                logger.exception("client_close_error", error=str(e), client_id=client_id)

        await BackgroundTasks.stop_all()
        clients.clear()
        logger.debug("shutdown_completed")



app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


    # Perform any startup tasks here
#upload user textures
@app.post("/pw")
async def check_pw(request: Request, response: Response):
    thisuser = await request.json()
    name = thisuser["name"]
    pw = thisuser["pw"]
    print("json:", thisuser)
    found = False
    
    for user in userdb["users"]:
        print("user:", user)
        if user["name"] == name:
            found = True
            print("found user:", user)
    
            if user["pw"] == pw:
                print("correct pw")
                return {"message": f"CORRECT","data":thisuser}
            else:
                return {"message": f"WRONG PW"}
    if not found:
        return {"message": f"NO USER Called {name}"}
   
      

@app.post("/upload")
async def upload( response: Response, file: UploadFile = File(...), myjson: str = Form(...)):

    thisuser = json.loads(myjson)
    print(thisuser["name"])
    found = False
    for user in userdb["users"]:
        if user["name"] == thisuser["name"]:
            found = True
    
    if found:
        return {"message": f"user exists"}
    else:
                #raise HTTPException(status_code=400, detail='User already exists')
        # In a real application, you would hash the password before storing it
        thisuser["pw"] = id_generator()
        thisuser["tex"] = file.filename
        userdb["users"].append(thisuser)
        name = thisuser["name"]
        pw = thisuser["pw"]
        try:
            contents = file.file.read()
            #print(file.name)
            with open("static/userskins/" + file.filename, "wb") as f:
                f.write(contents)

        except Exception:
            raise HTTPException(status_code=500, detail='Something went wrong')
        finally:
            file.file.close()
        return {"message": f"Welcome {name} ! your Password is {pw}"}
# HTML ROUTE
@app.get("/createAccount")
async def newaccount(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.get("/clients")
async def showclients():
    print("clients:", clients)
    #return json.dumps(clients)

@app.get("/cloudbase1337/{name}/{pw}", response_class=HTMLResponse)
async def multiplayermap(request: Request, name: str, pw: str):
    thisuser = searchUser(name,pw)  
    if thisuser is None:
        return templates.TemplateResponse("login.html", {"request": request})
    else:
        return templates.TemplateResponse(request=request, name="client.html", context={"name": name, "tex": thisuser["tex"]})


# WEBSOCKET ROUTES
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Handle incoming WebSocket connections."""
    await BackgroundTasks.task(name=f"ws_connection_{id(websocket)}")(handle_connection)(websocket)


#print(taskfiles)

@BackgroundTasks.task()

# NEW CONNECTION
async def handle_connection(websocket: WebSocket) -> None:
    """Handle a WebSocket connection lifecycle."""
    await websocket.accept()
    
    client_id = add_client(websocket)


    await websocket.send_json({"event_name": "TASK", "payload": taskdata})
    await websocket.send_json({"event_name": "TASKLIST", "payload": taskfiles})

    logger.info("client_connected", client_id=client_id)


    try:
        while True:
            data = await websocket.receive_json()
            try:
                message = WebSocketMessage.model_validate(data)
                message.from_id = client_id
                response = await handle_msg(message)
                if response is not None:

                    await broadcast(response, websocket)
            except ValueError as e:
                logger.exception("invalid_message_format", error=str(e), client_id=client_id)
                raise InvalidMessageFormat() from None
    except WebSocketDisconnect:
        remove_client(client_id)
    except Exception as e:
        logger.exception("websocket_error", error=str(e), client_id=client_id)
        raise


def add_client(websocket: WebSocket) -> str:
    """Add a new client and return its client ID."""
    client_id = str(uuid.uuid4())
    clients[client_id] = {"websocket": websocket, "state": {}}
    logger.info("client_connected", client_id=client_id, connected_clients=len(clients))
    return client_id


def remove_client(client_id: str) -> None:
    """Remove a client by its ID."""
    if client_id in clients:
        del clients[client_id]
        logger.info("client_disconnected", client_id=client_id)


def update_client_state(client_id: str, **kwargs: Any) -> None:
    """Update the state information for a client."""
    if client_id in clients:
        clients[client_id]["state"].update(kwargs)


def get_client_state(client_id: str) -> dict[str, Any] | None:
    """Retrieve the state information for a client by client ID."""
    return clients.get(client_id, {}).get("state")


async def handle_msg(message: WebSocketMessage) -> WebSocketMessage | None:
    """Handle an incoming WebSocket message."""
    logger.debug("message_received", message=message.model_dump())
    #print("message received:", message.payload)
    print("message received:", message)
    
    handlers = get_handlers(HandlerType.SERVER)
    if message.event_name in handlers:
        logger.info("handling_event", event_name=message.event_name)
        return await handlers[message.event_name](message)
    return message


async def broadcast(message: WebSocketMessage, sender: WebSocket) -> None:
            
                    
    """Broadcast a message to appropriate clients."""
    message_data = message.model_dump()
    targets: list[WebSocket] = []
    print("broadcasting message:", message)
    if message.to == "all":
        targets = [data["websocket"] for data in clients.values()]
    elif message.to == "others":
        targets = [data["websocket"] for cid, data in clients.items() if data["websocket"] != sender]
    else:
        target_data = next((data for cid, data in clients.items() if cid == message.to), None)
        if target_data:
            targets = [target_data["websocket"]]

    logger.debug("broadcasting_message", message=message_data, num_targets=len(targets))

    for websocket in targets:
        try:
            # Find client_id for this websocket
            client_id = next(cid for cid, data in clients.items() if data["websocket"] == websocket)
            await websocket.send_json(message_data)
            logger.debug("message_sent", client_id=client_id)
        except Exception as e:
            # Find client_id for this websocket
            client_id = next(cid for cid, data in clients.items() if data["websocket"] == websocket)
            logger.exception("broadcast_error", error=str(e), client_id=client_id)


async def close_client_connection(client_id: str) -> None:
    """Close a client connection."""
    if client_id in clients:
        del clients[client_id]

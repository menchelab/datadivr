from math import asin, cos, radians, sin, sqrt

from datadivr import BackgroundTasks, app
from datadivr.handlers.registry import HandlerType, websocket_handler
from datadivr.transport.messages import create_message, send_message
from datadivr.transport.models import WebSocketMessage
from datadivr.transport.server import clients, get_client_state, update_client_state
from datadivr.utils.logging import get_logger, setup_logging
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import  Request
import json
import string
import random
import shutil
from fastapi import File, Form, UploadFile, Request, FastAPI, HTTPException
from os import listdir

# Initialize logging first, before getting the logger
setup_logging()
logger = get_logger(__name__)



import os

userdb = {}
taskdata = {}
serverURL = ""
serverWS = ""
localserver = True

storage_path = os.getenv("PERSISTANT_PATH", "examples/gameserver/")
userskin_path = ""
tasks_path = ""
tracks_path = ""

if storage_path != "examples/gameserver/":
    localserver = False
print("we use:", storage_path)

if localserver:
    userskin_path = "userskins"
else:
    userskin_path = os.path.join(storage_path, "userskins")

tasks_path =  os.path.join(storage_path,  'tasks') 
tracks_path = os.path.join(storage_path,  'tracks') 

# debug open /storage, list all files, print
persistantFiles = os.listdir(storage_path)
print(persistantFiles)
if "users.json" not in persistantFiles:
    print("not found")
    with open(storage_path + 'users.json', 'w') as f:
        data = {"users":[]}
        json.dump(data, f)

if os.path.isdir(userskin_path):
    print(os.listdir(userskin_path))
else:
    print("Skins Doesn't exists")
    os.mkdir(userskin_path)

if os.path.isdir(tasks_path):
    print(os.listdir(tasks_path))
else:
    print("tasks Doesn't exists...copying files")
    os.mkdir(tasks_path)
    shutil.copytree("examples/gameserver/tasks", tasks_path, dirs_exist_ok=True)
    print(os.listdir(tasks_path))


if os.path.isdir(tracks_path):
    print(os.listdir(tracks_path))
else:
    print("tasks Doesn't exists")
    os.mkdir(tracks_path)

print("Serving userskins from:", userskin_path)
print("Absolute path:", os.path.abspath(userskin_path))
print("Files:", os.listdir(userskin_path))


if localserver:
    serverURL = "http://127.0.0.1:8765"
    serverWS = "ws://localhost:8765/ws"
else:
    serverURL = "https://cloudbase.lab.lbi-netmed.com"
    serverWS = "wss://cloudbase.lab.lbi-netmed.com/ws"

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/userskins", StaticFiles(directory=userskin_path), name="userskins")
templates = Jinja2Templates(directory="templates")

task_dir = os.path.join(os.path.dirname(__file__),  'tasks')
taskfiles = os.listdir(task_dir)
taskdata = {"tasks":[]}

for t in taskfiles:
    with open('examples/gameserver/tasks/'+ t, 'r', encoding='utf-8') as f:
        #global userdb 
        thistask = json.load(f)
        if "track" not in thistask:
            thistask["track"] = 'none'
        if "tracks" not in thistask:
            thistask["tracks"] = []
        print(thistask)

        taskdata["tasks"].append(thistask)
        f.close()

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def searchUser (name,pw):
    for user in userdb["users"]:
        if user["name"] == name:
            if user["pw"] == pw:
                return user
    return None

def getUser (name):
    for user in userdb["users"]:
        if user["name"] == name:   
            return user
    return None 





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
            with open(userskin_path + "/" + file.filename, "wb") as f:
                f.write(contents)
                print("write file")

        except Exception:
            raise HTTPException(status_code=500, detail='Something went wrong')
        finally:
            file.file.close()
            with open('examples/gameserver/users.json', 'w', encoding='utf-8') as f:
        #global userdb 
                json.dump(userdb,f)
                f.close()

        return {"message": f"Welcome {name} ! your Password is {pw}"}
# HTML ROUTE
@app.get("/createAccount")
async def newaccount(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request, "json_data":  {"tasks":taskfiles, "serverURL":serverURL}})

@app.get("/clients")
async def showclients():
    print("clients:", clients)
    #return json.dumps(clients)

@app.get("/test")
async def test(request: Request):
    
    print(taskdata["tasks"][1])
    #return templates.TemplateResponse(request=request, name="client.html", context={"name": {"ree":123}, "tex": "reee"})
    return templates.TemplateResponse("client.html", {"request": request, "json_data":  {"tasks":taskfiles, "serverURL":serverURL, "serverWS":serverWS}})

@app.get("/cloudbase1337/{name}/{pw}", response_class=HTMLResponse)
async def multiplayermap(request: Request, name: str, pw: str):
    
    thisuser = searchUser(name,pw)
    print(thisuser)  
    if thisuser is None:
        return templates.TemplateResponse("login.html", {"request": request, "json_data":  {"tasks":taskfiles, "serverURL":serverURL}})
    else:
        #return templates.TemplateResponse(request=request, name="client.html", context={"name": thisuser["name"], "tex": thisuser["tex"], "json_data": taskdata})

        return templates.TemplateResponse("client.html", {"request": request, "json_data": {"tasks":taskfiles, "user":thisuser, "livetask":5, "serverURL":serverURL, "serverWS":serverWS}})
    #return templates.TemplateResponse(request=request)











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
        Name = data.get("name")
        latitude = data.get("lat")
        longitude = data.get("long")
        altitude = data.get("alt")
        rotation_x = data.get("rot_x")
        rotation_y = data.get("rot_y")
        rotation_z = data.get("rot_z")
        aircraft_type = data.get("type")
        animation_state = data.get("anim")
        Tex = data.get("tex")
        Tp = data.get("tp")
        Flag = data.get("flag")
        '''
        if not all(
            isinstance(x, int | float | any)
            for x in [name, latitude, longitude, altitude, rotation_x, rotation_y, rotation_z, aircraft_type, animation_state]
        ):
            for x in [
                name,
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
        '''
        # Retrieve the current name or use a default if not set
        state = get_client_state(message.from_id)
        current_name = state.get("name", "Unknown") if state else "Unknown"

        # Update client state
        update_client_state(
            message.from_id,
            name=Name,
            lat=latitude,
            long=longitude,
            alt=altitude,
            rot_x=rotation_x,
            rot_y=rotation_y,
            rot_z=rotation_z,
            type=aircraft_type,
            anim=animation_state,
            tp = Tp,
            flag = Flag,
            tex=Tex,
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
                    "tp" :  other_state.get("tp"),
                    "flag":  other_state.get("flag"),
                    "tex":  other_state.get("tex"),
                })

        # also send if no nearby clients, to potentially clean old clients, could be improved:
        # TODO: check if last update was already empty for this client, if so, skip

        # if nearby_clients: # only send if there are nearby clients

        message = create_message(
            event_name="GAMESERVER_NEARBY_UPDATE", payload={"nearby_clients": nearby_clients}, to=client_id
        )
        await send_message(client_data["websocket"], message)



@websocket_handler("GAMESERVER_CLIENT_GPSTRACK", HandlerType.SERVER)
async def gpstrack_handler(message: WebSocketMessage) -> None:
    
    filename = message.payload["taskname"] + '_' + message.payload["name"] + '_' + message.from_id[:5]+ '_' + str(message.payload["rtime"])
    print(filename)
    
    with open('examples/gameserver/tracks/'+ filename +'.json', 'w', encoding='utf-8') as f:
        json.dump(message.payload,f)
    f.close()

    #print(message.payload)
    

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
        print("set_name_handler payload:", message.payload)
        name = message.payload.get("name", "")
        tex = message.payload.get("tex", "")
        if not isinstance(name, str) or not name.strip():
            logger.error("Invalid name format")
            return

        # Get existing state to preserve other fields
        existing_state = get_client_state(message.from_id) or {}

        # Create new state dict with updated name
        new_state = existing_state.copy()
        new_state["name"] = name.strip()
        new_state["tex"] = tex.strip()

        # Update state with all fields
        update_client_state(message.from_id, **new_state)
        logger.debug("Updated client name", client_id=message.from_id, name=name)



    except Exception as e:
        logger.exception("Error handling GAMESERVER_CLIENT_SETNAME", error=str(e))


'''
@websocket_handler("GAMESERVER_CLIENT_GETTASKLIST", HandlerType.SERVER)
async def set_tasklist_handler(message: WebSocketMessage) -> None:
    import os
    
    filepath = os.path.dirname(os.path.realpath(__file__))
    #parent = os.path.abspath(os.path.join(filepath, os.pardir))
    taskfiles = os.listdir(filepath + "/tasks")

    try:
        return WebSocketMessage(event_name="TASKLIST", payload={"tasks":taskfiles}, to=message.from_id)
    
    except Exception as e:
        logger.exception("Error handling GAMESERVER_CLIENT_SETNAME", error=str(e))
'''

@websocket_handler("get_task", HandlerType.SERVER)
async def set_task_handler(message: WebSocketMessage) -> None:
    try:
        index = message.payload.get("index", "")
        track_dir = os.path.join(os.path.dirname(__file__),  'tracks')
        trackfiles = os.listdir(track_dir)
        print(trackfiles)
        tname = taskdata["tasks"][index]["name"]
        matchingtracks = []
        for tr in trackfiles:
            name = tr.split("_")
            if name[0] == tname:
                with open('examples/gameserver/tracks/'+tr, 'r', encoding='utf-8') as f:
        #global userdb 
                    thistr = json.load(f)
                    matchingtracks.append(thistr)
                f.close()

        for t in matchingtracks:
            thisu = getUser(t["name"])
            tex = ""
            flag = "https://flagcdn.com/de.svg"
            if thisu == None:
                tex = "1.png"
            else:
                tex = thisu["tex"]
                flag = thisu["flag"]
            t["tex"] = tex
            t["flag"] = flag


        
        sortedtracks = sorted(matchingtracks, key=lambda k: k.get('rtime', 0), reverse=False)

        taskdata["tasks"][index]["tracks"] = sortedtracks

        return WebSocketMessage(event_name="TASK", payload=taskdata["tasks"][index], to=message.from_id)
    
    except Exception as e:
        logger.exception("Error handling GAMESERVER_CLIENT_SETNAME", error=str(e))



if __name__ == "__main__":
    import uvicorn
    #global userdb



    # check if /storage/users.json exist, if not create with default


    with open('examples/gameserver/users.json', 'r', encoding='utf-8') as f:
        #global userdb 
        userdb = json.load(f)
        f.close()
    #print(userdb)
    if localserver:
        uvicorn.run(app, host="127.0.0.1", port=8765)
    else:
        uvicorn.run(app, host="0.0.0.0", port=8765)
    print("post start")

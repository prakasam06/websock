from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Websocket Demo</title>

    </head>
    <body>
    <div>
        <center>
        <h1>Scrollbar and Telemetry Example</h1>
            <br/>
            <br/>
            <div style="display:flex;width:100%;">
                    <fieldset style="width:75%">
                        <legend>Scrollbar Example</legend>
                        <input type="range" class="form-control" id="range" autocomplete="off" onChange="sendData(event)" min="0" max="100" value="0" />  
                        <br/>
                        <span id='rangeValue' class="mt-5">0</span>
                    </fieldset>
                    <fieldset style="width:25%">
                        <legend>Telemetry Example</legend>
                        </b><span id='telemetryValue' class="mt-5">50</span>
                    </fieldset>
                    
            </div>
            <div style="width:25% margin-top:2rem">
            <img  id="videoFrame" width="640" height="480" />
            </div>
        </center>
    </div>
    
        <script> 
            var ws = new WebSocket(`ws://localhost:8000/ws/642003`);

            ws.onmessage = function(event) {
                var messages = document.getElementById('rangeValue')
                var input = document.getElementById("range")
                var telemetry = document.getElementById('telemetryValue')
                var data = JSON.parse(event.data)
                if (data.video && data.video.ret) {
                    const frameData = data.video.frame;
                    console.log(frameData)
                    document.getElementById('videoFrame').src = `data:image/jpeg;base64,${frameData}`;
                }

                if(data.Telemetry_update){
                telemetry.innerHTML = data.telemetry  
                
                }

                if(data.scrollbar_update){
                input.value = data.scrollBar
                messages.textContent = data.scrollBar
                }
            };

            function sendData(event) {
                var input = document.getElementById("range")
                
                var data = JSON.stringify({"scrollBar": input.value, "telemetry": 0})
                console.log(data)
                ws.send(data)

                var range = document.getElementById('rangeValue').textContent = event.data      
                event.preventDefault()  
            }
        </script>
    </body>
</html>
"""

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_json(message)

    
manager = ConnectionManager()


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try: 
        while True:
            data = await websocket.receive_json()

            await manager.send_personal_message(data, websocket)
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)               
        await manager.broadcast(f"Client #{client_id} has left the chat")



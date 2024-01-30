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
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">

    </head>
    <body>
    <div class="m2 w-50 d-flex justify-content-center">
   <h1>Drag the Slider !!</h1>
    </div>
    <div class="container mt-3">
        <input type="range" class="form-control" id="range" autocomplete="off" onChange="sendData(event)"/>  
        <span id='rangeValue' class="mt-5"></span>    
    </div>
    
        <script>    
            var ws = new WebSocket(`ws://localhost:8000/ws/642003`);

            ws.onmessage = function(event) {
                var messages = document.getElementById('rangeValue')
                var input = document.getElementById("range")
                input.value = event.data    
                messages.textContent = event.data
            };

            function sendData(event) {
                var input = document.getElementById("range")
                ws.send(input.value)
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

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    
manager = ConnectionManager()


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try: 
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(data, websocket)
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)               
        await manager.broadcast(f"Client #{client_id} has left the chat")



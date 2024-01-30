from tkinter import *
import websocket
import threading
import json

def send_scrollbar_value(value):
    global ws
    global telemetry
    if ws:
        ws.send(json.dumps({"scrollBar": value, "telemetry": telemetry}))

def send_telemetry_value(value):
    global ws
    global scrollBar
    if ws:
        ws.send(json.dumps({"scrollBar": scrollBar, "telemetry": value}))


def websocket_thread():
    global ws
    global scrollBar
    ws = websocket.create_connection("ws://localhost:8000/ws/642003")
    while True:
        data = json.loads(ws.recv())
        scrollBar = data["scrollBar"]
        print(data)
        root.after(0, update_status_bar, data["scrollBar"])

def update_status_bar(value):
    s_bar.set(value)
# This program is a simple test bed for developing a web interface
# 
# TODO
# -add a python webserver that can interface with this python GUI
# -implement bi-directional communication from this python program to the web UI (websockets?)

root = Tk()

# Scrollbar example
# -----------------
# Used to demonstrate control of a function in the python GUI and the HTML gui
# Changing the slider in python should update the corresponding slider in the HTML UI
# Changing the slider in HTML UI should update the python UI
s_frame = LabelFrame(root, text="Scrollbar Example")
s_frame.grid(row=0, column=0, padx=10, pady=10)


s_bar = Scale(s_frame, orient="horizontal", length=200,command=send_scrollbar_value)
s_bar.pack(expand=True)


# Telemetry example
# -----------------
# Used to demonstrate sending data from python to the web UI
# The web UI should be updated each time the timer value changes so it shows
# the same value as the python UI
timer = 0

def timer_service():
    global timer
    global t_string
    global telemetry
    timer+=1
    t_string.set(str(timer))
    send_telemetry_value(str(timer))
    telemetry = str(timer)
    root.after(1000, timer_service)

t_frame = LabelFrame(root, text="Telemetry Example")
t_frame.grid(row=0, column = 1, padx=10, pady=10, sticky=NSEW)

t_string = StringVar()
t_string.set(str(timer))
t_label = Label(t_frame,textvariable=t_string)
t_label.pack(expand=True)

root.after(1000,timer_service)

ws = None
scrollBar = 0
telemetry = 0

thread = threading.Thread(target=websocket_thread)
thread.daemon = True 
thread.start()

mainloop()

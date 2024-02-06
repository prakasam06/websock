from tkinter import *
import websocket
import threading
import json
from PIL import Image, ImageTk
import cv2
import base64
import time


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

def send_video_frame(ret,frame):
    global ws
    global scroolbar
    global telemetry
    if ws:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]  # Adjust JPEG quality for balance between quality and size
        result, encoded_frame = cv2.imencode('.jpg', frame, encode_param)
        if result:
            encoded_frame_base64 = base64.b64encode(encoded_frame).decode('utf-8')
            # Send the encoded frame over WebSocket
            ws.send(json.dumps({"scrollBar": scrollBar, "telemetry": telemetry ,"video": {"frame": encoded_frame_base64, "ret": ret}}))


def websocket_thread():
    global ws
    global scrollBar
    ws = websocket.create_connection("ws://localhost:8000/ws/642003")
    while True:
        data = json.loads(ws.recv())
        scrollBar = data["scrollBar"]
        print(data)
        root.after(0, update_status_bar, data["scrollBar"])

def open_stream_window():
    print('videooo')
    stream_window = Toplevel(root)
    stream_window.title("Stream Window")
    
    video_label = Label(stream_window)
    video_label.pack()
    # this 1 indicates the usb port -- i think so
    cap = cv2.VideoCapture(0)
    update_video(cap,video_label)

def update_video(cap,video_label,fps=15):
    if cap is None or not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    interval = int(1000 / fps)
    
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_LINEAR)
        
        send_video_frame(ret, frame)
        
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk  
        video_label.configure(image=imgtk)
        
        video_label.after(interval, lambda: update_video(cap, video_label, fps))
    else:
        # 
        cv2.imshow('USB Webcam', frame)
        print("Error: Failed to capture frame.")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Quitting...")
            cap.release()
        # 
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
           
video_handler_frame = LabelFrame(root, text="Video Handler")
video_handler_frame.grid(row=1, column=0, padx=10, pady=10, sticky=NSEW)

video_handler_frame.start_button =Button(video_handler_frame, text="Start Stream",command=open_stream_window)
video_handler_frame.start_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")


root.after(1000,timer_service)

ws = None
scrollBar = 0
telemetry = 0

thread = threading.Thread(target=websocket_thread)
thread.daemon = True 
thread.start()
mainloop()

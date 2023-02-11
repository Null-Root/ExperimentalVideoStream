import imutils
import pickle
import struct
import cv2
import numpy as np
import socket
import sys
import threading
import time

################################### Socket Connection ###################################

conn_list = []
is_run_thread = True

def server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    # TCP
        ServerInfo = ('127.0.0.1', 9999)
        s.bind(ServerInfo)
        s.listen()
        print(f'Server is Listening on {ServerInfo}')
        while True:
            conn, addr = s.accept()

            # Add Client To List
            conn_list.append(conn)

T = threading.Thread(target=server)
T.daemon = True
T.start()


################################### Video Stream ###################################

capture = cv2.VideoCapture(0)

while capture.isOpened():
    ret, frame = capture.read()

    #cv2 to string
    frame = imutils.resize(frame, width=640)
    a = pickle.dumps(frame)
    message = struct.pack("Q",len(a))+a
    
    for conn in conn_list:
        conn.sendall(message)

    cv2.imshow('Display', frame)

    # Case Insensitive Check
    if ord(chr(cv2.waitKey(1) & 0xFF).lower()) == ord('b'):
        break
        
capture.release()
cv2.destroyAllWindows()
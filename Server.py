import imutils
import pickle
import struct
import cv2
import numpy as np
import socket
import sys
import threading
import time


################################### Video Stream ###################################
class VideoHandler:
    def __init__(self) -> None:
        self.ret = False
        self.frame = None
        self.capture = None

    def get_frame(self):
        return self.ret, self.frame

    def start_capture(self):
        self.capture = cv2.VideoCapture(0)

        while self.capture.isOpened():
            self.ret, self.frame = self.capture.read()

            if self.ret == False:
                continue

            cv2.imshow('Server', self.frame)

            # Case Insensitive Check
            if ord(chr(cv2.waitKey(1) & 0xFF).lower()) == ord('b'):
                break

        self.capture.release()
        cv2.destroyAllWindows()


################################### Socket Connection ###################################
class ServerTCP:
    def __init__(self, ServerInfo) -> None:
        self.ServerInfo = ServerInfo
        self.conn_list = []

    def start_services(self):
        self.video_handler = VideoHandler()
        T = threading.Thread(target=self.video_handler.start_capture)
        T.daemon = True
        T.start()
        

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY)
            s.bind(self.ServerInfo)
            s.listen()
            print(f'Server is Listening on {self.ServerInfo}')
            while True:
                conn, addr = s.accept()

                # Add Client To List
                self.conn_list.append(conn)

                # Handle Client
                T = threading.Thread(target=self.handle_client, args=(conn, addr))
                T.start()

    def handle_client(self, conn, addr):
        print(f'{addr} connected to Server')
        try:
            while True:
                ret, frame = self.video_handler.get_frame()
                if ret:
                    # Send frame to client
                    self.unicast(conn, frame)
        except:
            self.conn_list.remove(conn)
    
    def unicast(self, conn, frame):
        frame_bytes = self.convert_frame_to_bytes(frame)
        conn.sendall(frame_bytes)

    def convert_frame_to_bytes(self, frame):
        adjframe = imutils.resize(frame, width=640)
        d_frame = pickle.dumps(adjframe)
        return struct.pack("Q",len(d_frame)) + d_frame

s = ServerTCP(('127.0.0.1', 9999))
s.start_services()
s.start_server()
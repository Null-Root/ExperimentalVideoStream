import imutils
import pickle
import struct
import cv2
import numpy as np
import socket
import sys
import threading
import time


class ClientTCP:
    def __init__(self, ServerInfo: tuple[str, int]):
        self.Limits = 4096
        self.ServerInfo = ServerInfo
        self.payload_size = struct.calcsize("Q")
        self.data = b""

    def connect_to_server(self) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.s:
            try:
                self.s.connect(self.ServerInfo)
                self.show_video_feed()
            except:
                print('Connection Failed, Server is Down')
                time.sleep(1.5)
        return False

    def show_video_feed(self):
        while True:
            frame = self.fetch_and_convert_frames()

            cv2.imshow('Client', frame)

            # Case Insensitive Check
            if ord(chr(cv2.waitKey(1) & 0xFF).lower()) == ord('b'):
                break
    
    def fetch_and_convert_frames(self):
        while len(self.data) < self.payload_size:
            packet = self.s.recv(4096)
            if not packet: break
            self.data += packet
        packed_msg_size = self.data[:self.payload_size]
        self.data = self.data[self.payload_size:]
        msg_size = struct.unpack("Q",packed_msg_size)[0]
                
        while len(self.data) < msg_size:
            self.data += self.s.recv(1_048_576)
        frame_data = self.data[:msg_size]
        self.data  = self.data[msg_size:]
        return pickle.loads(frame_data)

ClientTCP(('127.0.0.1', 9999)).connect_to_server()
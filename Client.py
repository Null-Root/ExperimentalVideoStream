import math
import struct
import cv2
import socket
import numpy as np

################################### Socket Connection ###################################
class Client:
    def __init__(self, server_info):
        self.server_info = server_info
        self.MAX_SIZE = (2**16) - 64
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def client_stuff(self):
        try:
            self.s.settimeout(1)
            dat = b''
            while True:
                msgFromClient       = "OK"
                bytesToSend         = msgFromClient.encode('utf-8')
                self.s.sendto(bytesToSend, self.server_info)
                while True:
                    try:
                        seg, addr = self.s.recvfrom(self.MAX_SIZE)
                    except Exception as e:
                        print(e)
                        break
                    if struct.unpack("B", seg[0:1])[0] > 1:
                        dat += seg[1:]
                    else:
                        dat += seg[1:]
                        img = cv2.imdecode(np.frombuffer(dat, dtype=np.uint8), 1)
                        cv2.imshow('Client', img)
                        dat = b''
                        break
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except Exception as e:
            print(e)
            self.s.close()


s = Client(('192.168.1.20', 12345)).client_stuff()

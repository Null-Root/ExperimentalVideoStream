import threading
from VideoStream import VideoHandler
import math
import struct
import cv2
import socket

################################### Socket Connection ###################################
class Server:
    def __init__(self, server_info):
        self.server_info = server_info
        self.MAX_SIZE = (2**16) - 64
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(server_info)

        self.video_handler = VideoHandler()
        T = threading.Thread(target=self.video_handler.start_capture)
        T.daemon = True
        T.start()
    
    def server_stuff(self):
        try:
            while True:
                ret, frame = self.video_handler.get_frame()
                if ret == False:
                    continue

                bytesAddressPair = self.s.recvfrom(4096)
                address = bytesAddressPair[1]
                print(bytesAddressPair)

                byte_arr = self.convert_frame_to_byte_arr(frame)

                for frame_byte in byte_arr:
                    self.s.sendto(frame_byte, address)
                
                print('SUCCESS')

        except Exception as e:
            print(e)
            self.s.close()
    
    def convert_frame_to_byte_arr(self, frame):
        byte_arr = []
        img_enc = cv2.imencode('.jpg', frame)[1]
        data = img_enc.tostring()
        size = len(data)
        segments_count = math.ceil(size/(self.MAX_SIZE))
        segment_start = 0
        while segments_count:
            segment_end = min(size, segment_start + self.MAX_SIZE)
            byte_arr.append(struct.pack("B", segments_count) + data[segment_start:segment_end])
            segment_start = segment_end
            segments_count -= 1
        return byte_arr

s = Server(('127.0.0.1', 9999)).server_stuff()
import zlib
from VideoStreamLib import VideoStream
import cv2
import math
import socket
import struct
import threading

'''
Video Port Range: 5001 - 5200
'''

class UDPServer:
    def __init__(self, server_info):
        self.MAX_SIZE = (2 ** 16) - 64
        self.server_info = server_info
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(server_info)
        self.s.settimeout(0.8)

    def startOpenCV(self):
        self.video_handler = VideoStream()
        self.video_handler.start_capture()
        T = threading.Thread(target=self.video_handler.handle_capturing)
        T.daemon = True
        T.start()

    def startServer(self):
        print(f'UDP Server at {self.server_info}')
        self.startOpenCV()
        self.serverProcess()
    
    def serverProcess(self):
        try:
            # Server Process Loop
            while True:
                ret, frame = self.video_handler.get_frame()
                if ret == False:
                    continue
                msg, addr = self.s.recvfrom(4096)
                byte_arr = self.convertFramesToBytes(frame)
                for frame_byte in byte_arr:
                    self.s.sendto(frame_byte, addr)
                
                self.s.sendto(b'DONE', addr)
        except Exception as ex:
            print('Closing Process...')

    def convertFramesToBytes(self, frame):
        f_bytes = []

        # Turn a frame to bytes
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        raw_img_bytes = cv2.imencode('.jpg', frame, encode_param)[1].tobytes()

        # Compress frame to bytes
        img_bytes = zlib.compress(raw_img_bytes)
        size = len(img_bytes)

        # Segment bytes
        segments_count = math.ceil(size / self.MAX_SIZE)
        for i in range(segments_count):
            segment_start = i * self.MAX_SIZE
            segment_end = min(size, segment_start + self.MAX_SIZE)
            f_bytes.append(struct.pack("B", segments_count) + img_bytes[segment_start:segment_end])
        return f_bytes

u = UDPServer(('127.0.0.1', 9999)).startServer()
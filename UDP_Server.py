import zlib
from VideoStreamLib import VideoStream
import cv2
import math
import socket
import struct
import threading

'''
[TCP] Hub Port: 9999
[UDP] Video Port Range: 5001 - 5200 (001-190[Default], 191-200[Buffer for accidental overflow])
[TCP] Text Port Range: 5001 - 5200 {NOT YET IMPLEMENTED}
'''

class UDPServer:
    def __init__(self, server_info):
        self.MAX_SIZE = (2 ** 16) - 64
        self.server_info = server_info
        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_socket.bind(server_info)

        self.port_in_use = []

    def startOpenCV(self):
        self.video_handler = VideoStream()
        self.video_handler.start_capture()
        T = threading.Thread(target=self.video_handler.handle_capturing)
        T.daemon = True
        T.start()
    
    def handleClients(self):
        # Listen for clients
        # Serve one client at a time
        self.main_socket.listen()

        while True:
            try:
                # Accept Client
                conn, addr = self.main_socket.accept()

                # Check if server if full
                if len(self.port_in_use) >= 190:
                    print("Server is full")
                    continue

                # For each connection, provide a new port number
                newPort = 5001
                while True:
                    if newPort in self.port_in_use:
                        newPort += 1
                    else:
                        break   
                
                # Assign connection to port number
                self.port_in_use.append(newPort)

                # Send Port to use to client
                conn.sendall(str(newPort).encode('utf-8'))

                # Create new thread
                servProcThread = threading.Thread(target=self.serverProcess, args=[newPort])
                servProcThread.start()
            except Exception as ex:
                print(ex)
                break
        
        # Close Main Socket
        self.main_socket.close()

    def startServer(self):
        print(f'TCP Server at {self.server_info}')
        self.startOpenCV()
        self.handleClients()
    
    def serverProcess(self, client_video_port: int):
        print(f"New socket at Port {client_video_port} [UDP]")

        # Create New Socket for the client
        video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        video_socket.bind((self.server_info[0], client_video_port))
        video_socket.settimeout(1)

        # Server Process Loop
        try:
            while True:
                # Get frame from opencv
                ret, frame = self.video_handler.get_frame()

                # Check if frame is present
                if ret == False:
                    continue

                # Wait for client
                msg, addr = video_socket.recvfrom(4096)

                # Prepare frame byte(s)
                byte_arr = self.convertFramesToBytes(frame)
                for frame_byte in byte_arr:

                    # Send All bytes to user
                    video_socket.sendto(frame_byte, addr)
                
                # Send "DONE" if all bytes to a frame has been sent
                video_socket.sendto(b'DONE', addr)
        except Exception as ex:
            print(ex)
            print(f'Error Encountered, Closing Process with Port {client_video_port}')
        
        # Remove port from list
        self.port_in_use.remove(client_video_port)

        # Close Socket
        video_socket.close()

    def convertFramesToBytes(self, frame):
        f_bytes = []

        # Turn a frame to bytes
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        raw_img_bytes = cv2.imencode('.jpg', frame, encode_param)[1].tobytes()

        # Compress frame bytes
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
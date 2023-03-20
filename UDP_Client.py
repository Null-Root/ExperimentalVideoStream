import zlib
import struct
import cv2
import socket
import numpy as np


class UDPClient:
    def __init__(self, server_info):
        self.server_info = server_info
        self.MAX_SIZE = 2 ** 16
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.settimeout(0.8)
    
    def clientProcess(self):
        while True:
            # Send a message to the server to receive a frame
            # Receive the frame data bytes from the server
            # Loop until all bytes for the frame has been received
            byte_arr = []
            while True:
                try:
                    self.s.sendto(b"send_frame", self.server_info)
                    data, addr = self.s.recvfrom(self.MAX_SIZE)
                    byte_arr.append(bytes(data))

                    # Check If End of Frame
                    if data == b'DONE':
                        break
                except Exception as ex:
                    print(ex)
                    continue

            try:
                # Decode bytes array to frame
                frame =  self.convertBytesToFrame(byte_arr)

                # Show the frame, skip if error
                cv2.imshow('UDP Client', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except:
                continue

        # Clean up
        self.s.close()
        cv2.destroyAllWindows()
    
    def convertBytesToFrame(self, data_arr):
        frame_data = []
        
        # Loop all segments received
        for byte_data in data_arr:
            # Unpack the frame data
            segments_count = struct.unpack("B", byte_data[:1])[0]
            frame_bytes = byte_data[1:]

            # Reconstruct the frame from its segments
            for i in range(segments_count):
                segment_start = i * self.MAX_SIZE
                segment_end = min(len(frame_bytes), segment_start + self.MAX_SIZE)
                frame_data.append(frame_bytes[segment_start:segment_end])
        
        # Combine all bytes to a single frame byte
        frame_bytes = b"".join(frame_data)

        # Decompress to get frame bytes
        frame_bytes = zlib.decompress(frame_bytes)

        # Decode the frame data to a numpy array
        return cv2.imdecode(np.frombuffer(frame_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)

u = UDPClient(('127.0.0.1', 9999)).clientProcess()
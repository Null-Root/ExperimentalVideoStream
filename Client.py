import struct
import cv2
import socket
import pickle


HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 9999  # The port used by the server
payload_size = struct.calcsize("Q")
data = b""
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
while True:
    while len(data) < payload_size:
        packet = s.recv(4096)
        if not packet: break
        data += packet
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q",packed_msg_size)[0]
        
    while len(data) < msg_size:
        data += s.recv(4096)
    frame_data = data[:msg_size]
    data  = data[msg_size:]
    frame = pickle.loads(frame_data)

    cv2.imshow('Client', frame)
    key = cv2.waitKey(1) & 0xFF
    if key  == ord('q'):
        break
s.close()
# Echo server program
import socket

HOST = '123.123.123.2'                 # Symbolic name meaning all available interfaces
PORT = 9930              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))
while True:
    data, addr  = s.recvfrom(1024)
    print "received message:", data
    s.sendto(data, addr)
conn.close()

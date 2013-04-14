# Echo client program
import socket

HOST = '123.123.123.2'    # The remote host
PORT = 9930              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto('Hello, world', (HOST, PORT))
data = s.recv(1024)
s.close()
print 'Received', repr(data)

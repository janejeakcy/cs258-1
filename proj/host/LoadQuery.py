#!/usr/bin/env python
# Xiaohan Li
# Apr. 14, 2013
# POX server load balancing query
# Listen and store blance of servers
import socket
import threading
class LoadQuery:
    """Get load-balancing from servers"""
    HOST = '' #Any
    PORT = 9930
    s = None
    balance = {}
    t = None
    f = True;
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((self.HOST,self.PORT))
    def __del__(self):
        self.s.close()
    def receive(self):
        while self.f:
            data,addr = self.s.recvfrom(1024)
            print 'received balance msg:', data
            result = str(data).split(':')
            self.balance[result[0]] = int(result[1])
            self.s.sendto(data,addr)
    def listen(self):
        self.f = True
        t = threading.Thread(target = self.receive)
        t.start()
    def stop(self):
        self.f = False

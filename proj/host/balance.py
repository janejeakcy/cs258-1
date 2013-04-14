#!/usr/bin/env python
# Xiaohan Li
# Apr. 14, 2013
# POX server load balancing query
# Listen and store blance of servers
import socket
import threading
class loadquery:
    """Get load-balancing from servers"""
    HOST = '' #Any
    PORT = 9930
    s = None
    balance = {}
    t = None
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((HOST,PORT))
    def __del__(self):
        self.s.close()
    def receive(self):
        while True:
            data,addr = s.recvfrom(1024)
            print 'received balance msg:', data
            result = str(data).split(':')
            self.balance[result[0]] = int(result[1])
            self.s.sendto(data,addr)
    def listen(self):
        t = threading.Thread(target = self.receive)
        t.start()


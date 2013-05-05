#!/usr/bin/env python
# Xiaohan Li
# Apr. 14, 2013
# POX server load balancing query
# Listen and store blance of servers
import socket
import threading
import collections
import time
total_server_num = 4
class LoadQuery2:
    """Get load-balancing from servers"""
    HOST = '' #Any
    PORT = 9930
    s = None
    balance = collections.defaultdict(lambda: 0)
    t = None
    t1 = None
    f = True
    fi = None
    def receive(self):
        while self.f:
            data,addr = self.s.recvfrom(1024)
            #print 'received balance msg:', data
            result = str(data).split(':')
            if result[1] != None:
                self.balance[result[0]] = int(result[1])
            self.s.sendto(data,addr)
    def write(self):
        while self.f:
            vals = '|'
            for i in range(total_server_num):
                vals = vals + str(self.balance[str(i + 1)]) + '|'
            self.fi.write(vals + '|\n')
            time.sleep(1)
    def listen(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.fi = open('result.txt', 'w')
        self.s.bind((self.HOST,self.PORT))
        self.f = True
        t = threading.Thread(target = self.receive)
        t.start()
        t1 = threading.Thread(target = self.write)
        t1.start()
    def stop(self):
        self.f = False
        self.s.close()
        self.fi.close()

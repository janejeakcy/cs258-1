#!/usr/bin/env python
# Xiaohan Li, Jing Huang
# Apr. 28, 2013
# POX server load balancing query
# Listen and store blance of servers

import socket
import threading
import collections
import time

int server_num = 4

class LoadQuery2:
    """Get load-balancing from servers"""
    HOST = '' #Any
    PORT = 9940
    tcp_server_sock = None
    tcp_client_sock = None
    balance = collections.defaultdict(lambda: 0)
    t = None
    t1 = None
    f = True
    fi = None
    
    def receive(self):
        while self.f:
            self.tcp_client_sock, addr = self.tcp_server_sock.accept()
            while self.f:
                data = self.tcp_client_sock.recv(1024)
                print 'received balance msg:', data
                result = str(data).split(':')
                self.balance[result[0]] = int(result[1])
                self.tcp_client_sock.send(data)
        
    def write(self):
        while self.f:
            vals = '|'
            for i in range(server_num):
                vals = vals + str(self.balance[str(i + 1)]) + '|'
            self.fi.write(vals + '|\n')
            time.sleep(1)

    def listen(self):
        self.tcp_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fi = open('result.txt', 'w')
        self.tcp_server_sock.bind((self.HOST,self.PORT))
        self.f = True
        self.tcp_server_sock.listen(server_num)
        t = threading.Thread(target = self.receive)
        t.start()
        t1 = threading.Thread(target = self.write)
        t1.start()

    def stop(self):
        self.f = False
        self.tcp_server_sock.close()
        self.tcp_client_sock.close()
        self.fi.close()
        

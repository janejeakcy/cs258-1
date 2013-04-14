

from mininet.topo import Topo

class Topo1(Topo):
    def __init__(self):
        Topo.__init__(self)
        h1 = self.addHost('hc1', ip = '10.0.0.1', mac ='00:00:00:00:00:01')
        h2 = self.addHost('hc2', ip = '10.0.0.2', mac ='00:00:00:00:00:02')
        h3 = self.addHost('hc3', ip = '10.0.0.3', mac ='00:00:00:00:00:03')
        h4 = self.addHost('hc4', ip = '10.0.0.4', mac ='00:00:00:00:00:04')
        h5 = self.addHost('hc5', ip = '10.0.0.5', mac ='00:00:00:00:00:05')
        h6 = self.addHost('hc6', ip = '10.0.0.6', mac ='00:00:00:00:00:06')
        h7 = self.addHost('hs1', ip = '10.0.0.7', mac ='00:00:00:00:00:07')
        h8 = self.addHost('hs2', ip = '10.0.0.8', mac ='00:00:00:00:00:08')
        h9 = self.addHost('hs3', ip = '10.0.0.9', mac ='00:00:00:00:00:09')
        h10 = self.addHost('fake', ip = '10.0.0.10', mac ='00:00:00:00:00:10')
        s1 = self.addSwitch('s1')
        self.addLink(s1, h1, bw = 500)
        self.addLink(s1, h2, bw = 500)
        self.addLink(s1, h3, bw = 500)
        self.addLink(s1, h4, bw = 500)
        self.addLink(s1, h5, bw = 500)
        self.addLink(s1, h6, bw = 500)
        self.addLink(s1, h7, bw = 100)
        self.addLink(s1, h8, bw = 200)
        self.addLink(s1, h9, bw = 300)
        self.addLink(s1, h10, bw = 500)

topos = { 'demo1': ( lambda: Topo1() ) }

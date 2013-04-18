from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.node import OVSSwitch, Controller, RemoteController

class Topo2(Topo):
  def __init__(self):
    Topo.__init__(self)
    h1 = self.addHost('h1', ip = '10.0.0.1', mac ='00:00:00:00:00:01')
    h2 = self.addHost('h2', ip = '10.0.0.2', mac ='00:00:00:00:00:02')
    h3 = self.addHost('h3', ip = '10.0.0.3', mac ='00:00:00:00:00:03')
    h4 = self.addHost('h4', ip = '10.0.0.4', mac ='00:00:00:00:00:04')
    h5 = self.addHost('h5', ip = '10.0.0.5', mac ='00:00:00:00:00:05')
    h6 = self.addHost('h6', ip = '10.0.0.6', mac ='00:00:00:00:00:06')
    h7 = self.addHost('h7', ip = '10.0.0.7', mac ='00:00:00:00:00:07')
    h8 = self.addHost('h8', ip = '10.0.0.8', mac ='00:00:00:00:00:08')
    h9 = self.addHost('h9', ip = '10.0.0.9', mac ='00:00:00:00:00:09')
    h10 = self.addHost('fake', ip = '10.0.0.10', mac ='00:00:00:00:00:10')
    s1 = self.addSwitch('s1')
    self.addLink(s1, h1, bw = 500)
    self.addLink(s1, h2, bw = 500)
    self.addLink(s1, h3, bw = 500)
    self.addLink(s1, h4, bw = 500)
    self.addLink(s1, h5, bw = 500)
    self.addLink(s1, h6, bw = 500)
    self.addLink(s1, h7, bw = 500)
    self.addLink(s1, h8, bw = 500)
    self.addLink(s1, h9, bw = 500)
    self.addLink(s1, h10, bw = 500)


def topoTest():
  topo = Topo2()
  net = Mininet(topo = topo,controller = lambda name : RemoteController(name, defaultIP = '192.168.42.1'), link = TCLink, switch = OVSSwitch)
  c0 = net.getNodeByName('c0')

  s1 = net.getNodeByName('h7')
  l1 = s1.linkTo(c0)
  i1 = l1.intf1
  i2 = l1.intf2
  s1.setIP('123.123.123.1', 8, i1)
  c0.setIP('123.123.125.1', 8, i2)

  s2 = net.getNodeByName('h8')
  l1 = s2.linkTo(c0)
  i1 = l1.intf1
  i2 = l1.intf2
  s2.setIP('123.123.123.2', 8, i1)
  c0.setIP('123.123.125.2', 8, i2)

  net.start()
  s1.cmd('route add -net 123.123.125.1 netmask 255.255.255.255 dev' + str(i1))
  s2.cmd('route add -net 123.123.125.2 netmask 255.255.255.255 dev' + str(i1))

  CLI(net)
  net.stop()
  
if __name__ == "__main__":
  topoTest()


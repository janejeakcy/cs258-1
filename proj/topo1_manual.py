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
  net = Mininet(topo = topo,controller = RemoteController, link = TCLink, switch = OVSSwitch)
  net.start()
  hc1, hc2, hc3, hc4, hc5, hc6, hs1, hs2, hs3 = net.getNodeByName('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9')
  servers = [hs1, hs2, hs3]
  clients = [hc1, hc2, hc3, hc4, hc5, hc6]
  filenames = ['test1.dat', 'test2.dat', 'test3.dat', 'test4.dat', 'test5.dat']
  for server in servers:
    result = server.cmd('cd ~/proj/host/mongoose/')
    server.cmd('./mongoose &')
  timeList = []
  for filename in filenames:
    downloadTime = []
    for i in range(2):
      for client in clients:
        client.cmd('cd ~/proj/host/')
        wgetCmd = 'wget 10.0.0.10:8080/cs258/' + filename
        result = client.cmd(wgetCmd).split('\n')
        for line in result:
           if line.find('saved') != -1 or line.find('100%') != -1:
            if line.find('100%') != -1:
              start = line.find('=')
              if start != -1:
                downloadTime.append(float(line[start+1: start+4]))
              print client.IP()
            print line
    print downloadTime
    avg = sum(downloadTime)/len(downloadTime)
    timeList.append(avg)
  print timeList
  net.stop()
if __name__ == "__main__":
  topoTest()


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.node import OVSSwitch, Controller, RemoteController
import json

class Topo2(Topo):
    def __init__(self):
        Topo.__init__(self)
        nodeDict = {}
        for i in range(1, 65):
            if(i<16):
                macStr = '00:00:00:00:00:0'+hex(i)[2:]
            else:
                macStr = '00:00:00:00:00:'+hex(i)[2:]
            ipStr = '10.0.0.'+str(i)
            name = 'hc'+str(i)
            client = self.addHost(name, ip = ipStr, mac = macStr)
            nodeDict[name] = client
        fake = self.addHost('fake', ip = '10.0.0.65', mac = '00:00:00:00:00:41')
        for i in range(1, 17):
            macStr = '00:00:00:00:00:'+hex(i+65)[2:]
            ipStr = '10.0.0.'+str(i+65)
            name = 'hs'+str(i)
            server = self.addHost(name, ip = ipStr, mac = macStr)
            nodeDict[name] = server

        for i in range(1, 15):
            name = 's'+str(i)
            switch = self.addSwitch(name)
            nodeDict[name]=switch

        for i in range(1,65):
            name = 'hc'+str(i)
            self.addLink(nodeDict[name], nodeDict['s1'])
            
        self.addLink(nodeDict['s1'], fake)

        data = self.readData()
        for link in data['links']:
            para = link['para']
            node1 = str(link['node'][0])
            node2 = str(link['node'][1])
            self.addLink(node1, node2, **para)

    def readData(self):
        json_data = open('/home/mininet/demoTopo.json')
        data = json.load(json_data)
        json_data.close()
        return data

def topoTest():
    topo = Topo2()
    net = Mininet(topo = topo,controller = lambda name : RemoteController(name, ip = '192.168.42.1'),link = TCLink, switch = OVSSwitch)
    serverList = []
    c = net.getNodeByName('c0')
    for i in range(1, 17):
        serverName = 'hs'+str(i)
        serverList.append(net.getNodeByName(serverName))
    for i in range(16):
        server = serverList[i]
        link = server.linkTo(c)
        i1 = link.intf1
        i2 = link.intf2
        sIp = '123.123.123.'+str(i)
        cIp = '123.123.124.'+str(i)
        server.setIP(sIp, 8, i1)
        c.setIP(cIp, 8, i2)
        server.cmd('route add -net ' + cIp + 'netmask 255.255.255.255 dev' +str(i1))
        #c.cmd('route add -net ' + sIp + ' dev' +str(i2))
    net.start()
    CLI(net)
    net.stop()

if __name__ == "__main__":
    topoTest()

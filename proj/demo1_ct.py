from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.node import RemoteController

def emptyNet():

    "Create an empty network and add nodes to it."
    net = Mininet(controller=lambda name: RemoteController(name,
defaultIP='192.168.0.125' ), listenPort=6633 )

    info( '*** Adding controller\n' )
    c0 =net.addController( 'c0' )

    info( '*** Adding hosts\n' )
    h1 = net.addHost( 'h1', ip='10.0.0.1' )
    h2 = net.addHost( 'h2', ip='10.0.0.2' )
    h3 = net.addHost( 'h3', ip='10.0.0.3' )
    info( '*** Adding switch\n' )
    s3 = net.addSwitch( 's3' )

    info( '*** Creating links\n' )
    h1.linkTo( s3 )
    h2.linkTo( s3 )
    h3.linkTo( s3 )
    #i1 = h3.linkTo(c0).intf1
    #i1.setIP('c0-eth0 10.0.2.110')
    info( '*** Starting network\n')
    net.start()

    info( '*** Running CLI\n' )
    CLI( net )

    info( '*** Stopping network' )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    emptyNet()

# Copyright 2012 James McCauley
#
# This file is part of POX.
#
# POX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# POX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with POX.  If not, see <http://www.gnu.org/licenses/>.

"""
A simple OpenFlow learning switch that installs rules for
each L2 address.
"""

# These next two imports are common POX convention
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ethernet import ethernet, ETHER_BROADCAST
from pox.lib.util import str_to_bool, dpid_to_str
from pox.lib.addresses import IPAddr, EthAddr
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
from pox.lib.packet.icmp import icmp
from random import *
import math
from pox.lib.revent import *

# Even a simple usage of the logger is much nicer than print!
log = core.getLogger()


# This table maps (switch,MAC-addr) pairs to the port on 'switch' at
# which we last saw a packet *from* 'MAC-addr'.
# (In this case, we use a Connection object for the switch.)

total_host_num = 10
client_num = 6
server_num = 3
mac_port_table = {}
port_mac_table = {}
ip_port_table = {}
port_ip_table = {}

mac_addresses = ["00:00:00:00:00:01", "00:00:00:00:00:02", "00:00:00:00:00:03",
                 "00:00:00:00:00:04", "00:00:00:00:00:05", "00:00:00:00:00:06",
                 "00:00:00:00:00:07", "00:00:00:00:00:08", "00:00:00:00:00:09",
                 "00:00:00:00:00:10"]

ip_addresses = ["10.0.0.1", "10.0.0.2", "10.0.0.3",
                "10.0.0.4", "10.0.0.5", "10.0.0.6",
                "10.0.0.7", "10.0.0.8", "10.0.0.9",
                "10.0.0.10"]

# Handle messages the switch has sent us because it has no
# matching rule.
def _handle_PacketIn (event):
  log.debug("Connection %s at switch %s" % (event.connection, dpid_to_str(event.dpid)))

  packet = event.parsed

  # build up table
  for i in range(0, total_host_num)
    mac_port_table[(event.dpid, EthAddr(mac_addresses[i]))] = i + 1
    port_mac_table[(event.dpid, i + 1)] = EthAddr(mac_addresses[i])
    ip_port_table[(event.dpid,IPAddr(ip_addresses[i]))] = i + 1
    port_ip_table[(event.dpid, i + 1)] = IPAddr(ip_addresses[i])

  if isinstance(packet.next, ipv4):
      log.debug("%i %i IP %s => %s", event.dpid,event.port,
                packet.next.srcip,packet.next.dstip)
      #log.debug("%i %i IP ", event.dpid, event.port)
  elif isinstance(packet.next, arp):
      log.debug("%i %i arp ", event.dpid,event.port)
  elif isinstance(packet.next, icmp):
      log.debug("%i %i icmp ", event.dpid,event.port)
  else:
      log.debug("%i %i not known protocol ", event.dpid, event.port)

  #packet is arp   
  if isinstance(packet.next, arp):
    log.debug("ARP!!!!!!!!!!!!!!!")
    log.debug("destination address is %s" % packet.dst)
    log.debug("source address is %s" % packet.src)
    log.debug("dest ip address %s" %packet.next.protodst)
    
    dst_port = ip_port_table.get((event.dpid,packet.next.protodst))
    log.debug("destnation port is %i" % dst_port)

    #mac address is "ff:ff:ff:ff:ff:ff"
    if packet.dst == EthAddr("ff:ff:ff:ff:ff:ff"):
      msg = of.ofp_packet_out()
      msg.actions.append(of.ofp_action_output(port = dst_port))
      msg.data = event.ofp
      msg.in_port = event.port
      event.connection.send(msg)

    #mac address is not "ff:ff:ff:ff:ff:ff"
    else:
      msg = of.ofp_flow_mod()
      msg.data = event.ofp
      msg.match.dl_dst = packet.dst
      msg.match.dl_src = packet.src
      msg.idle_timeout =  20
      msg.actions.append(of.ofp_action_output(port = dst_port))                                         
      event.connection.send(msg)

  #packet is normal ip
  elif isinstance(packet.next, ipv4):
    log.debug("IP!!!!!!!!!")  
    dst_port = ip_port_table.get((event.dpid,packet.next.dstip))
    log.debug("destnation port is %i" % dst_port)
    msg = of.ofp_flow_mod()
    msg.data = event.ofp
    msg.match.dl_dst = packet.dst
    msg.match.dl_src = packet.src
    msg.idle_timeout =  20
    msg.actions.append(of.ofp_action_output(port = dst_port))
    event.connection.send(msg)
  
  log.debug("Installing at switch %s" % dpid_to_str(event.dpid))


def launch ():
  core.openflow.addListenerByName("PacketIn", _handle_PacketIn)

  log.debug("Initial-Learning switch running.")

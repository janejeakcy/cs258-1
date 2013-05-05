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
from pox.lib.util import str_to_bool, dpid_to_str, str_to_dpid
from pox.lib.addresses import IPAddr, EthAddr
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
from pox.lib.packet.icmp import icmp
from random import *
import math
from pox.lib.revent import *
import LoadQuery2
import collections

# Even a simple usage of the logger is much nicer than print!
log = core.getLogger()

cluster = False
total_cluster_num = 4
round_robin = False
rand = False
fixed = False
load = False
two_rand = True
load_balancing_path = False

round_robin_current_server_num = 1
round_robin_current_servers_num = [1, 1, 1, 1]

total_host_num = 12
total_client_num = 8
total_server_num = 4
total_switch_num = 14

server_count = collections.defaultdict(lambda: 0)
connection_up_count = 0
connection_down_count = 0
q = None

servers = {}
switches_hierarchy = {}
hierarchy_count = 1

# switch name dpid map. 
#switch_name_dpid = defaultdict(lambda:None)
switch_name_dpid = {"sw1": "00-00-00-00-00-01", "sw2": "00-00-00-00-00-02",
                    "sw3": "00-00-00-00-00-03", "sw4": "00-00-00-00-00-04",
                    "sw5": "00-00-00-00-00-05", "sw6": "00-00-00-00-00-06",
                    "sw7": "00-00-00-00-00-07", "sw8": "00-00-00-00-00-08",
                    "sw9": "00-00-00-00-00-09", "sw10": "00-00-00-00-00-0a",
                    "sw11": "00-00-00-00-00-0b", "sw12": "00-00-00-00-00-0c",
                    "sw13": "00-00-00-00-00-0d", "sw14": "00-00-00-00-00-0e"}
switch_dpid_name = {"00-00-00-00-00-01": "sw1", "00-00-00-00-00-02": "sw2",
                    "00-00-00-00-00-03": "sw3", "00-00-00-00-00-04": "sw4",
                    "00-00-00-00-00-05": "sw5", "00-00-00-00-00-06": "sw6",
                    "00-00-00-00-00-07": "sw7", "00-00-00-00-00-08": "sw8",
                    "00-00-00-00-00-09": "sw9", "00-00-00-00-00-0a": "sw10",
                    "00-00-00-00-00-0b": "sw11", "00-00-00-00-00-0c": "sw12",
                    "00-00-00-00-00-0d": "sw13", "00-00-00-00-00-0e": "sw14"}

# switch adjacency map. [sw1][sw2] -> (weight, port of sw1, port of sw2)
#switch_switch_adjacency = defaultdict(lambda:defaultdict(lambda:(None,None,None))
switch_switch_adjacency_8switch = {"sw1": {"sw2": (1, 6, 1), "sw3": (3, 7, 1)},
                           "sw2": {"sw4": (1, 2, 1), "sw5": (2, 3, 1)},
                           "sw3": {"sw5": (1, 2, 2), "sw6": (2, 3, 1)},
                           "sw4": {"sw7": (1, 2, 1)},
                           "sw5": {"sw7": (2, 3, 2), "sw8": (3, 4, 1)},
                           "sw6": {"sw8": (2, 2, 2)}}

switch_switch_adjacency_7switch = {"sw1": {"sw2": (1, 6, 1), "sw3": (2, 7, 1)},
                           "sw2": {"sw4": (1, 2, 1), "sw5": (2, 3, 1)},
                           "sw3": {"sw6": (1, 2, 1), "sw7": (2, 3, 1)}}

switch_switch_adjacency_16server = {"sw1": {"sw2": (5, 66, 1), "sw3": (6, 67, 1), "sw4": (4, 68, 1)},
                           "sw2": {"sw5": (2, 2, 1), "sw6": (5, 3, 1)},
                           "sw3": {"sw5": (1, 2, 2), "sw6": (3, 3, 2)},
                           "sw4": {"sw6": (4, 2, 3), "sw7": (1, 3, 1)},
                           "sw5": {"sw8": (7, 3, 1), "sw9": (2, 4, 1)},
                           "sw6": {"sw9": (1, 4, 2), "sw10": (3, 5, 1)},
                           "sw7": {"sw9": (2, 2, 3), "sw10": (2, 3, 2)},
                           "sw8": {"sw11": (4, 2, 1), "sw12": (2, 3, 1)},
                           "sw9": {"sw12": (3, 4, 2), "sw13": (2, 5, 1)},
                           "sw10": {"sw13": (4, 3, 2), "sw14": (3, 4, 1)}}

switch_switch_adjacency_8server = {"sw1": {"sw2": (5, 18, 1), "sw3": (6, 19, 1), "sw4": (4, 20, 1)},
                           "sw2": {"sw5": (2, 2, 1), "sw6": (5, 3, 1)},
                           "sw3": {"sw5": (1, 2, 2), "sw6": (3, 3, 2)},
                           "sw4": {"sw6": (4, 2, 3), "sw7": (1, 3, 1)},
                           "sw5": {"sw8": (7, 3, 1), "sw9": (2, 4, 1)},
                           "sw6": {"sw9": (1, 4, 2), "sw10": (3, 5, 1)},
                           "sw7": {"sw9": (2, 2, 3), "sw10": (2, 3, 2)},
                           "sw8": {"sw11": (4, 2, 1), "sw12": (2, 3, 1)},
                           "sw9": {"sw12": (3, 4, 2), "sw13": (2, 5, 1)},
                           "sw10": {"sw13": (4, 3, 2), "sw14": (3, 4, 1)}}

switch_switch_adjacency = {"sw1": {"sw2": (5, 10, 1), "sw3": (6, 11, 1), "sw4": (4, 12, 1)},
                           "sw2": {"sw5": (2, 2, 1), "sw6": (5, 3, 1)},
                           "sw3": {"sw5": (1, 2, 2), "sw6": (3, 3, 2)},
                           "sw4": {"sw6": (4, 2, 3), "sw7": (1, 3, 1)},
                           "sw5": {"sw8": (7, 3, 1), "sw9": (2, 4, 1)},
                           "sw6": {"sw9": (1, 4, 2), "sw10": (3, 5, 1)},
                           "sw7": {"sw9": (2, 2, 3), "sw10": (2, 3, 2)},
                           "sw8": {"sw11": (4, 2, 1), "sw12": (2, 3, 1)},
                           "sw9": {"sw12": (3, 4, 2), "sw13": (2, 5, 1)},
                           "sw10": {"sw13": (4, 3, 2), "sw14": (3, 4, 1)}}

switch_switch_adjacency_matrix8 = [[0, 1, 1, 0, 0, 0, 0, 0],
                                  [1, 0, 0, 1, 1, 0, 0, 0],
                                  [1, 0, 0, 0, 1, 1, 0, 0],
                                  [0, 1, 0, 0, 0, 0, 1, 0],
                                  [0, 1, 1, 0, 0, 0, 1, 1],
                                  [0, 0, 1, 0, 0, 0, 0, 1],
                                  [0, 0, 0, 1, 1, 0, 0, 0],
                                  [0, 0, 0, 0, 1, 1, 0, 0]]

switch_switch_adjacency_matrix7 = [[0, 1, 1, 0, 0, 0, 0],
                                  [1, 0, 0, 1, 1, 0, 0],
                                  [1, 0, 0, 0, 0, 1, 1],
                                  [0, 1, 0, 0, 0, 0, 0],
                                  [0, 1, 0, 0, 0, 0, 0],
                                  [0, 0, 1, 0, 0, 0, 0],
                                  [0, 0, 1, 0, 0, 0, 0]]

switch_switch_adjacency_matrix = [[0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                  [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                                  [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                                  [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
                                  [0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                                  [0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0],
                                  [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0],
                                  [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1],
                                  [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]]


switch_iter8 = ["sw1", "sw2", "sw3", "sw4", "sw5", "sw6", "sw7", "sw8"]
switch_iter7 = ["sw1", "sw2", "sw3", "sw4", "sw5", "sw6", "sw7"]
switch_iter = ["sw1", "sw2", "sw3", "sw4", "sw5", "sw6", "sw7", "sw8", "sw9", "sw10", "sw11", "sw12", "sw13", "sw14"]

link_weight = [([0] * total_switch_num) for i in range(total_switch_num)]

# switch to client port map. client_num -> port
switch_client_port78 = {1: 1, 2: 2, 3: 3, 4: 4}           ######### assume all clients are directly connected with one gateway

switch_client_port = {}
for i in range(1, total_client_num + 1):
    switch_client_port[i] = i
    
# switch to server port map. [server_num][switch] -> port
switch_server_port_8switch = {1: {"sw7": 3}, 2: {"sw8": 3}}
switch_server_port_7swtich = {1: {"sw4": 2}, 2: {"sw5": 2}, 3: {"sw6": 2}, 4: {"sw7": 2}}

switch_server_port_16server = {1: {"sw11": 2}, 2: {"sw11": 3}, 3: {"sw11": 4}, 4: {"sw11": 5},
                      5: {"sw12": 3}, 6: {"sw12": 4}, 7: {"sw12": 5}, 8: {"sw12": 6},
                      9: {"sw13": 3}, 10: {"sw13": 4}, 11: {"sw13": 5}, 12: {"sw13": 6},
                      13: {"sw14": 2}, 14: {"sw14": 3}, 15: {"sw14": 4}, 16: {"sw14": 5}}
switch_server_port_8server = {1: {"sw11": 2}, 2: {"sw11": 3}, 3: {"sw12": 3}, 4: {"sw12": 4},
                      5: {"sw13": 3}, 6: {"sw13": 4}, 7: {"sw14": 2}, 8: {"sw14": 3}}

switch_server_port = {1: {"sw11": 2}, 2: {"sw12": 3}, 3: {"sw13": 3}, 4: {"sw14": 2}}

"""client_mac_addresses = [EthAddr("00:00:00:00:00:01"), EthAddr("00:00:00:00:00:02"), EthAddr("00:00:00:00:00:03"), EthAddr("00:00:00:00:00:04")]
                      
server_mac_addresses = [EthAddr("00:00:00:00:00:05"), EthAddr("00:00:00:00:00:06")]
server_mac_addresses1 = [EthAddr("00:00:00:00:00:05"), EthAddr("00:00:00:00:00:06"), EthAddr("00:00:00:00:00:07"), EthAddr("00:00:00:00:00:08")]

fake_mac_address = EthAddr("00:00:00:00:00:10")

client_ip_addresses = [IPAddr("10.0.0.1"), IPAddr("10.0.0.2"), IPAddr("10.0.0.3"), IPAddr("10.0.0.4")]
server_ip_addresses = [IPAddr("10.0.0.5"), IPAddr("10.0.0.6")]
server_ip_addresses1 = [IPAddr("10.0.0.5"), IPAddr("10.0.0.6"), IPAddr("10.0.0.7"), IPAddr("10.0.0.8")]
fake_ip_address = IPAddr("10.0.0.10")"""

client_mac_addresses = []
client_ip_addresses = []
fake_ip_address = IPAddr("10.0.0.9")
fake_mac_address = EthAddr("00:00:00:00:00:09")

for i in range(1, total_client_num + 2):
    if i < 16:
        macStr = '00:00:00:00:00:0'+ hex(i)[2:]
    else:
        macStr = '00:00:00:00:00:'+ hex(i)[2:]
    ipStr = '10.0.0.'+ str(i)
    if i < total_client_num + 1:
        client_mac_addresses.append(EthAddr(macStr))
        client_ip_addresses.append(IPAddr(ipStr))
    else:
        fake_mac_address = EthAddr(macStr)
        fake_ip_address = IPAddr(ipStr)

print fake_ip_address

server_mac_addresses = []
server_ip_addresses = []
for i in range(1, total_server_num + 1):
    macStr = '00:00:00:00:00:' + hex(i + total_client_num + 1)[2:]
    ipStr = '10.0.0.' + str(i + total_client_num + 1)
    server_mac_addresses.append(EthAddr(macStr))    
    server_ip_addresses.append(IPAddr(ipStr))


def calc_switch_hierarchy ():
    global hierarchy_count
    if switches_hierarchy.get(hierarchy_count) is None:
        switches_hierarchy[hierarchy_count] = []
    switches_hierarchy[hierarchy_count].append(switch_iter[0])
    #print hierarchy_count, 'corresponds to', 0
    hierarchy_count += 1
    if switches_hierarchy.get(hierarchy_count) is None:
        switches_hierarchy[hierarchy_count] = []
    temp1 = 0
    temp2 = 0
    for i in range (0, len(switch_switch_adjacency_matrix)):
      if i == temp1 + 1:
        temp1 = temp2
        hierarchy_count += 1        
      for j in range (i + 1, len(switch_switch_adjacency_matrix)):
        if switch_switch_adjacency_matrix[i][j] == 1:
          if switches_hierarchy.get(hierarchy_count) is None:
            switches_hierarchy[hierarchy_count] = []
          if switch_iter[j] not in switches_hierarchy[hierarchy_count]:
            switches_hierarchy[hierarchy_count].append(switch_iter[j])
            #print hierarchy_count, 'corresponds to', j
          if temp2 < j:
            temp2 = j
    hierarchy_count -= 1

def init_link_weight():
  for i in range (0, len(switch_switch_adjacency_matrix)):
    for j in range (i + 1, len(switch_switch_adjacency_matrix)):
      if switch_switch_adjacency_matrix[i][j] == 1:
        link_weight[i][j] = switch_switch_adjacency[switch_iter[i]][switch_iter[j]][0]
        link_weight[j][i] = link_weight[i][j]

############################ need to query switches buffers #############  
def update_link_weight():  
  i = 0
#########################################################################   

class Server (object):

  def __init__ (self, num, mac, ip):

    self.num = num
    self.macAddr = mac
    self.ipAddr = ip
    self.switches_on_path = []
    self.sub_switch_hierarchy = {}
    self.sub_switch_hierarchy_count = 1
    self.end_switch = switch_server_port[self.num].keys()[0]
    self.end_switch_index = switch_iter.index(self.end_switch)

  def _calc_sub_switch_hierarchy (self):

    list1 = []
    list2 = []
    
    for j in range(0, self.end_switch_index):
        if self.sub_switch_hierarchy.get(self.sub_switch_hierarchy_count) is None:
          self.sub_switch_hierarchy[self.sub_switch_hierarchy_count] = []
        if switch_switch_adjacency_matrix[self.end_switch_index][j] == 1:
          if j not in self.sub_switch_hierarchy[self.sub_switch_hierarchy_count]:  
            self.sub_switch_hierarchy[self.sub_switch_hierarchy_count].append(j)
            list1.append(j)

    self.sub_switch_hierarchy_count += 1
    
    for i in range(list1[-1], 0, -1):
      if i not in list1:
        continue
      else:
        for j in range(0, i):
          if self.sub_switch_hierarchy.get(self.sub_switch_hierarchy_count) is None:
            self.sub_switch_hierarchy[self.sub_switch_hierarchy_count] = []
          if switch_switch_adjacency_matrix[i][j] == 1:
            if j not in self.sub_switch_hierarchy[self.sub_switch_hierarchy_count]:  
              self.sub_switch_hierarchy[self.sub_switch_hierarchy_count].append(j)
              self.sub_switch_hierarchy[self.sub_switch_hierarchy_count].sort()
            if j not in list2:
              list2.append(j)
              list2.sort()
        if list1.index(i) == 0:
          self.sub_switch_hierarchy_count += 1
          list1 = list2
          list2 = []
    self.sub_switch_hierarchy_count -= 1
    '''for key, value in sub_switch_hierarchy.items():
        print key, value'''
    
   
  def _calc_shortest_path(self):

    self._calc_sub_switch_hierarchy ()
    infin = 999999
    total_min_cost_list = {}
    for i in range (1, self.sub_switch_hierarchy_count + 1):
        if i == 1:
          for j in self.sub_switch_hierarchy[i]:
            if total_min_cost_list.get(j) is None:
               total_min_cost_list[j] = [] 
            total_min_cost_list[j] = [link_weight[self.end_switch_index][j], self.end_switch_index]
        else:
          for j in self.sub_switch_hierarchy[i]:
              temp_cost = infin
              for k in self.sub_switch_hierarchy[i - 1]:
                 if switch_switch_adjacency_matrix[j][k] == 1:
                     if temp_cost > total_min_cost_list[k][0] + link_weight[k][j]:
                        temp_cost = total_min_cost_list[k][0] + link_weight[k][j] 
                        inter_switch = k
              if total_min_cost_list.get(j) is None:
                 total_min_cost_list[j] = [] 
              total_min_cost_list[j] = [temp_cost, inter_switch]
    print total_min_cost_list
    
    index = 0
    self.switches_on_path.append(switch_iter[index])    ############### assume gateway switch is "sw1" ####################
    for i in range (1, self.sub_switch_hierarchy_count):
       self.switches_on_path.append(switch_iter[total_min_cost_list[index][1]])
       index = total_min_cost_list[index][1]
    self.switches_on_path.append(self.end_switch)
    print self.switches_on_path   

      
  def init_path (self):
    init_link_weight()
    self._calc_shortest_path()


  def update_path (self):
    update_link_weight()     ####### might be called in another thread #######
    self._calc_shortest_path()

  def get_path (self):
    return self.switches_on_path
    

class load_balancing (object):
  
  def __init__ (self, connection):
    
    self.connection = connection

    # We want to hear PacketIn messages, so we listen
    # to the connection
    connection.addListeners(self)


  def _round_robin_calc_server (self, packet):
    if cluster == False:
      for i in range (1, total_server_num + 1):
        print q.balance[str(i)],
      global round_robin_current_server_num
      dst_server_num = round_robin_current_server_num
      round_robin_current_server_num += 1
      if round_robin_current_server_num == total_server_num + 1:
        round_robin_current_server_num = 1
      #print("dst_server_num is %i" % dst_server_num)
      #log.debug("dst_server_num is %i" % dst_server_num)
      return dst_server_num
    else:
      #print("mac is %s" % packet.src.toStr())
      global round_robin_current_servers_num
      last_digit = int(packet.src.toStr().split(':')[5], 16)                    ##### assigned to appropriate cluster   
      cluster_num = last_digit % total_cluster_num
      if cluster_num == 0:
          cluster_num = total_cluster_num
      #print("cluster_num is %i" % cluster_num)
      total_server_num_in_cluster = total_server_num / total_cluster_num
      #print("total_server_num_in_cluster is %i" % total_server_num_in_cluster)
      dst_server_num = round_robin_current_servers_num[cluster_num - 1] + (cluster_num - 1) * total_server_num_in_cluster
      round_robin_current_servers_num[cluster_num - 1] += 1
      if round_robin_current_servers_num[cluster_num - 1] == total_server_num_in_cluster + 1:
        round_robin_current_servers_num[cluster_num - 1] = 1
      #print("dst_server_num is %i" % dst_server_num)
      #log.debug("dst_server_num is %i" % dst_server_num)
      return dst_server_num


  def _random_calc_server (self, packet):
    if cluster == False:
      for i in range (1, total_server_num + 1):
        print q.balance[str(i)],
      dst_server_num = randint(1, total_server_num)
      #dst_server_num = math.floor(random() * total_server_num) + 1
      #print("dst_server_num is %i" % dst_server_num)
      #log.debug("dst_server_num is %i" % dst_server_num)
      return dst_server_num
    else:
      #print("mac is %s" % packet.src.toStr())
      last_digit = int(packet.src.toStr().split(':')[5], 16)                    ##### assigned to appropriate cluster   
      cluster_num = last_digit % total_cluster_num
      if cluster_num == 0:
          cluster_num = total_cluster_num
      total_server_num_in_cluster = total_server_num / total_cluster_num
      dst_server_num = randint(1, total_server_num_in_cluster) + (cluster_num - 1) * total_server_num_in_cluster
      #dst_server_num = math.floor(random() * total_server_num_in_cluster) + 1 + (cluster_num - 1) * total_server_num_in_cluster
      #print("dst_server_num is %i" % dst_server_num)
      #log.debug("dst_server_num is %i" % dst_server_num)
      return dst_server_num


  def _fix_calc_server (self, packet):
    if cluster == False:
      for i in range (1, total_server_num + 1):
        print q.balance[str(i)],
      client_num = self._get_client_num(packet.src)
      #print("client_num is %i" % client_num)
      dst_server_num = client_num % total_server_num
      if dst_server_num == 0:
          dst_server_num = total_server_num
      #print("dst_server_num is %i" % dst_server_num)
      #log.debug("dst_server_num is %i" % dst_server_num)
      return dst_server_num
    else:
      last_digit = int(packet.src.toStr().split(':')[5], 16)                    ##### assigned to appropriate cluster   
      cluster_num = last_digit % total_cluster_num
      if cluster_num == 0:
          cluster_num = total_cluster_num
      total_server_num_in_cluster = total_server_num / total_cluster_num
      total_client_num_in_cluster = total_client_num / total_cluster_num
      client_num = self._get_client_num(packet.src)
      #print("client_num is %i" % client_num)
      if cluster_num == total_cluster_num:
          client_num_in_cluster = client_num / (total_client_num / total_cluster_num)
      else:
          client_num_in_cluster = client_num / (total_client_num / total_cluster_num) + 1
      #print("client_num_in_cluster is %i" % client_num_in_cluster)
      temp = client_num_in_cluster % total_server_num_in_cluster
      if temp == 0:
         temp = total_server_num_in_cluster
      #print("temp is %i" % temp)
      dst_server_num = temp + (cluster_num - 1) * total_server_num_in_cluster
      #print("dst_server_num is %i" % dst_server_num)
      #log.debug("dst_server_num is %i" % dst_server_num)
      return dst_server_num

  def _load_calc_server (self, packet):
    min_load = 999999
    if cluster == False:
        dst_server_num = 1
        for i in range (1, total_server_num + 1):
            print q.balance[str(i)],
        for i in range (1, total_server_num + 1):
            temp = q.balance[str(i)]
            if min_load > temp:
                min_load = temp
                dst_server_num = i
        min_load_server_nums = []
        for i in range (1, total_server_num + 1):
            if min_load == q.balance[str(i)]:
                min_load_server_nums.append(i)
        if len(min_load_server_nums) > 1:
            dst_server_num = min_load_server_nums[randint(0, len(min_load_server_nums) - 1)]
        return dst_server_num  
    else:
        last_digit = int(packet.src.toStr().split(':')[5], 16)                    ############### needs to be modified ###############   
        cluster_num = last_digit % total_cluster_num
        if cluster_num == 0:
            cluster_num = total_cluster_num
        total_server_num_in_cluster = total_server_num / total_cluster_num
        dst_server_num = (cluster_num - 1) * total_server_num_in_cluster + 1
        for i in range (((cluster_num - 1) * total_server_num_in_cluster + 1), (cluster_num * total_server_num_in_cluster + 1)):
            temp = q.balance[str(i)]
            if min_load > temp:
                min_load = temp
                dst_server_num = i
        return dst_server_num
    
  def _two_random_calc_server(self, packet):
    if cluster == False:
        dst_server_num = 1
        for i in range (1, total_server_num + 1):
            print q.balance[str(i)],
        r1 = randint(1, total_server_num)
        r2 = randint(1, total_server_num)
        while r1 == r2:
            r2 = randint(1, total_server_num)
	if q.balance[str(r1)] < q.balance[str(r2)]:
            dst_server_num = r1
        else:
            dst_server_num = r2
        print("r1 is %i r2 is %i" % (r1, r2))
	return dst_server_num
    else:
        last_digit = int(packet.src.toStr().split(':')[5], 16)                    ############### needs to be modified ###############   
        cluster_num = last_digit % total_cluster_num
        if cluster_num == 0:
            cluster_num = total_cluster_num
        total_server_num_in_cluster = total_server_num / total_cluster_num
        dst_server_num = (cluster_num - 1) * total_server_num_in_cluster + 1
        return dst_server_num

  def _calc_server (self, packet):
    if round_robin:
        return self._round_robin_calc_server(packet)
    elif rand:
        return self._random_calc_server(packet)
    elif fixed:
        return self._fix_calc_server(packet)
    elif load:
        return self._load_calc_server(packet)
    else:
        return self._two_random_calc_server(packet)
     
  def _get_client_num (self, client_mac_addr):
    return (client_mac_addresses.index(client_mac_addr) + 1)

  def _handle_PacketIn (self, event):
    #log.debug("Connection packet in %s at switch %s" % (event.connection, dpid_to_str(event.dpid)))

    packet = event.parsed
    
      
    '''if isinstance(packet.next, ipv4):
        log.debug("%i %i IP %s => %s", event.dpid,event.port,
                  packet.next.srcip,packet.next.dstip)
        #log.debug("%i %i IP ", event.dpid, event.port)
    elif isinstance(packet.next, arp):
        log.debug("%i %i arp ", event.dpid, event.port)
    elif isinstance(packet.next, icmp):
        log.debug("%i %i icmp ", event.dpid,event.port)
    else:
        log.debug("%i %i not known protocol ", event.dpid, event.port)'''

    
    #packet is arp   
    if isinstance(packet.next, arp):
        '''log.debug("ARP!!!!!!!!!!!!!!!")
        log.debug("destination address is %s" % packet.dst)
        log.debug("source address is %s" % packet.src)
        log.debug("dest ip address %s" %packet.next.protodst)'''
        outport = 0
        switch = switch_dpid_name[dpid_to_str(event.dpid)]
        if packet.next.protodst == fake_ip_address:
            if packet.next.protosrc in client_ip_addresses:
                outport = total_client_num + 1
                if dpid_to_str(event.dpid) != "00-00-00-00-00-01":
                    print "wrong switch has arp src is client dst is fake!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            elif packet.next.protosrc in server_ip_addresses:
                server_num = server_ip_addresses.index(packet.next.protosrc) + 1
                switches = servers[server_num].get_path()
                switch = switch_dpid_name[dpid_to_str(event.dpid)]
                if switches.index(switch) == 0:
                  outport = total_client_num + 1
                else:
                  downlink_switch = switches[switches.index(switch) - 1]
                  outport = switch_switch_adjacency[downlink_switch][switch][2]
        elif packet.next.protodst in client_ip_addresses:
            if packet.next.protosrc in client_ip_addresses or packet.next.protosrc == fake_ip_address:
                client_num = client_ip_addresses.index(packet.next.protodst) + 1
                outport = switch_client_port[client_num]
                if dpid_to_str(event.dpid) != "00-00-00-00-00-01":
                    print "wrong switch has arp src is client dst is fake!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            elif packet.next.protosrc in server_ip_addresses:
                server_num = server_ip_addresses.index(packet.next.protosrc) + 1
                switches = servers[server_num].get_path()
                switch = switch_dpid_name[dpid_to_str(event.dpid)]
                if switches.index(switch) == 0:
                  client_num = client_ip_addresses.index(packet.next.protodst) + 1
                  outport = switch_client_port[client_num]
                else:
                  downlink_switch = switches[switches.index(switch) - 1]
                  outport = switch_switch_adjacency[downlink_switch][switch][2]                
        elif packet.next.protodst in server_ip_addresses:
             if packet.next.protosrc in client_ip_addresses or packet.next.protosrc == fake_ip_address:
                server_num = server_ip_addresses.index(packet.next.protodst) + 1
                switches = servers[server_num].get_path()
                switch = switch_dpid_name[dpid_to_str(event.dpid)]
                if switches.index(switch) < len(switches) - 1:
                  downlink_switch = switches[switches.index(switch) + 1]
                  outport = switch_switch_adjacency[switch][downlink_switch][1]
                else:
                  outport = switch_server_port[server_num][switch]
             '''elif packet.next.protosrc in server_ip_addresses:
                log.debug("wrong arp server -> server!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ")
                #src server -> sw1
                server_num = server_ip_addresses.index(packet.next.protosrc) + 1
                switches = servers[server_num].get_path()
                switch = switch_dpid_name[dpid_to_str(event.dpid)]
                
                downlink_switch = switches[switches.index(switch) - 1]
                outport1 = switch_switch_adjacency[downlink_switch][switch][2]
                if switches.index(switch) < len(switches) - 1:
                   uplink_switch = switches[switches.index(switch) + 1]
                   inport1 = switch_switch_adjacency[switch][uplink_switch][1]
                else:
                   inport1 = switch_server_port[server_num][switch]
                msg = of.ofp_packet_out()
                msg.data = event.ofp
                msg.match = of.ofp_match.from_packet(packet)
                msg.match.in_port = inport1
                msg.idle_timeout =  10
                #msg.in_port = event.port
                msg.actions.append(of.ofp_action_output(port = outport1))
                core.openflow.sendToDPID(str_to_dpid(switch_name_dpid[switch]), msg)
                log.debug("Installing arp at %s" % switch)
                
                #sw1 -> dst server
                server_num = server_ip_addresses.index(packet.next.protodst) + 1
                switches = servers[server_num].get_path()
                switch = switch_dpid_name[dpid_to_str(event.dpid)]
                if switches.index(switch) < len(switches) - 1:
                  downlink_switch = switches[switches.index(switch) + 1]
                  outport2 = switch_switch_adjacency[switch][downlink_switch][1]
                else:
                  outport2 = switch_server_port[server_num][switch]
                
                msg = of.ofp_packet_out()
                msg.data = event.ofp
                msg.match = of.ofp_match.from_packet(packet)
                msg.idle_timeout =  10
               #msg.in_port = event.port
                msg.actions.append(of.ofp_action_output(port = outport))
                event.connection.send(msg)'''

        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.match = of.ofp_match.from_packet(packet)
        msg.idle_timeout =  10
        #msg.in_port = event.port
        msg.actions.append(of.ofp_action_output(port = outport))
        core.openflow.sendToDPID(str_to_dpid(switch_name_dpid[switch]), msg)
        #log.debug("Installing arp at %s" % switch)


    #packet is normal ip
    elif isinstance(packet.next, ipv4):
      #log.debug("IP!!!!!!!!!")
      #print("packet.next.dstip is %s, pack.dst is %s" % (packet.next.dstip.toStr(), packet.dst.toStr()))
      #establish bi-direction flow tables on switches along the shortest path
      #client->server
      if packet.next.dstip == fake_ip_address:
        
        server_num = self._calc_server(packet)
        print "dst_server_num: " + str(server_num)
        global server_count
        server_count[server_num] += 1
        if load_balancing_path:
          servers[server_num].update_path()
        switches = servers[server_num].get_path()

        switch = switch_dpid_name[dpid_to_str(event.dpid)]
        if switches.index(switch) < len(switches) - 1:
          downlink_switch = switches[switches.index(switch) + 1]
          outport = switch_switch_adjacency[switch][downlink_switch][1]
        else:
          outport = switch_server_port[server_num][switch]

        new_dl_dst = servers[server_num].macAddr
        new_nw_dst = servers[server_num].ipAddr
        #print ("client->server")
        #rewrite at gateway
        
        #print ("i is %i, outport is %i, dst is %s, src is %s" % (switches.index(switch), outport, new_dl_dst.toStr(), packet.src.toStr()))
        msg = of.ofp_flow_mod()
        msg.data = event.ofp
        msg.match.dl_dst = packet.dst
        msg.match.dl_src = packet.src
        msg.match.dl_type = packet.type
        msg.idle_timeout =  1
        msg.actions.append(of.ofp_action_dl_addr.set_dst(new_dl_dst))
        msg.actions.append(of.ofp_action_nw_addr.set_dst(new_nw_dst))
        msg.actions.append(of.ofp_action_output(port = outport))
                
        core.openflow.sendToDPID(str_to_dpid(switch_name_dpid[switch]), msg)
        #log.debug("Installing at %s" % switch)

      elif packet.next.dstip in server_ip_addresses:
        server_num = server_ip_addresses.index(packet.next.dstip) + 1
        switches = servers[server_num].get_path()
        switch = switch_dpid_name[dpid_to_str(event.dpid)]
        if switches.index(switch) < len(switches) - 1:
          downlink_switch = switches[switches.index(switch) + 1]
          outport = switch_switch_adjacency[switch][downlink_switch][1]
        else:
          outport = switch_server_port[server_num][switch]
        new_dl_dst = servers[server_num].macAddr
        new_nw_dst = servers[server_num].ipAddr
        #print ("client->server")
        #print ("i is %i, outport is %i, dst is %s, src is %s" % (switches.index(switch), outport, new_dl_dst.toStr(), packet.src.toStr()))
        msg = of.ofp_flow_mod()
        msg.data = event.ofp
        msg.match.dl_dst = new_dl_dst
        msg.match.dl_src = packet.src
        msg.match.dl_type = packet.type
        msg.idle_timeout =  1
        msg.actions.append(of.ofp_action_output(port = outport))
        
        core.openflow.sendToDPID(str_to_dpid(switch_name_dpid[switch]), msg)
        #log.debug("Installing at %s" % switch)
        
      #server->client
      elif packet.next.srcip in server_ip_addresses:
      
        #print ("server->client")
        server_num = server_ip_addresses.index(packet.next.srcip) + 1
        switches = servers[server_num].get_path()
        switch = switch_dpid_name[dpid_to_str(event.dpid)]
        if switches.index(switch) == 0:
          client_num = self._get_client_num(packet.dst)
          outport = switch_client_port[client_num]
        else:
          downlink_switch = switches[switches.index(switch) - 1]
          outport = switch_switch_adjacency[downlink_switch][switch][2]
        #print ("i is %i, outport is %i, dst is %s, src is %s" % (switches.index(switch), outport, packet.dst, packet.src))
        msg = of.ofp_flow_mod()
        msg.data = event.ofp
        msg.match.dl_dst = packet.dst
        msg.match.dl_src = packet.src
        msg.match.dl_type = packet.type
        msg.idle_timeout =  1
        #rewrite at gateway
        if switches.index(switch) == 0:
          new_dl_src = fake_mac_address
          new_nw_src = fake_ip_address
          msg.actions.append(of.ofp_action_dl_addr.set_src(new_dl_src))
          msg.actions.append(of.ofp_action_nw_addr.set_src(new_nw_src))
        msg.actions.append(of.ofp_action_output(port = outport))
        
        core.openflow.sendToDPID(str_to_dpid(switch_name_dpid[switch]), msg)
        #log.debug("Installing at %s" % switch)

                              
      #drop other packets                                                 ############## if there are other useful packets this might be wrong
      '''else:
        if event.ofp.buffer_id is not None:
          msg = of.ofp_packet_out()
          msg.buffer_id = event.ofp.buffer_id
          msg.in_port = event.port
          self.connection.send(msg)
          log.debug("Drop packets at switch %s" % dpid_to_str(event.dpid))'''

class Multi_switches_load_balancing (object):
  """
  Waits for OpenFlow switches to connect and learns dpid.
  """
  def __init__ (self):
    core.openflow.addListeners(self)
    
    calc_switch_hierarchy()
    
    for i in range (0, total_server_num):
      server = Server(i + 1, server_mac_addresses[i], server_ip_addresses[i])
      servers[i + 1] = server
      server.init_path()


  def _handle_ConnectionUp (self, event):
    log.debug("Connection %s" % (event.connection,))
    log.debug("switch dpid %s" % dpid_to_str(event.dpid))
    global connection_up_count
    connection_up_count += 1
    if connection_up_count == total_switch_num:
        global q
        q = LoadQuery2.LoadQuery2()
        q.listen()
        log.debug("q.listen")
        connection_up_count = 0
  
    load_balancing(event.connection)


  def _handle_ConnectionDown (self, event):
    log.debug("Connection down %s" % (event.connection,))
    log.debug("switch dpid %s" % dpid_to_str(event.dpid))
    global connection_down_count
    connection_down_count += 1
    if connection_down_count == total_switch_num:
        for i in range (1, total_server_num + 1):
            print "server: " + str(i) + " count: " + str(server_count[i])
        global q
        q.stop()
        log.debug("q.stop")
        connection_down_count = 0
    


def launch ():

  core.registerNew(Multi_switches_load_balancing)



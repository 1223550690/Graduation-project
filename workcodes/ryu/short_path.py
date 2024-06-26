from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.topology.api import get_switch, get_link
from ryu.topology import event
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import arp, ipv4, tcp
from ryu.lib.packet import ether_types
import time

import matplotlib.pyplot as plt
 
import networkx as nx
 
 
class PathForward(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
 
    def __init__(self, *args, **kwargs):
        super(PathForward, self).__init__(*args, **kwargs)
        self.G = nx.DiGraph()
        self.topology_api_app = self
        self.arp_table = {}
        self.arp_hold_time = 0.01
        
    def grah_plot(self):
        nx.draw(self.G, with_labels=True)
        plt.savefig('network_graph.png')
        plt.clf()

    def add_flow(self, datapath, priority, match, actions):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        command = ofp.OFPFC_ADD
        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        req = ofp_parser.OFPFlowMod(datapath=datapath, command=command,
                                    priority=priority, match=match, instructions=inst)
        datapath.send_msg(req)
 

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
 
        # add table-miss
        match = ofp_parser.OFPMatch()
        actions = [ofp_parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)]
        self.add_flow(datapath=datapath, priority=0, match=match, actions=actions)
 
 
    @set_ev_cls(event.EventSwitchEnter)
    def get_topo(self, ev):
        switch_list = get_switch(self.topology_api_app)
        switches = []

        for switch in switch_list:
            switches.append(switch.dp.id)
        self.G.add_nodes_from(switches)
 
        link_list = get_link(self.topology_api_app)
        links = []

        for link in link_list:
            links.append((link.src.dpid, link.dst.dpid, {'attr_dict': {'port': link.src.port_no}}))
        self.G.add_edges_from(links)
 
        for link in link_list:
            links.append((link.dst.dpid, link.src.dpid, {'attr_dict': {'port': link.dst.port_no}}))
        self.G.add_edges_from(links)
        self.grah_plot()
 
 
 
    def get_out_port(self, datapath, src, dst, in_port):
        dpid = datapath.id
 
        if src not in self.G:
            print("src:{}".format(src))
            self.G.add_node(src)
            self.G.add_edge(dpid, src, attr_dict={'port': in_port})
            self.G.add_edge(src, dpid)
            self.grah_plot()
        if dst in self.G:
            print("dst:{}".format(dst))
            path = nx.shortest_path(self.G, src, dst)
            next_hop = path[path.index(dpid) + 1]
            out_port = self.G[dpid][next_hop]['attr_dict']['port']
            print(path)
            """
            with open('pkt_data.txt', 'a') as outfile: 
                outfile.write("{------------------}\n")
            """
        else:
            out_port = datapath.ofproto.OFPP_FLOOD
        return out_port
 
 
 
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
 
        dpid = datapath.id
        in_port = msg.match['in_port']
 
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        arp_pkt = pkt.get_protocols(arp.arp)
        
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return
        
	if arp_pkt:
            arp_pkt = arp_pkt[0]
            arp_src_ip = arp_pkt.src_ip
            arp_dst_ip = arp_pkt.dst_ip
            arp_src_mac = eth.src
            
            arp_request_key = (dpid, arp_src_ip, arp_dst_ip, arp_src_mac)

            current_time = time.time()
            
            if arp_pkt.opcode == arp.ARP_REQUEST:
                if arp_request_key in self.arp_table:
                    old_time = self.arp_table[arp_request_key]
                    if current_time - old_time < self.arp_hold_time:
                        return
                self.arp_table[arp_request_key] = current_time


        """ 


        elif eth:
            print("its an eth")
        elif pkt.get_protocols(ipv4.ipv4):
            print("its a ipv4")
        elif pkt.get_protocols(tcp.tcp):
            print("its a tcp")
        else:
            print("its other packet")
        """   
 
        dst = eth.dst
        src = eth.src
  
        if dst == ('33:33:00:00:00:fb') or dst == ('33:33:00:00:00:02') or dst == ('01:80:c2:00:00:0e'):
            return

        if dst in self.G:
            with open('pkt_data.txt', 'a') as outfile: 
                outfile.write("{}\n".format(pkt.protocols))
        
 
        out_port = self.get_out_port(datapath, src, dst, in_port)
        
        actions = [ofp_parser.OFPActionOutput(out_port)]
 
        if out_port != ofp.OFPP_FLOOD:
            match = ofp_parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            self.add_flow(datapath=datapath, priority=1, match=match, actions=actions)
            print("out_port:{}\n".format(out_port))

 
        data = None
        if msg.buffer_id == ofp.OFP_NO_BUFFER:
            data = msg.data

        out = ofp_parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                      in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

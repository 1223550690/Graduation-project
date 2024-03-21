from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet

import matplotlib.pyplot as plt
import threading
import json
 
import networkx as nx
 
 
class PathForward(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
 
    def __init__(self, *args, **kwargs):
        super(PathForward, self).__init__(*args, **kwargs)
        self.G = nx.DiGraph()
        self.topology_api_app = self
        
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

        switch_list = get_switch(self.topology_api_app, None)  
        switches=[switch.dp.id for switch in switch_list]
        self.G.add_nodes_from(switches)  
	
	for switch in switch_list:
            for port in switch.ports:
                self.G.add_node(port.hw_addr, portID = port.port_no)
                self.G.add_edge(port.hw_addr, switch.dp.id)
                self.G.add_edge(switch.dp.id, port.hw_addr)

        link_list = get_link(self.topology_api_app, None) 
	
        for link in link_list:
            self.G.add_node(link.src.hw_addr, portID = link.src.port_no )
            self.G.add_edge(link.src.hw_addr, link.dst.hw_addr)
	
	"""
        links = [(link.src.hw_addr, link.dst.hw_addr) for link in link_list] 
        self.G.add_edges_from(links)
        
        link = [(link.src.dpid, link.src.hw_addr) for link in link_list] 
        self.G.add_edges_from(link) 
        
        
        links = [(link.dst.hw_addr, link.src.hw_addr) for link in link_list] 
        self.G.add_edges_from(links)
        
        link = [(link.src.hw_addr, link.src.dpid) for link in link_list] 
        self.G.add_edges_from(link) 
        """
 
 

        self.grah_plot()
        
        with open('switches_data.txt', 'w') as outfile:
            outfile.write("{}\n".format(switches))
        """    
        with open('links_data.txt', 'w') as outfile:
            outfile.write("{}\n".format(links))
            
        with open('link_data.txt', 'w') as outfile:
            outfile.write("{}\n".format(link))
         """ 

 	
    def get_out_port(self, datapath, src, dst, in_port):
        dpid = datapath.id
        print("src:{}".format(src)) 
        print("dst:{}".format(dst)) 
        print("innnn:{}".format(in_port)) 
        
        port_addr = None
        for port in datapath.ports.values():
            if port.port_no == in_port:
            	  port_addr = port.hw_addr
        
        #new host
        """
        for node, data in self.G.nodes(data=True):
            if data.get('portID') == src:
                break
        else:
        """
        if src not in self.G:  
            self.G.add_node(src, portID = "host")
            self.G.add_edge(port_addr, src)
            self.G.add_edge(src, port_addr)
            self.grah_plot()
            
            
        """    
        if src not in self.G:        
            self.G.add_node(src)
            self.G.add_edge(dpid, src, attr_dict={'port': in_port})
            self.G.add_edge(src, dpid)
            self.grah_plot()
        """
            
        if dst in self.G:
            print("dafawfawfawfawfawfwafawfawfwa") 
            path = nx.shortest_path(self.G, port_addr, dst) 
            next_hop = path[path.index(dpid) + 2]  
            out_port = in_port
            """
            out_port = self.G[dpid][next_hop]['attr_dict']['port'] 
            
            """
            print("path:{}".format(path)) 

        else:
            out_port = datapath.ofproto.OFPP_FLOOD 
            print("FLOOD") 
        return out_port
        
        
 
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        
        
        msg_data = vars(ev.msg) 

        with open('event_data.txt', 'w') as file:
            for key, value in msg_data.items():
                file.write("{}: {}\n".format(key, value))
                
        datapath = msg.datapath
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
 
        dpid = datapath.id
        in_port = msg.match['in_port']
 
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
 
        dst = eth.dst
        src = eth.src
        
        print("-------------------")
        out_port = self.get_out_port(datapath, src, dst, in_port)  
        actions = [ofp_parser.OFPActionOutput(out_port)]
        print("datapath:{}".format(dpid))
        print("outputport:{}".format(out_port))

 

        if out_port != ofp.OFPP_FLOOD:
            match = ofp_parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            self.add_flow(datapath=datapath, priority=1, match=match, actions=actions)
 
        data = None
        
        if msg.buffer_id == ofp.OFP_NO_BUFFER:
            data = msg.data

        out = ofp_parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                      in_port=in_port, actions=actions, data=data)
                                                                
        datapath.send_msg(out)

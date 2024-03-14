from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.topology.api import get_switch, get_link
from ryu.topology import event
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
 
import networkx as nx
 
 
class PathForward(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
 
    def __init__(self, *args, **kwargs):
        super(PathForward, self).__init__(*args, **kwargs)
        self.G = nx.DiGraph()

        self.topology_api_app = self
 
    #添加流表
    def add_flow(self, datapath, priority, match, actions):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        command = ofp.OFPFC_ADD
        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        req = ofp_parser.OFPFlowMod(datapath=datapath, command=command,
                                    priority=priority, match=match, instructions=inst)
        datapath.send_msg(req)
 
    #设置新交换机
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
 
    #更新SDN网络的拓扑视图
    @set_ev_cls(event.EventSwitchEnter)  #新交换机加入网络时触发
    def get_topo(self, ev):
        switch_list = get_switch(self.topology_api_app)  #获取当前网络中所有交换机的列表
        switches = []  #存储交换机的标识

        for switch in switch_list:
            switches.append(switch.dp.id)  

        self.G.add_nodes_from(switches)  #将交换机列表加入到图G节点中
 
        link_list = get_link(self.topology_api_app)  #获取当前网络中所有活动链接的列表
        links = []  #存储链接信息

        for link in link_list:
            links.append((link.src.dpid, link.dst.dpid, {'attr_dict': {'port': link.src.port_no}}))   

        self.G.add_edges_from(links)  #将网络链接作为边加入到图G中
 
        for link in link_list:
            links.append((link.dst.dpid, link.src.dpid, {'attr_dict': {'port': link.dst.port_no}}))

        self.G.add_edges_from(links)  #添加反向链接
 
    def get_out_port(self, datapath, src, dst, in_port):
        dpid = datapath.id
 
        if src not in self.G:        #如果拓扑图G中没有源MAC地址作为节点，则将它添加到图中，并且向图添加两条边，一条从交换机dpid到源MAC src，一条相反方向。边上带有属性字典attr_dict，其中记录了相应的端口号
            self.G.add_node(src)
            self.G.add_edge(dpid, src, attr_dict={'port': in_port})
            self.G.add_edge(src, dpid)
 
        if dst in self.G:
            path = nx.shortest_path(self.G, src, dst)   #查找从源到目的的最短路径
            next_hop = path[path.index(dpid) + 1]  #从查找到的路径中提取出在当前交换机dpid之后的下一个跳的节点
            out_port = self.G[dpid][next_hop]['attr_dict']['port']  #查询图中从当前交换机dpid到下一个跳next_hop对应的端口号，并将其设置为输出端口
            print(path)
        else:
            out_port = datapath.ofproto.OFPP_FLOOD  #泛洪
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
 
        dst = eth.dst
        src = eth.src
 
        out_port = self.get_out_port(datapath, src, dst, in_port)  #决定数据包的输出端口
        actions = [ofp_parser.OFPActionOutput(out_port)]
 

        if out_port != ofp.OFPP_FLOOD:
            match = ofp_parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            self.add_flow(datapath=datapath, priority=1, match=match, actions=actions)
 
        data = None
        
        if msg.buffer_id == ofp.OFP_NO_BUFFER:
            data = msg.data

        out = ofp_parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                      in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

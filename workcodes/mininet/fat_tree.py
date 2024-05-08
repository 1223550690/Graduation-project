from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.link import TCLink

class FatTreeTopo(Topo):
    "Simple 4-ary fat-tree topology"

    def build(self, k=4):
        self.port = 1  # Start with port 1 for global increment

        # Constructor for MAC address based on layer, switch id, and port
        def mac(layer, sw_id, port):
            return "00:00:00:0%d:%02d:%02d" % (layer, sw_id, port)

            
        # Create core switches
        core_switches = [self.addSwitch('c{}'.format(i+1)) for i in range((k//2)**2)]

        # Create pod switches and hosts
        for pod_id in range(k):
            pod_agg_switches = [self.addSwitch('a%d%d' % (pod_id + 1, i + 1)) for i in range(k // 2)]
            pod_edge_switches = [self.addSwitch('e%d%d' % (pod_id + 1, i + 1)) for i in range(k // 2)]

            # Add links between aggregation and edge switches
            for agg_id, agg_sw in enumerate(pod_agg_switches):
                for edge_id, edge_sw in enumerate(pod_edge_switches):
                    self.addLink(
                        agg_sw, edge_sw,
                        port1=self.port,
                        port2=self.port + 1,
                        addr1=mac(2, pod_id * k//2 + agg_id + 1, self.port),
                        addr2=mac(3, pod_id * k//2 + edge_id + 1, self.port + 1),
                    )
                    self.port += 2

            # Create and link hosts to edge switches
            host_id = pod_id * (k//2) * (k//2)
            for edge_id, edge_sw in enumerate(pod_edge_switches):
                for i in range(k // 2):
                    host = self.addHost('h%d' % (host_id + 1))
                    self.addLink(edge_sw, host, port1=self.port, addr1=mac(3, pod_id * k//2 + edge_id + 1, self.port))
                    host_id += 1
                    self.port += 1

        # Interconnect core and aggregation switches
        for core_id in range((k//2)**2):
            for pod_id in range(k):
                core_sw = core_switches[core_id]
                agg_sw = self.switches()[core_id // (k//2) + (pod_id * (k//2))]
                self.addLink(
                    core_sw, agg_sw,
                    port1=self.port,
                    port2=self.port + 1,
                    addr1=mac(1, core_id + 1, self.port),
                    addr2=mac(2, pod_id * k//2 + core_id // (k//2) + 1, self.port + 1),
                )
                self.port += 2

def test():
    "Trt to create and test a simple fat tree network(k=4)"
    topo = FatTreeTopo(k=4)
    net = Mininet(topo, controller=RemoteController, link=TCLink, switch=OVSKernelSwitch)
    
    info('*** Starting network\n')
    net.start()
    
    """
    print("Dumping host connections")
    dumpNodeConnections(net.hosts)
    """
    
    info('*** Running CLI\n')
    CLI(net)
    
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    test()

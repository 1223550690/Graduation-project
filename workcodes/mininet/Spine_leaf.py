from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

def Spine_leaf():
    net = Mininet(controller=RemoteController, link=TCLink, switch=OVSSwitch)

    # 添加一个默认的控制器
    info('*** Adding controller\n')
    net.addController('c0')

    # 添加两个交换机
    info('*** Adding switches\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    s4 = net.addSwitch('s4')
    s5 = net.addSwitch('s5')

    # 添加两个客户端
    info('*** Adding hosts\n')
    h1 = net.addHost('h1', ip = '192.168.1.1')
    h2 = net.addHost('h2', ip = '192.168.1.2')
    h3 = net.addHost('h3', ip = '192.168.1.3')


    # 创建链路: 客户端到交换机
    info('*** Creating links\n')
    net.addLink(s1, s3, port1=1, port2=7, addr1='00:00:00:00:01:01', addr2='00:00:00:00:03:07')
    net.addLink(s1, s4, port1=2, port2=9, addr1='00:00:00:00:01:02', addr2='00:00:00:00:04:09')
    net.addLink(s1, s5, port1=3, port2=11, addr1='00:00:00:00:01:03', addr2='00:00:00:00:05:11')
    
    net.addLink(s2, s3, port1=4, port2=8, addr1='00:00:00:00:02:04', addr2='00:00:00:00:03:08')
    net.addLink(s2, s4, port1=5, port2=10, addr1='00:00:00:00:02:05', addr2='00:00:00:00:04:10')
    net.addLink(s2, s5, port1=6, port2=12, addr1='00:00:00:00:02:06', addr2='00:00:00:00:05:12')
    

    # 主机到交换机

    net.addLink(s3, h1, port1=13, port2=16, addr1='00:00:00:00:03:13', addr2='00:00:00:00:00:16')
    net.addLink(s4, h2, port1=14, port2=17, addr1='00:00:00:00:04:14', addr2='00:00:00:00:00:17')
    net.addLink(s5, h3, port1=15, port2=18, addr1='00:00:00:00:05:15', addr2='00:00:00:00:00:18')
    


    # 启动网络
    info('*** Starting network\n')
    net.start()

    # 运行CLI
    info('*** Running CLI\n')
    CLI(net)

    # 停止网络
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    Spine_leaf()

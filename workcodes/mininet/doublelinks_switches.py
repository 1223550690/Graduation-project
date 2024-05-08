from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

def double_switches():
    net = Mininet(controller=RemoteController, link=TCLink, switch=OVSKernelSwitch)

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
    h2 = net.addHost('h2', ip = '192.168.2.1')


    # 创建链路: 客户端到交换机
    info('*** Creating links\n')
    net.addLink(h1, s1, port1=1, port2=2, addr1='00:00:00:00:00:01', addr2='00:00:00:00:01:02')
    net.addLink(s1, s2, port1=3, port2=5, addr1='00:00:00:00:01:03', addr2='00:00:00:00:02:05')
    net.addLink(s2, s3, port1=6, port2=7, addr1='00:00:00:00:02:06', addr2='00:00:00:00:03:07')
    net.addLink(s3, s5, port1=8, port2=9, addr1='00:00:00:00:03:08', addr2='00:00:00:00:05:09')
    net.addLink(s5, h2, port1=11, port2=12, addr1='00:00:00:00:05:11', addr2='00:00:00:00:00:12')
    # 主机到交换机

    net.addLink(s1, s4, port1=4, port2=13, addr1='00:00:00:00:01:04', addr2='00:00:00:00:04:13')
    net.addLink(s4, s5, port1=14, port2=10, addr1='00:00:00:00:04:14', addr2='00:00:00:00:05:10')

    


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
    double_switches()

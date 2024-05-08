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

    # 添加两个客户端
    info('*** Adding hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')

    # 添加一个主机
    h3 = net.addHost('h3', ip='10.0.0.3')

    # 创建链路: 客户端到交换机
    info('*** Creating links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s2)

    # 主机到交换机
    net.addLink(h3, s2)
    net.addLink(h3, s1)
    
    # 交换机 s1 到交换机 s2
    net.addLink(s1, s2)

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

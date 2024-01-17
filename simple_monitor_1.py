from operator import attrgetter

from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub

import plotly.graph_objects as go
import plotly.offline as pyo
import pandas as pd
import datetime
import os

class SimpleMonitor13(simple_switch_13.SimpleSwitch13):

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)

        self.mylist = []
        self.list = []
 
        self.csv_file = 'data.csv'
        if os.path.isfile(self.csv_file):
        	open(self.csv_file, 'w').close()
            	self.df = pd.DataFrame(columns=['Index', 'datapath','port',
				'rx-pkts','rx-bytes',
				'rx-error', 'tx-pkts',
				'tx-bytes', 'tx-error','time'])
		self.df.to_csv(self.csv_file, index=False)


    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(10)

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         '
                         'in-port  eth-dst           '
                         'out-port packets  bytes')
        self.logger.info('---------------- '
                         '-------- ----------------- '
                         '-------- -------- --------')
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['eth_dst'])):
            self.logger.info('%016x %8x %17s %8x %8d %8d',
                             ev.msg.datapath.id,
                             stat.match['in_port'], stat.match['eth_dst'],
                             stat.instructions[0].actions[0].port,
                             stat.packet_count, stat.byte_count)

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error')
        self.logger.info('---------------- -------- '
                         '-------- -------- -------- '
                         '-------- -------- --------')
        for stat in sorted(body, key=attrgetter('port_no')):
            self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',
                             ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors)
            if stat.port_no == 1:
            	self.mylist.append(stat.rx_bytes)
            	self.list = [ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors]

            	self.df = pd.read_csv(self.csv_file)	

            	last_index = self.df['Index'].max() if not self.df.empty else 0
            	current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            	new_data = {'Index': last_index + 1, 'datapath': ev.msg.datapath.id, 'port': stat.port_no,
            			'rx-pkts': stat.rx_packets, 'rx-bytes': stat.rx_bytes, 'rx-error': stat.rx_errors,
            			'tx-pkts': stat.tx_packets, 'tx-bytes': stat.tx_bytes, 'tx-error': stat.tx_errors, 'time': current_time}
            	self.df = self.df.append(new_data, ignore_index=True)
            	self.df.to_csv(self.csv_file, index=False)
            	
#        trace = go.Scatter(x=list(range(len(self.mylist))), y=self.mylist)
#        layout = go.Layout(title='r_bypes', xaxis=dict(title='Xaxis'), yaxis=dict(title='Yaxis'))
#        fig = go.Figure(data=[trace], layout=layout)
#        pyo.plot(fig, filename='line_chart.html', auto_open=True)


            	table = go.Table(
            		header=dict(values=list(self.df.columns)),
            		cells=dict(values=[self.df[col] for col in self.df.columns])
            		)
            		
            	line_chart = go.Scatter(
            		x=self.df['time'],
            		y=self.df['rx-bytes'],
            		mode='lines',
            		name='rx-bytes'
            		)
            	fig1 = go.Figure(data=[table])
            	fig2 = go.Figure(data=[line_chart])
            	pyo.plot(fig1, filename='table.html', auto_open=False)
            	pyo.plot(fig2, filename='line_chart.html', auto_open=False)

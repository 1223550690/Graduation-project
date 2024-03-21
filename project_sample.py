import dash
from dash import Dash, html, dcc
from dash import dash_table
import requests
from dash.dependencies import Input, Output,State
import pandas as pd
import plotly.graph_objs as go
from dash.exceptions import PreventUpdate
import json
from pathlib import Path

app = Dash(__name__)


app.layout = html.Div([
    html.H1("交换机信息实时展示"),
    #组件：计时器
    dcc.Interval(
        id='interval-component',
        interval=1*1000, 
        n_intervals=0
    ),
    dcc.Dropdown(id='switches-dropdown'),  #组件：下拉菜单
    
    html.Div([
        dash_table.DataTable(
            id='flow-table',
            columns = [
    		{'name': 'actions', 'id': 'actions'}, 

    		{'name': 'match.in_port', 'id': 'match.in_port'},  
    
    		{'name': 'packet_count', 'id': 'packet_count'},
	    	{'name': 'byte_count', 'id': 'byte_count'},
	    	{'name': 'idle_timeout', 'id': 'idle_timeout'},
	    	{'name': 'hard_timeout', 'id': 'hard_timeout'},
	    	{'name': 'duration_sec', 'id': 'duration_sec'},
	    	{'name': 'duration_nsec', 'id': 'duration_nsec'},
	    	{'name': 'priority', 'id': 'priority'},
	    	{'name': 'table_id', 'id': 'table_id'},
	    	{'name': 'flags', 'id': 'flags'}
            ],
            
            data=[],  # 初始数据为空
            row_selectable='single',  # 允许单行选择
            style_table={'height': '200px', 'overflowY': 'auto', 'display': 'none'}
        )
    ]),
    
        html.Div([
        dash_table.DataTable(
            id='port-table',
            columns = [
    		{'name': 'hw_addr', 'id': 'hw_addr'}, 

    		{'name': 'curr', 'id': 'curr'},  
    
    		{'name': 'supported', 'id': 'supported'},
	    	{'name': 'max_speed', 'id': 'max_speed'},
	    	{'name': 'advertised', 'id': 'advertised'},
	    	{'name': 'peer', 'id': 'peer'},
	    	{'name': 'port_no', 'id': 'port_no'},
	    	{'name': 'curr_speed', 'id': 'curr_speed'},
	    	{'name': 'name', 'id': 'name'},
	    	{'name': 'state', 'id': 'state'},
	    	{'name': 'config', 'id': 'config'}
            ],
            
            data=[],  # 初始数据为空
            style_table={'height': '200px', 'overflowY': 'auto', 'display': 'none'}
        )
    ]),

    # 当选中某行时用于显示信息的 Div
    html.Div(id='flow-details'),
    
    
    html.Div(id='switches-info'),  #组件：交换机信息
    html.Div(id='flows-info'),     #组件：流量信息
    dcc.Graph(id='rx-packets-time-series')  #组件：流量图(接收流量)

])


#函数：更新交换机下拉列表
@app.callback(Output('switches-dropdown', 'options'),      #输出：下拉菜单的options
              [Input('interval-component', 'n_intervals')])   #输入：计时器组件的n_intervals
def update_switches_list(n_intervals):
    url = 'http://localhost:8080/stats/switches'  # Ryu 控制器获取交换机列表的API
    try:
        response = requests.get(url)
        switches_list = response.json()
        # 创建一个用于Dropdown的选项列表，每个选项是一个字典
        options = [{'label': f"交换机 {s}", 'value': s} for s in switches_list]
    except requests.exceptions.RequestException:
        options = []
    return options
    
    
@app.callback([Output('flow-table', 'data'),
              Output('flow-table', 'style_table')],
              [Input('switches-dropdown', 'value')])
def update_table(selected_switch):
    if selected_switch is None:
        return ([],{'display': 'none'})

    url = f'http://localhost:8080/stats/flow/{selected_switch}'
    try:
        response = requests.get(url)  # 可能需要使用GET请求获取数据
        flow_info = response.json()
        
        for entry in flow_info[str(selected_switch)]:
            entry['actions'] = ', '.join(entry['actions'])
        for entry in flow_info.get(str(selected_switch), []):
            entry['match'] = str(entry['match'])
	    
        flows = flow_info[str(selected_switch)]
        
        return [flows, {'display': 'block'}]
        
    except requests.exceptions.RequestException as e:
        print(e)
        return ([],{'display': 'none'})  # 请求失败时返回空数据



@app.callback([Output('port-table', 'data'),
              Output('port-table', 'style_table')],
              [Input('switches-dropdown', 'value')])
def update_table(selected_switch):
    if selected_switch is None:
        return ([],{'display': 'none'})

    url = f'http://localhost:8080/stats/portdesc/{selected_switch}'
    try:
        response = requests.get(url)  # 可能需要使用GET请求获取数据
        port_info = response.json()
        
        for entry in port_info[str(selected_switch)]:
            entry['hw_addr'] = str(entry['hw_addr'])
            entry['name'] = str(entry['name'])
            
        ports = port_info[str(selected_switch)]
        return [ports, {'display': 'block'}]
        
    except requests.exceptions.RequestException as e:
        print(e)
        return ([],{'display': 'none'})  # 请求失败时返回空数据







@app.callback(
    Output('flow-details', 'children'),
    [Input('flow-table', 'selected_rows')],
    [State('flow-table', 'data')])
def display_flow_details(selected_rows, rows):
    if selected_rows is None or len(selected_rows) == 0:
        # 未选择任何行时不展示任何内容或展示提示信息
        return "请选择一个流表项以查看详情。"
    else:
        # 取得选中的第一行
        selected_row = rows[selected_rows[0]]
        # 解析流表信息，并返回格式化的中文解释
        details = parse_flow_table_row(selected_row)
        preformatted_text = html.Pre(details, style={'white-space': 'pre-wrap'})
        return preformatted_text

def parse_flow_table_row(row):
    chinese_explanation = f"""
    - 动作: {row['actions']}\n
    - 闲置超时: {row['idle_timeout']} 秒\n
    - 硬超时: {row['hard_timeout']} 秒\n
    - 数据包计数: {row['packet_count']}\n
    - 字节计数: {row['byte_count']}\n
    - 持续时间: {row['duration_sec']} 秒 {row['duration_nsec']} 纳秒\n
    - 优先级: {row['priority']}\n
    - 匹配条件: {json.dumps(row['match'], ensure_ascii=False)}\n
    """
    return chinese_explanation

'''
#函数：更新特定交换机信息
@app.callback(Output('switches-info', 'children'),
              [Input('switches-dropdown', 'value')])
def update_switch_info(selected_switch):
    if selected_switch is None:
        return html.Div()

    # 根据选择的交换机获取特定的交换机信息
    url = f'http://localhost:8080/stats/flow/{selected_switch}'
    try:
        response = requests.post(url, data={})
        flow_info = response.json()
        # 假设数据格式是一个字典，键为交换机，值为流表信息
        flows = pd.DataFrame(flow_info[str(selected_switch)])
        # 将数据转换为HTML表格
        children = html.Div([
            html.H2(f"交换机 {selected_switch} 流表"),
            dcc.Markdown(flows.to_markdown(index=False))
        ])
    except requests.exceptions.RequestException:
        children = html.Div(f"获取交换机 {selected_switch} 的数据失败。")

    return children

'''
#函数：数据包信息更新
@app.callback(Output('rx-packets-time-series', 'figure'),   #输出：流量图组件的figure
              [Input('interval-component', 'n_intervals')]) #输入：计时器组件的n_intervals

def update_rx_packets_time_series(n):
    csv_file_path = 'data.csv'
    

    if not Path(csv_file_path).is_file() or Path(csv_file_path).stat().st_size == 0:

        return {
            'data': [],
            'layout': go.Layout(
                title='无法打开 data.csv 文件或文件无内容'
            )
        }
    

    df = pd.read_csv(csv_file_path)
  
    if df.empty:
        return {
            'data': [],
            'layout': go.Layout(
                title='无法打开 data.csv 文件或文件无内容'
            )
        }
    
    
    df['time'] = pd.to_datetime(df['time']).dt.strftime('%H:%M:%S')

    df.loc[df['datapath'] == 1, 'rx_rate'] = df.loc[df['datapath'] == 1, 'rx-bytes'].diff()

    trace = go.Scatter(
        x=df['time'],
        y=df['rx_rate']*8,
        mode='lines+markers',
        name='接收包速率'
    )

    layout = go.Layout(
        title='datapath1 接收包速率随时间变化',
        xaxis=dict(title='时间'),
        yaxis=dict(title='速率 (bytes/s)')
    )
    
    return {'data': [trace], 'layout': layout}

'''
#函数：交换机状态更新
@app.callback(Output('switches-info', 'children'),          #输出：交换机信息组件的children
              [Input('interval-component', 'n_intervals')]) #输入：计时器组件的n_intervals
def update_switches_info(n):
    # Ryu REST API endpoint
    url = 'http://localhost:8080/stats/switches'

    try:
        response = requests.get(url)  #响应信息
        switches = response.json()    #json信息
    except requests.exceptions.RequestException as e:
        return html.Div([
            html.P("无法从Ryu获取交换机信息。"),
            html.P(str(e))
        ])

    switches_pd = pd.DataFrame(switches, columns=['Switch ID'])
    return html.Div([
        html.H3('交换机列表'),
        dcc.Markdown(switches_pd.to_markdown(index=False)) 
    ])
'''

#函数：流量状态更新
@app.callback(Output('flows-info', 'children'),              #输出：流量信息组件的children
              [Input('interval-component', 'n_intervals')])  #输入：计时器组件的n_intervals
def update_flows_info(n):
    # Ryu REST API endpoint
    url = 'http://localhost:8080/stats/flow/1'
    try:
        response = requests.post(url, data={})
        flows = response.json()[str(1)] 
    except requests.exceptions.RequestException as e:
        return html.Div([
            html.P("无法从Ryu获取流表信息。"),
            html.P(str(e))
        ])
    if not flows:
        return html.Div("当前没有流量信息")
    
    flows_table = html.Table([
        html.Thead(
            html.Tr([html.Th('Action'), html.Th('Packet Count'), html.Th('Byte Count')])
        ),
        html.Tbody([
            html.Tr([
                html.Td(flow.get('actions', '')),
                html.Td(flow.get('packet_count', '')),
                html.Td(flow.get('byte_count', ''))
            ]) for flow in flows
        ])
    ])
    return html.Div([
        html.H3('流表信息'),
        flows_table
    ])


if __name__ == '__main__':
    app.run_server(debug=True)

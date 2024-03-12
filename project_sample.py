import dash
from dash import Dash, html, dcc
import requests
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
from dash.exceptions import PreventUpdate


app = Dash(__name__)

#组件：整体布局
app.layout = html.Div([
    html.H1("交换机信息实时展示"),
    #组件：计时器
    dcc.Interval(
        id='interval-component',
        interval=1*1000, 
        n_intervals=0
    ),
    html.Div(id='switches-info'),  #组件：交换机信息
    html.Div(id='flows-info'),     #组件：流量信息
    dcc.Graph(id='rx-packets-time-series')  #组件：流量图(接收流量)
])


#函数：数据包信息更新
@app.callback(Output('rx-packets-time-series', 'figure'),   #输出：流量图组件的figure
              [Input('interval-component', 'n_intervals')]) #输入：计时器组件的n_intervals

def update_rx_packets_time_series(n):
    df = pd.read_csv('data.csv')
    
    df['time'] = pd.to_datetime(df['time']).dt.strftime('%H:%M:%S')

    df['rx_rate'] = df['rx-bytes'].diff()

    trace = go.Scatter(
        x=df['time'],
        y=df['rx_rate']*8,
        mode='lines+markers',
        name='接收包速率'
    )

    layout = go.Layout(
        title='接收包速率随时间变化',
        xaxis=dict(title='时间'),
        yaxis=dict(title='速率 (bytes/s)')
    )
    
    return {'data': [trace], 'layout': layout}


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

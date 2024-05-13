import os
import pathlib
import random
import json
import dash
from dash import dcc, html, dash_table, callback_context
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import dash_daq as daq
import pandas as pd
from io import StringIO
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash.exceptions import PreventUpdate



app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}], #定义初始Dash应用程序，设置默认缩放大小
)

app.title = "SDN网络监控"  #网页名称
server = app.server  #部署Flask服务器对象
app.config["suppress_callback_exceptions"] = True  #允许在回调函数中使用动态生成的组件，避免调用异常

APP_PATH = str(pathlib.Path(__file__).parent.resolve()) #获取当前脚本文件所在的目录的绝对路径
df = pd.read_csv(os.path.join(APP_PATH, os.path.join("data", "data.csv"))) #读取csv文件

params = list(df)   #获取列名
max_length = len(df)   #获取行数

switch_list = [1, 2, 3, 4, 5]
flow_info = {
    "1": [
        {
            "actions": [
                "OUTPUT:4294967293"
            ],
            "idle_timeout": 0,
            "cookie": 0,
            "packet_count": 563,
            "hard_timeout": 0,
            "byte_count": 28713,
            "length": 96,
            "duration_nsec": 149000000,
            "priority": 65535,
            "duration_sec": 180,
            "table_id": 0,
            "flags": 0,
            "match": {
                "dl_type": 35020,
                "dl_dst": "01:80:c2:00:00:0e"
            }
        },
        {
            "actions": [
                "OUTPUT:1"
            ],
            "idle_timeout": 0,
            "cookie": 0,
            "packet_count": 7,
            "hard_timeout": 0,
            "byte_count": 518,
            "length": 104,
            "duration_nsec": 223000000,
            "priority": 1,
            "duration_sec": 154,
            "table_id": 0,
            "flags": 0,
            "match": {
                "dl_dst": "00:00:00:00:00:16",
                "dl_src": "00:00:00:00:00:17",
                "in_port": 2
            }
        },
        {
            "actions": [
                "OUTPUT:2"
            ],
            "idle_timeout": 0,
            "cookie": 0,
            "packet_count": 4,
            "hard_timeout": 0,
            "byte_count": 336,
            "length": 104,
            "duration_nsec": 215000000,
            "priority": 1,
            "duration_sec": 154,
            "table_id": 0,
            "flags": 0,
            "match": {
                "dl_dst": "00:00:00:00:00:17",
                "dl_src": "00:00:00:00:00:16",
                "in_port": 1
            }
        },
        {
            "actions": [
                "OUTPUT:4294967293"
            ],
            "idle_timeout": 0,
            "cookie": 0,
            "packet_count": 19,
            "hard_timeout": 0,
            "byte_count": 1384,
            "length": 80,
            "duration_nsec": 184000000,
            "priority": 0,
            "duration_sec": 180,
            "table_id": 0,
            "flags": 0,
            "match": {}
        }
    ]
}
flow_rows =[]
for entry in flow_info["1"]:
    actions = entry["actions"][0] if "actions" in entry else None
    dl_src = entry["match"].get("dl_src", None)
    dl_dst = entry["match"].get("dl_dst", None)
    in_port = entry["match"].get("in_port", None)

    flow_rows.append([actions, dl_src, dl_dst, in_port])
df_flow = pd.DataFrame(flow_rows, columns=["actions", "dl_src", "dl_dst", "in_port"])

port_info = {
    "1": [
        {
            "tx_dropped": 0,
            "rx_packets": 0,
            "rx_crc_err": 0,
            "tx_bytes": 0,
            "rx_dropped": 3,
            "port_no": 4294967294,
            "rx_over_err": 0,
            "rx_frame_err": 0,
            "rx_bytes": 0,
            "tx_errors": 0,
            "duration_nsec": 899000000,
            "collisions": 0,
            "duration_sec": 2107,
            "rx_errors": 0,
            "tx_packets": 0
        },
        {
            "tx_dropped": 0,
            "rx_packets": 273,
            "rx_crc_err": 0,
            "tx_bytes": 16072,
            "rx_dropped": 0,
            "port_no": 1,
            "rx_over_err": 0,
            "rx_frame_err": 0,
            "rx_bytes": 16072,
            "tx_errors": 0,
            "duration_nsec": 83000000,
            "collisions": 0,
            "duration_sec": 1429,
            "rx_errors": 0,
            "tx_packets": 273
        },
        {
            "tx_dropped": 0,
            "rx_packets": 272,
            "rx_crc_err": 0,
            "tx_bytes": 16030,
            "rx_dropped": 0,
            "port_no": 2,
            "rx_over_err": 0,
            "rx_frame_err": 0,
            "rx_bytes": 16030,
            "tx_errors": 0,
            "duration_nsec": 245000000,
            "collisions": 0,
            "duration_sec": 1425,
            "rx_errors": 0,
            "tx_packets": 272
        },
        {
            "tx_dropped": 0,
            "rx_packets": 266,
            "rx_crc_err": 0,
            "tx_bytes": 15554,
            "rx_dropped": 0,
            "port_no": 3,
            "rx_over_err": 0,
            "rx_frame_err": 0,
            "rx_bytes": 15554,
            "tx_errors": 0,
            "duration_nsec": 244000000,
            "collisions": 0,
            "duration_sec": 1425,
            "rx_errors": 0,
            "tx_packets": 266
        }
    ]
}
port_rows =[]
for entry in port_info["1"]:
    port_no = entry["port_no"] if "port_no" in entry else None
    rx_bytes = entry["rx_bytes"] if "rx_bytes" in entry else None
    tx_bytes = entry["tx_bytes"] if "tx_bytes" in entry else None
    duration_sec = entry["duration_sec"] if "duration_sec" in entry else None
    duration_nsec = entry["duration_nsec"] if "duration_nsec" in entry else None
    duration = duration_sec + duration_nsec / 1e9
    port_rows.append([port_no, rx_bytes, tx_bytes, duration])
# print(port_rows)
port_list = [sublist[0] for sublist in port_rows]
port_dir = {}
for sub_port in port_rows:
    port = sub_port[0]
    port_dir.update(
        {
            str(port): {
                "rx_bytes": [sub_port[1]],
                "tx_bytes": [sub_port[2]],
                "duration": [sub_port[3]],
            }
        }
    )
# print(port_dir)

#定义后缀变量
suffix_row = "_row"
suffix_button_id = "_button"
suffix_sparkline_graph = "_sparkline_graph"
suffix_count = "_count"
suffix_ooc_n = "_OOC_number"
suffix_ooc_g = "_OOC_graph"
suffix_indicator = "_indicator"



#构建banner
def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("SDN网络拥塞控制中心"),
                    html.H6("SDN Network Congestion Control Center"),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.A(
                        html.Button(children="ENTERPRISE DEMO"),
                        href="https://plotly.com/get-demo/",
                    ),
                    html.Button(
                        id="learn-more-button", children="LEARN MORE", n_clicks=0
                    ),
                    html.A(
                        html.Img(id="logo", src=app.get_asset_url("dash-logo-new.png")),
                        href="https://plotly.com/dash/",
                    ),
                ],
            ),
        ],
    )

#构建选项卡
def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab2",
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="Specs-tab",
                        label="Specification Settings: 设置中心",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Control-chart-tab",
                        label="Control Charts Dashboard: 控制中心",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                ],
            )
        ],
    )

#数据统计
def init_df():
    ret = {}
    for col in list(df[1:]):
        data = df[col]
        stats = data.describe()  #对当前列的数据进行描述性统计，包括计数、均值、标准差、最小值、最大值等

        std = stats["std"].tolist() #获取标准差，并转换为列表
        ucl = (stats["mean"] + 3 * stats["std"]).tolist() #计算上控制限
        lcl = (stats["mean"] - 3 * stats["std"]).tolist() #计算下控制限
        usl = (stats["mean"] + stats["std"]).tolist() #计算上规格限
        lsl = (stats["mean"] - stats["std"]).tolist() #计算下规格限

        #更新ret数据字典
        ret.update(
            {
                col: {
                    "count": stats["count"].tolist(),
                    "data": data,
                    "mean": stats["mean"].tolist(),
                    "std": std,
                    "ucl": round(ucl, 3), #四舍五入到第三位
                    "lcl": round(lcl, 3),
                    "usl": round(usl, 3),
                    "lsl": round(lsl, 3),
                    "min": stats["min"].tolist(),
                    "max": stats["max"].tolist(),
                    "ooc": populate_ooc(data, ucl, lcl),
                }
            }
        )

    return ret

#用于计算超出控制限观测点的比例
def populate_ooc(data, ucl, lcl):
    ooc_count = 0
    ret = []
    for i in range(len(data)):
        if data[i] >= ucl or data[i] <= lcl:
            ooc_count += 1
            ret.append(ooc_count / (i + 1))
        else:
            ret.append(ooc_count / (i + 1))
    return ret

#初始化统计数据字典
state_dict = init_df()

def init_value_setter_store():
    # Initialize store data
    state_dict = init_df()
    return state_dict






#设置页面
def build_tab_1():
    return [
        # Manually select metrics
        html.Div(
            id="set-specs-intro-container",
            # className='twelve columns',
            children=[html.P(
                "Use historical control limits to establish a benchmark, or set new values."
            ),
                html.Br(),
                html.P(
                "使用历史控制限制来建立基准,或者设置新的值。"
            ),
            ]
        ),
        html.Div(
            id="settings-menu",
            children=[
                html.Div(
                    id="metric-select-menu",
                    # className='five columns',
                    children=[
                        html.Label(id="metric-select-title", children="Select Metrics: 选择指标"),
                        html.Br(),
                        dcc.Dropdown(
                            id="metric-select-dropdown",
                            options=list(
                                {"label": param, "value": param} for param in params[1:] #指标为所有的列名
                            ),
                            value=params[1],
                        ),
                    ],
                ),
                html.Div(
                    id="value-setter-menu",
                    # className='six columns',
                    children=[
                        html.Div(id="value-setter-panel"),
                        html.Br(),
                        html.Div(
                            id="button-div",
                            children=[
                                html.Button("Update", id="value-setter-set-btn"),
                                html.Button(
                                    "View current setup",
                                    id="value-setter-view-btn",
                                    n_clicks=0,
                                ),
                            ],
                        ),
                        html.Div(
                            id="value-setter-view-output", className="output-datatable"
                        ),
                    ],
                ),
            ],
        ),
    ]

#设置数字输入框
ud_usl_input = daq.NumericInput(
    id="ud_usl_input", className="setting-input", size=200, max=9999999
)
ud_lsl_input = daq.NumericInput(
    id="ud_lsl_input", className="setting-input", size=200, max=9999999
)
ud_ucl_input = daq.NumericInput(
    id="ud_ucl_input", className="setting-input", size=200, max=9999999
)
ud_lcl_input = daq.NumericInput(
    id="ud_lcl_input", className="setting-input", size=200, max=9999999
)

#创建数值设置行
def build_value_setter_line(line_num, label, value, col3):
    return html.Div(
        id=line_num,
        children=[
            html.Label(label, className="four columns"),
            html.Label(value, className="four columns"),
            html.Div(col3, className="four columns"),
        ],
        className="row",
    )

#设置项目说明模态框
def generate_modal():
    return html.Div(
        id="markdown",
        className="modal",
        children=(
            html.Div(
                id="markdown-container",
                className="markdown-container",
                children=[
                    html.Div(
                        className="close-container",
                        children=html.Button(
                            "Close",
                            id="markdown_close",
                            n_clicks=0,
                            className="closeButton",
                        ),
                    ),
                    html.Div(
                        className="markdown-text",
                        children=dcc.Markdown(
                            children=(
                                """
                        ###### What is this mock app about?

                        This is a dashboard for monitoring real-time process quality along manufacture production line.

                        ###### What does this app shows

                        Click on buttons in `Parameter` column to visualize details of measurement trendlines on the bottom panel.

                        The sparkline on top panel and control chart on bottom panel show Shewhart process monitor using mock data.
                        The trend is updated every other second to simulate real-time measurements. Data falling outside of six-sigma control limit are signals indicating 'Out of Control(OOC)', and will
                        trigger alerts instantly for a detailed checkup.
                        
                        Operators may stop measurement by clicking on `Stop` button, and edit specification parameters by clicking specification tab.

                        ###### Source Code

                        You can find the source code of this app on our [Github repository](https://github.com/plotly/dash-sample-apps/tree/main/apps/dash-manufacture-spc-dashboard).

                    """
                            )
                        ),
                    ),
                ],
            )
        ),
    )

#控制中心——最左侧状态栏
def build_quick_stats_panel():
    return html.Div(
        id="quick-stats",
        className="row",
        children=[
            html.Div(
                id="card-1",
                # className='five columns',
                children=[
                    html.P("To Select The Switches:"),
                    # html.Label(id="switch-select-title", children="Select Switches: "),
                    html.Br(),
                    dcc.Dropdown(
                        id="switch-select-dropdown",
                        options=list(
                            {"label": switch, "value": switch} for switch in switch_list
                        ),
                        value=switch_list[0],
                        style={'width': '200px', 'height': '30px'},
                    ),
                ],
            ),
            html.Div(
                id="card-2",
                children=[
                    html.P("Flow Infos: "),
                    dash_table.DataTable(

                        data=df_flow.to_dict('records'),
                        columns=[{'id': c, 'name': c} for c in df_flow.columns],
                        style_cell_conditional=[
                            {'if': {'column_id': 'actions'},
                             'width': '30%'},
                        ],
                        style_data={
                            'backgroundColor': 'black',
                            'color': 'white'
                        },
                        style_header={
                            'backgroundColor': 'white',
                            'color': 'black',
                            'fontWeight': 'bold'
                        },
                        style_cell={
                            'fontFamily': 'Open Sans Semi Bold',
                            'fontSize': '14px',
                            'textAlign': 'center'
                        },
                    )
                ],
            ),
            html.Div(
                id="utility-card",
                children=[daq.StopButton(id="stop-button", size=160, n_clicks=0)],
            ),
        ],
    )

#标题banner生成器
def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)


def build_top_panel(stopped_interval):
    return html.Div(
        id="top-section-container",
        className="row",
        children=[
            # Metrics summary
            html.Div(
                id="metric-summary-session",
                className="eight columns",
                children=[
                    generate_section_banner("Process Control Metrics Summary: 交换机端口状态栏"), #创建标题banner
                    html.Div(
                        id="metric-div",
                        children=[
                            generate_metric_list_header(), #创建数据表头
                            html.Div(
                                id="metric-rows",
                                children=[
                                    #generate_metric_row_helper(stopped_interval, port)
                                    # generate_metric_row_helper(stopped_interval, 2),
                                    # generate_metric_row_helper(stopped_interval, 3),
                                    # generate_metric_row_helper(stopped_interval, 4),
                                    # generate_metric_row_helper(stopped_interval, 5),
                                    # generate_metric_row_helper(stopped_interval, 6),
                                    # generate_metric_row_helper(stopped_interval, 7),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

#饼图生成器
def generate_piechart():
    return dcc.Graph(
        id="piechart",
        figure={
            "data": [
                {
                    "labels": [],
                    "values": [],
                    "type": "pie",
                    "marker": {"line": {"color": "white", "width": 1}},
                    "hoverinfo": "label",
                    "textinfo": "label",
                }
            ],
            "layout": {
                "margin": dict(l=20, r=20, t=20, b=20),
                "showlegend": True,
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": "white"},
                "autosize": True,
            },
        },
    )


# Build header 创建数据表头
def generate_metric_list_header():
    return generate_metric_row(
        "metric_header",
        {"height": "3rem", "margin": "1rem 0", "textAlign": "center"},
        {"id": "m_header_1", "children": html.Div("Switches No.")},
        {"id": "m_header_2", "children": html.Div("time")},
        {"id": "m_header_3", "children": html.Div("Bandwidth")},
        {"id": "m_header_4", "children": html.Div("RT-rate")},
        {"id": "m_header_5", "children": html.Div("%OcC")},
        {"id": "m_header_6", "children": "Jam/Normal"},
    )

#常规数据行生成
def generate_metric_row_helper(index):
    item = str(index)

    div_id = item + suffix_row
    button_id = item + suffix_button_id  #按钮的id
    sparkline_graph_id = item + suffix_sparkline_graph
    count_id = item + suffix_count
    ooc_percentage_id = item + suffix_ooc_n
    ooc_graph_id = item + suffix_ooc_g
    indicator_id = item + suffix_indicator

    return generate_metric_row(
        div_id,
        None,
        {
            "id":button_id,
            "className": "metric-row-button-text",
            "children": html.Button(
                id={'type': 'dynamic-output', 'index': item},
                className="metric-row-button",
                children="None",
                title="Click to visualize live SPC chart",
                n_clicks=0,
            ),
        },
        {"id": {'type': 'dynamic-time', 'index': count_id}, "children": "None"},
        {
            "id": item + "_sparkline",
            "children": dcc.Graph(
                id={'type': 'dynamic-sparkline', 'index': sparkline_graph_id},
                style={"width": "100%", "height": "95%"},
                config={
                    "staticPlot": False,
                    "editable": False,
                    "displayModeBar": False,
                },
                figure=go.Figure(
                    {
                        "data": [
                            {
                                "x": [],
                                "y": [],
                                "mode": "lines+markers",
                                "name": item,
                                "line": {"color": "#f4d44d"},
                            }
                        ],
                        "layout": {
                            "uirevision": True,
                            "margin": dict(l=0, r=0, t=4, b=4, pad=0),
                            "xaxis": dict(
                                showline=False,
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False,
                                dtick=1
                            ),
                            "yaxis": dict(
                                showline=False,
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False,
                            ),
                            "paper_bgcolor": "rgba(0,0,0,0)",
                            "plot_bgcolor": "rgba(0,0,0,0)",
                        },
                    }
                ),
            ),
        },
        {"id": {'type': 'dynamic-ooc-n', 'index': ooc_percentage_id}, "children": "0.00%"},
        {
            "id": ooc_graph_id + "_container",
            "children": daq.GraduatedBar(
                id={'type': 'dynamic-ooc-g', 'index': ooc_graph_id},
                color={
                    "ranges": {
                        "#92e0d3": [0, 20],
                        "#f4d44d ": [21, 80],
                        "#f45060": [81, 100],
                    }
                },
                showCurrentValue=False,
                max=100,
                value=0,
            ),
        },
        {
            "id": item + "_pf",
            "children": daq.Indicator(
                id={'type': 'dynamic-indicator', 'index': indicator_id}, value=True, color="#91dfd2", size=12
            ),
        },
    )

# 用于生成一个指标行。
# 它返回一个包含6个HTML元素的Div组件，用于呈现指标行的各个列。
def generate_metric_row(id, style, col1, col2, col3, col4, col5, col6):
    if style is None:
        style = {"height": "8rem", "width": "100%"}

    return html.Div(
        id=id,
        className="row metric-row",
        style=style,
        children=[
            html.Div(
                id=col1["id"],
                className="one column",
                style={"margin-right": "2.5rem", "minWidth": "50px"},
                children=col1["children"],
            ),
            html.Div(
                id=col2["id"],
                style={"textAlign": "center"},
                className="one column",
                children=col2["children"],
            ),
            html.Div(
                id=col3["id"],
                style={"height": "100%"},
                className="four columns",
                children=col3["children"],
            ),
            html.Div(
                id=col4["id"],
                style={},
                className="one column",
                children=col4["children"],
            ),
            html.Div(
                id=col5["id"],
                style={"height": "100%", "margin-top": "5rem"},
                className="three columns",
                children=col5["children"],
            ),
            html.Div(
                id=col6["id"],
                style={"display": "flex", "justifyContent": "center"},
                className="one column",
                children=col6["children"],
            ),
        ],
    )

#控制中心——实时图表
def build_chart_panel():
    return html.Div(
        id="control-chart-container",
        className="twelve columns",
        children=[
            generate_section_banner("Live SPC Chart: 实时SPC图表"),
            dcc.Graph(
                id="control-chart-live",
                figure=go.Figure(
                    {
                        "data": [
                            {
                                "x": [],
                                "y": [],
                                "mode": "lines+markers",
                                "name": "",
                            }
                        ],
                        "layout": {
                            "paper_bgcolor": "rgba(0,0,0,0)",
                            "plot_bgcolor": "rgba(0,0,0,0)",
                            "xaxis": dict(
                                showline=False, showgrid=False, zeroline=False
                            ),
                            "yaxis": dict(
                                showgrid=False, showline=False, zeroline=False
                            ),
                            "autosize": True,
                        },
                    }
                ),
            ),
        ],
    )


def generate_graph(interval, data, port):
    rate = 0
    if interval == 0 or len(data[port]["rx_bytes"]) < 2 or len(data[port]["duration"]) < 2:
        return dict(x=[[0]], y=[[0]]), [0]
    else:
        rate = (data[port]["rx_bytes"][-1] - data[port]["rx_bytes"][-2]) / (data[port]["duration"][-1] - data[port]["duration"][-2]) + random.randint(-200, 200)

    x_array = interval
    y_array = rate



    return dict(x=[[x_array]], y=[[y_array]]), [0]


#更新迷你图
def update_sparkline(time, rate, data):

    x_new = time
    y_new = rate

    return dict(x=[[x_new]], y=[[y_new]]), [0] #一号轨迹

#更新计数, 即数据表中各项内容
def update_count(interval, port, data):
    if interval == 0 or len(data[port]["rx_bytes"]) < 2 or len(data[port]["duration"]) < 2:
        return "None", "0", 0.00001, "0.00%", "#92e0d3"  # port, time, rate, occ, color

    else:

        rate = (data[port]["rx_bytes"][-1] - data[port]["rx_bytes"][-2]) / (data[port]["duration"][-1] - data[port]["duration"][-2]) + random.randint(-200, 200)

        ooc_percentage_f = rate / 1300 * 100
        ooc_percentage_str = "%.2f" % ooc_percentage_f + "%"

        # Set maximum ooc to 15 for better grad bar display
        if ooc_percentage_f > 100:
            ooc_percentage_f = 100

        if ooc_percentage_f == 0.0:
            ooc_grad_val = 0.00001
        else:
            ooc_grad_val = float(ooc_percentage_f)

        # Set indicator theme according to threshold 5%
        if 0 <= ooc_grad_val <= 20:
            color = "#92e0d3"  #蓝色
        elif 20 < ooc_grad_val < 70:
            color = "#f4d44d"  #黄色
        else:
            color = "#FF0000"  #红色

    return port, data[port]["duration"][-1], rate, ooc_grad_val, color





#构建完整的html页面
app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(), #创建主banner栏
        dcc.Interval(  #创建定时器
            id="interval-component",
            interval=2 * 500,  # 数据刷新间隔
            n_intervals=0,  # 初始调用次数为50
            disabled=False,
        ),
        html.Div(
            id="app-container",
            children=[
                # build_tabs(), #创建两个选项卡页面
                # Main app

                html.Div(id="app-content",
                        children=[
                                html.Div(
                                    id="status-container",
                                    children=[
                                        build_quick_stats_panel(),
                                        html.Div(
                                            id="graphs-container",
                                            children=[build_top_panel(0), build_chart_panel()],
                                        ),
                                    ],
                                ),
                        ],
                ),
            ],
        ),
        #dcc.Store：用于前端传递数据
        dcc.Store(id="value-setter-store", data=port_dir), #数据字典
        dcc.Store(id="port-store", data=[]), #端口字典
        dcc.Store(id="select-port", data=""), #端口字典
        dcc.Store(id="n-interval-stage", data=50), #调用次数
        html.Div(id='dummy-output', style={'display': 'none'}),
        generate_modal(), #创建模态框
    ],
)


# Update interval 更新计时器状态到主app，切页面时触发
@app.callback(
    Output("n-interval-stage", "data"),
    [Input("app-tabs", "value")],
    [
        State("interval-component", "n_intervals"),
        State("interval-component", "disabled"),
        State("n-interval-stage", "data"),
    ],
)
def update_interval_state(tab_switch, cur_interval, disabled, cur_stage):
    if disabled:
        return cur_interval
    if tab_switch == "tab1":
        return cur_interval

    # 如果 Tab2下计数器未启用 或 在Tab1 则 前端调用次数同步为 计数器次数
    return cur_stage
    # 前端调用次数 同步为 前端调用次数


# Callbacks for stopping interval update 用于停止间隔更新的回调
@app.callback(
    [Output("interval-component", "disabled"), Output("stop-button", "buttonText")],
    [Input("stop-button", "n_clicks")],
    [State("interval-component", "disabled")],
)
def stop_production(n_clicks, current):
    if n_clicks == 0:
        return False, "stop"
    return not current, "stop" if current else "start"
#按钮开始计数器启动，stop则暂停


# ======= Callbacks for modal popup 模态框弹出逻辑（learn more按钮） =======
@app.callback(
    Output("markdown", "style"),
    [Input("learn-more-button", "n_clicks"), Input("markdown_close", "n_clicks")],
)
def update_click_output(button_click, close_click):
    ctx = dash.callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id == "learn-more-button":
            return {"display": "block"}

    return {"display": "none"}


# ======= update progress gauge 更新进度表 =========
@app.callback(
    output=Output("progress-gauge", "value"),
    inputs=[Input("interval-component", "n_intervals")],
)
def update_gauge(interval):
    if interval < max_length:
        total_count = interval
    else:
        total_count = max_length

    return int(total_count)




# ====== Callbacks to update stored data via click 设置存储数据的更新回调=====
@app.callback(
    output=[Output("value-setter-store", "data"),
            Output("port-store", "data"),
    ],
    inputs=[Input("interval-component", "n_intervals"),
            Input("switch-select-dropdown", "value"),
    ],
    state=[State("value-setter-store", "data"),
    ],
)
def set_value_setter_store(interval, switch, data):
    if not interval:
        return data, list(data.keys())
    else:
        for port in data.keys():
            data[port]["rx_bytes"].append(data[port]["rx_bytes"][-1] + 1000 )
            data[port]["duration"].append(data[port]["duration"][-1] + 1)

        return data, list(data.keys())


@app.callback(
    [
        Output({'type': 'dynamic-output', 'index': ALL}, "children"),
        Output({'type': 'dynamic-time', 'index': ALL}, "children"),
        Output({'type': 'dynamic-sparkline', 'index': ALL}, "extendData"),
        Output({'type': 'dynamic-ooc-n', 'index': ALL}, "children"),
        Output({'type': 'dynamic-ooc-g', 'index': ALL}, "value"),
        Output({'type': 'dynamic-indicator', 'index': ALL}, "color"),
    ],
    [Input("interval-component", "n_intervals")],
    [State("port-store", "data"), State("value-setter-store", "data")]
)
def update_multiple_controls(interval, ports, current_data):
    if not ports:
        raise PreventUpdate

    outputs = []

    ports_output = []
    times_output = []
    sparklines_output = []
    rates_output = []
    occs_output = []
    colors_output = []

    for param in ports:
        port, time, rate, occ, color = update_count(
            interval, param, current_data
        )
        spark_line_data = update_sparkline(interval, rate, current_data)


        ports_output.append(port)
        times_output.append(time)
        sparklines_output.append(spark_line_data)
        rates_output.append(rate)
        occs_output.append(occ)
        colors_output.append(color)

    return [
        ports_output,
        times_output,
        sparklines_output,
        rates_output,
        occs_output,
        colors_output
    ]






















@app.callback(
    output=Output("metric-rows", "children"),
    inputs=[Input("switch-select-dropdown", "value"),
    ],
    state=[State("metric-rows", "children"),
           State("value-setter-store", "data")
    ],
)
def update_datarows(switch, children, data):
    if data == None:
        return children
    else:
        # print("update_datarows")
        # print(data)
        return [generate_metric_row_helper(port) for port in data.keys()]



# ======= button to choose/update figure based on click ============
@app.callback(
    output=Output("control-chart-live", "figure"),
    inputs=[
        Input({'type': 'dynamic-output', 'index': ALL}, 'n_clicks'),
    ],
    state=[State({'type': 'dynamic-output', 'index': ALL}, 'index'),
    ],
)
def clear_control_chart(clicks, index):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    triggered_id, triggered_value = ctx.triggered[0]['prop_id'].split('.')
    triggered_id = json.loads(triggered_id)
    port = triggered_id["index"]
    print(port)

    if port is None:
        raise PreventUpdate


    return go.Figure(
                    {
                        "data": [
                            {
                                "x": [],
                                "y": [],
                                "mode": "lines+markers",
                                "name":port ,
                            }
                        ],
                        "layout": {
                            "paper_bgcolor": "rgba(0,0,0,0)",
                            "plot_bgcolor": "rgba(0,0,0,0)",
                            "xaxis": dict(
                                showline=False, showgrid=False, zeroline=False
                            ),
                            "yaxis": dict(
                                showgrid=False, showline=False, zeroline=False
                            ),
                            "autosize": True,
                        },
                    }
                )


@app.callback(
    output=Output("control-chart-live", "extendData"),
    inputs=[
        Input("interval-component", "n_intervals"),
    ],
    state=[State("value-setter-store", "data"),
           State("control-chart-live", "figure"),
           State({'type': 'dynamic-output', 'index': ALL}, 'n_clicks'),
    ],
)
def update_control_chart(interval, data, figure, clicks):
    port = figure["data"][0]["name"]
    if port == "":
        port = next(iter(data.keys()))
    return generate_graph(interval, data, port)


# Running the server
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)

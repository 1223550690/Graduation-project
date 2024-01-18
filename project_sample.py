import dash
from dash import Dash, html, dcc
import requests
from dash.dependencies import Input, Output
import pandas as pd


app = Dash(__name__)


app.layout = html.Div([
    html.H1("交换机信息实时展示"),
    dcc.Interval(
        id='interval-component',
        interval=1*1000, 
        n_intervals=0
    ),
    html.Div(id='switches-info')
])


@app.callback(Output('switches-info', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_switches_info(n):
    # Ryu REST API endpoint
    url = 'http://localhost:8080/stats/switches'
    

    try:
        response = requests.get(url)

        switches = response.json()
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


if __name__ == '__main__':
    app.run_server(debug=True)

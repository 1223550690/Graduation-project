from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, ALL

import dash as dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State


app = dash.Dash(__name__)

layout = html.Div([
    html.Button("Add Filter", id="add-filter", n_clicks=0),
    html.Div(id='dropdown-container', children=[]),
    html.Div(id='dropdown-container-output')
])
app.layout = layout

@app.callback(
    Output('dropdown-container', 'children'),
    Input('add-filter', 'n_clicks'),
    State('dropdown-container', 'children'))
def display_dropdowns(n_clicks, children):
    new_dropdown = dcc.Dropdown(
        id={
            'type': 'filter-dropdown',
            'index': n_clicks
        },
        options=[{'label': i, 'value': i}
                 for i in ['NYC', 'MTL', 'LA', 'TOKYO']]
    )
    children.append(new_dropdown)
    return children


@app.callback(
    Output('dropdown-container-output', 'children'),
    Input({'type': 'filter-dropdown', 'index': ALL}, 'value')
)
def display_output(values):
    return html.Div([
        html.Div('Dropdown {} = {}'.format(i + 1, value))
        for (i, value) in enumerate(values)
    ])

if __name__ == "__main__":
    app.run_server(debug=True, port=8080)


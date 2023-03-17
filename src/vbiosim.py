'''A viewer for information on Biosimulations'''

import dash
import dash_html_components as html
import plotly.graph_objects as go
from dash import dcc
import plotly.express as px
from dash.dependencies import Input, Output
import requests

API_URL = "https://api.biosimulations.org"
PROJECT_URL = "%s/projects" % API_URL
response = requests.get(PROJECT_URL)
projects = response.json()
import pdb; pdb.set_trace()


app = dash.Dash()
application = app.server

df = px.data.stocks()


app.layout = html.Div(id = 'parent', children = [
    html.H1(id = 'H1', children = 'Styling using html components', style = {'textAlign':'center',\
                                            'marginTop':40,'marginBottom':40}),

        dcc.Dropdown( id = 'dropdown',
        options = [
            {'label':'GGoogle', 'value':'GOOG' },
            {'label': 'AApple', 'value':'AAPL'},
            {'label': 'AAmazon', 'value':'AMZN'},
            ],
        value = 'GOOG'),
        dcc.Graph(id = 'bar_plot')
    ])


@app.callback(Output(component_id='bar_plot', component_property= 'figure'),
              [Input(component_id='dropdown', component_property= 'value')])
def graph_update(dropdown_value):
    print(dropdown_value)
    fig = go.Figure([go.Scatter(x = df['date'], y = df['{}'.format(dropdown_value)],\
                     line = dict(color = 'firebrick', width = 4))
                     ])

    fig.update_layout(title = 'Stock prices over time',
                      xaxis_title = 'Dates',
                      yaxis_title = 'Prices'
                      )
    return fig



if __name__ == '__main__':
    app.run_server()

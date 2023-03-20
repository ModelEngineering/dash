'''A viewer for information on Biosimulations'''

import dash
from dash import html
import plotly.graph_objects as go
from dash import dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output
import requests

API_URL = "https://api.biosimulations.org"
PROJECT_URL = "%s/projects" % API_URL
response = requests.get(PROJECT_URL)
project_descs = response.json()

# Construct the list of projects
project_dct = {d["id"]: d for d in project_descs}
project_ids = list(project_dct.keys())
project_dropdowns = [dict(label=v, value=v) for v in project_ids]

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
application = app.server

project_col = dbc.Col(dbc.Row([
      html.H2("Project"),
      dcc.Dropdown(id = 'dropdown1', options = project_dropdowns,
            value = project_ids[0]),
      ])
)
details_col = dbc.Col(dbc.Row([
      html.H2("Details"),
      dcc.Markdown(id = 'details', style={'whiteSpace': 'pre-line'})
      ])
)

app.layout = html.Div([
    dbc.Row([
          project_col,
          details_col
          ],
    ),
])


######### CALL BACKS ############
@app.callback(Output(component_id='selection1', component_property= 'children'),
              [Input(component_id='dropdown1', component_property= 'value')])
def graph_update(dropdown_value):
    return dropdown_value

@app.callback(Output(component_id='details', component_property= 'children'),
              [Input(component_id='dropdown1', component_property= 'value')])
def getProjectDetails(project_id):
    lst = ["**%s**: %s" % (k, v) for k, v in project_dct[project_id].items()]
    return "\n".join(lst)

########## SAVE #########
#      style = {'textAlign':'center', 'marginTop':40,'marginBottom':40})


if __name__ == '__main__':
    app.run_server()

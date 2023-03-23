'''A viewer for information on Biosimulations'''

import dash
from dash import html
import plotly.graph_objects as go
from dash import dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output
import json
import requests
import yaml
import whoosh.index as index
from whoosh.qparser import QueryParser
from htmldom import htmldom
from requests_html import HTMLSession
from selenium import webdriver

import src.constants as cn

API_URL = "https://api.biosimulations.org"
PROJECT_URL = "%s/projects" % API_URL
response = requests.get(PROJECT_URL)
project_descs = response.json()
PAPER_URL = "http://identifiers.org/doi:10.1186/1752-0509-7-135"
PAPER_URL = "http://identifiers.org/doi:10.1016/j.jtbi.2009.03.021"
PAPER_URL = "https://www.google.com/search?q=Mathematical%20modeling%20of%20heat%20shock%20protein%20synthesis%20in%20response%20to%20temperature%20change"

if False:
    # Attempt to execute the page JavaScrpt
    session = HTMLSession()
    r = session.get(PAPER_URL)
    r.html.render()
    import pdb; pdb.set_trace()

# Construct the list of projects
project_dct = {d["id"]: d for d in project_descs}
project_ids = list(project_dct.keys())
project_dropdowns = [dict(label=v, value=v) for v in project_ids]

# Get the indexer
indexer = index.open_dir(cn.INDEX_DIR)

#summary_url = "%s/projects/%s/summary" % (API_URL, project_ids[0])
#response = requests.get(summary_url)
#print(yaml.dump(json.loads(response.content), default_flow_style=False))

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
application = app.server

# UI dfinitions
project_col = dbc.Col(dbc.Row([
      html.H2("Project"),
      dcc.Dropdown(id='dropdown1', options=project_dropdowns,
            value=project_ids[0]),
      ])
)
search_col = dbc.Col(dbc.Row([
      dbc.Input(id="search", placeholder="Enter query ...", type="text"),
      ])
)
abstract_col = dbc.Col(dbc.Row([
      html.H2("Abstract"),
      dcc.Markdown(id = 'Abstract', style={'whiteSpace': 'pre-line',
            'padding-left': '40px', 'padding-right': '20px'})
      ])
)

details_col = dbc.Col(dbc.Row([
      html.H2("Details"),
      dcc.Markdown(id = 'Details', style={'whiteSpace': 'pre-line',
            'padding-left': '40px'})
      ])
)

app.layout = html.Div([
    dbc.Row([
        html.H1("Query BioSimulations")
        ],
        justify="center", align="center"
    ),
    dbc.Row([
          search_col,
          ]
    ),
    dbc.Row([
          project_col,
          abstract_col
          ],
    ),
    dbc.Row([
          details_col,
          ],
    ),
])


######### CALL BACKS ############
@app.callback(Output(component_id='Abstract', component_property= 'children'),
              [Input(component_id='dropdown1', component_property= 'value')])
def getProjectSummary(project_id):
    summary_url = "%s/projects/%s/summary" % (API_URL, project_id)
    response = requests.get(summary_url)
    null = None
    dct = eval(response.content.decode())
    if len(dct["simulationRun"]["metadata"]) > 0:
        abstract = dct["simulationRun"]["metadata"][0]["abstract"]
        uri = dct["simulationRun"]["metadata"][0]["citations"][0]["uri"]
    else:
        abstract = "None."
        uri = ""
    text = "%s\n%s" % (abstract, uri)
    return text

@app.callback(Output(component_id='Details', component_property= 'children'),
              [Input(component_id='dropdown1', component_property= 'value')])
def getProjectDetails(project_id):
    summary_url = "%s/projects/%s/summary" % (API_URL, project_id)
    response = requests.get(summary_url)
    null = None
    dct = eval(response.content.decode())
    abstract = dct["simulationRun"]["metadata"][0]["abstract"]
    result = str(yaml.dump(json.loads(response.content), default_flow_style=False))
    return result

@app.callback(Output(component_id='dropdown1', component_property= 'options'),
              [Input(component_id='search', component_property= 'value')])
def getSearchTerms(term):
    if len(term) > 0:
        with indexer.searcher() as searcher:
            new_term = term + "*"
            query = QueryParser("content", indexer.schema).parse(new_term)
            query_result = searcher.search(query)
            query_ids = [project_ids[p[0]] for p in query_result.items()]
            query_dropdowns = [dict(label=v, value=v) for v in query_ids]
            import pdb; pdb.set_trace()
            print(query_dropdowns)
            return query_dropdowns
    else:
        return project_dropdowns



if __name__ == '__main__':
    app.run_server()

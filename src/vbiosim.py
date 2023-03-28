'''A viewer for information on Biosimulations'''

import dash
from dash import html
import plotly.graph_objects as go
from dash import dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output
import json
import pandas as pd
import requests
import yaml
import whoosh.index as index
from whoosh.qparser import QueryParser
from htmldom import htmldom
from requests_html import HTMLSession
from selenium import webdriver

import src.constants as cn
import src.util as util

######## Constants #######
API_URL = "https://api.biosimulations.org"
CHILDREN = 'children'
PROJECT_URL = "%s/projects" % API_URL
response = requests.get(PROJECT_URL)
project_descs = response.json()
PROJECT_DCT = {d["id"]: d for d in project_descs}
PROJECT_IDS = list(PROJECT_DCT.keys())
PAPER_URL = "https://www.google.com/search?q=Mathematical%20modeling%20of%20heat%20shock%20protein%20synthesis%20in%20response%20to%20temperature%20change"
OLD_RAD = "old"
PLACEHOLDER = "placeholder"  # Used if there is no output in a callback
NEW_RAD = "new"
ABSTRACT_DF = pd.read_csv(cn.ABSTRACT_FILE)
ABSTRACT_DF.index = ABSTRACT_DF[cn.ID]
ABSTRACT_DF = util.cleanDF(ABSTRACT_DF)

####### State Object ########
class OptionState():

    def __init__(self, radio_button=OLD_RAD, project_id=PROJECT_IDS[0]):
        self.radio_button = radio_button
        self.project_id = project_id
OPTION_STATE = OptionState()

# Initializations
project_dropdowns = [dict(label=v, value=v) for v in PROJECT_IDS]
# Get the indexer
indexer = index.open_dir(cn.INDEX_DIR)

#summary_url = "%s/projects/%s/summary" % (API_URL, PROJECT_IDS[0])
#response = requests.get(summary_url)
#print(yaml.dump(json.loads(response.content), default_flow_style=False))

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
application = app.server

# UI dfinitions
project_col = dbc.Col(dbc.Row([
      html.H2("Select Project (%d)" % len(PROJECT_IDS)),
      dcc.Dropdown(id='dropdown1', options=project_dropdowns,
            value=PROJECT_IDS[0]),
      # Used to handle callbacks without output
      html.P(id=PLACEHOLDER)
      ])
)
search_col = dbc.Col(dbc.Row([
      dbc.Input(id="search", placeholder="Enter search terms ...", type="text"),
      ])
)
abstract_col = dbc.Col(dbc.Row([
      html.H2("Research Summary"),
      dcc.RadioItems(id = 'input-radio-button',
            options = [
                  dict(label = OLD_RAD, value = OLD_RAD),
                  dict(label = NEW_RAD, value = NEW_RAD),
            ],
            value=OLD_RAD,
            labelStyle={'display': 'block'}
      ),
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
model_summary_col = dbc.Col([
      html.H2("Model Elements"),
      dcc.Markdown( 'Glu: [Glucose](https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:17234)',
            id = 'Model Summary',
            style={'whiteSpace': 'pre-line',
                  'padding-left': '40px', 'padding-right': '20px'},
      )
])
model_details_col = dbc.Col([
      html.H2("Model Details"),
      dcc.Markdown( 'A + B -> C',
            id = 'Model Details',
            ),
      ],
      style={'whiteSpace': 'pre-line',
            'padding-left': '40px', 'padding-right': '20px',
            'textAlign': 'center'},
)
simulation_col = dbc.Col([
      html.H2("Simulation"),
      dcc.Markdown( 'A Graph',
            id = 'Simulation',
      ) ],
      style={'whiteSpace': 'pre-line',
            'padding-left': '40px', 'padding-right': '20px',
            'textAlign': 'center'},
)
download_col = dbc.Col(
      [html.Button('Download', id='download')],
      style={'margin-bottom': '10px',
              'textAlign':'center',
              'width': '220px',
              'margin':'auto'}
)



#@app.callback(Output('output-text', CHILDREN),
#              [Input('input-radio-button', 'value')])
#def update_graph(value):
#    return f'The selected value is {value}'


app.layout = html.Div([
    dbc.Row([
          html.H1("Query BioSimulations"),
          html.Br(),
        ],
        justify="center", align="center"
    ),
    dbc.Row([
          search_col,
          html.Div(style={"margin-left": "25px"}),
          ]
    ),
    dbc.Row([
          project_col,
          abstract_col,
          html.Div(style={"margin-left": "25px"}),
          ],
    ),
    dbc.Row([
          details_col,
          ],
    ),
    dbc.Row([
          model_summary_col,
          model_details_col,
          simulation_col,
          html.Div(style={"margin-left": "25px"}),
          ],
    ),
    dbc.Row([
          download_col,
          ],
    ),
])


######### CALL BACKS ############
#-------- HELPERS -----------#
def calculateAbstractText(project_id):
    # TODO: class that decomdes project summary
    summary_url = "%s/projects/%s/summary" % (API_URL, project_id)
    response = requests.get(summary_url)
    null = None
    dct = eval(response.content.decode())
    # URI
    if len(dct["simulationRun"]["metadata"]) > 0:
        uri = dct["simulationRun"]["metadata"][0]["citations"][0]["uri"]
    else:
        uri = ""
    # Abstract and citation
    if (OPTION_STATE.radio_button == OLD_RAD) or (not project_id in set(ABSTRACT_DF["id"])):
        if len(dct["simulationRun"]["metadata"]) > 0:
            abstract = dct["simulationRun"]["metadata"][0]["abstract"]
            citation = ""
        else:
            abstract = "None."
            citation = ""
    else:
        # FIXME: Wrong types in ABSTRACT_DF
        abstract = ABSTRACT_DF.loc[project_id, "abstract"]
        citation = ABSTRACT_DF.loc[project_id, "citation"]
        if not isinstance(abstract, str):
            abstract = abstract.values[0]
        if not isinstance(citation, str):
            citation = citation.values[0]
    # Construct result
    citation = "*" + citation + "*"
    result = "%s\n\n%s\n\n%s" % (citation, abstract, uri)
    return result

#-------- CALLBACKS -----------#
@app.callback(Output(component_id='Abstract', component_property= CHILDREN),
              [Input(component_id='dropdown1', component_property= 'value'),
               Input('input-radio-button', 'value'),
              ])
def updateAbstract(project_id, radio_button):
    OPTION_STATE.project_id = project_id
    OPTION_STATE.radio_button = radio_button
    text = calculateAbstractText(project_id)
    return text

@app.callback(Output(component_id='Details', component_property= CHILDREN),
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
    return project_dropdowns
    if len(term) > 0:
        with indexer.searcher() as searcher:
            new_term = term + "*"
            query = QueryParser("content", indexer.schema).parse(new_term)
            query_result = searcher.search(query)
            query_ids = [PROJECT_IDS[p[0]] for p in query_result.items()]
            query_dropdowns = [dict(label=v, value=v) for v in query_ids]
            import pdb; pdb.set_trace()
            print(query_dropdowns)
            return query_dropdowns
    else:
        return project_dropdowns

## Handle change in type of abstract display
#@app.callback(Output(component_id='Abstract', component_property= CHILDREN, allow_duplicate=True),
#              [Input('input-radio-button', 'value')])
#def updateAbstractMode(value):
#    OPTION_STATE.radio_button = value
#    text = calculateAbstractText(OPTION_STATE.project_id)
#    return text



if __name__ == '__main__':
    app.run_server(debug=True)

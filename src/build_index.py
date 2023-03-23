"""Builds the index for search simulation abstracts"""
import whoosh
from whoosh.index import create_in
from whoosh.fields import *
import requests
import pandas as pd

import src.constants as cn

API_URL = "https://api.biosimulations.org"
PROJECT_URL = "%s/projects" % API_URL

# Get the list of projects
response = requests.get(PROJECT_URL)
project_descs = response.json()
project_dct = {d["id"]: d for d in project_descs}
project_ids = list(project_dct.keys())

# Initialize the indexer
schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
ix = create_in("indexdir", schema)
writer = ix.writer()

# Iterate over project abstracts
abstract_dct = {"id": [], "abstract": []}
for id in project_ids:
    summary_url = "%s/projects/%s/summary" % (API_URL, id)
    response = requests.get(summary_url)
    null = None
    dct = eval(response.content.decode())
    abstract = dct["simulationRun"]["metadata"][0]["abstract"]
    writer.add_document(title=id, path=u"/a", content=abstract)
    #
    abstract_dct["id"].append(id)
    abstract_dct["abstract"].append(abstract)

#
writer.commit()
df = pd.DataFrame(abstract_dct)
df.to_csv(cn.ABSTRACT_FILE)

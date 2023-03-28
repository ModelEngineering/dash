"""Generates content for search and searches content"""


import constants as cn
import src.util as util

import openai
import os
import pandas as pd
import whoosh
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
import whoosh.index as index


# The API Key must be updated periodically
API_KEY = "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"
MODEL_ENGINE = "gpt-3.5-turbo"
if os.path.isfile(cn.ABSTRACT_FILE):
    ABSTRACT_DF = pd.read_csv(cn.ABSTRACT_FILE)
    ABSTRACT_DF.index = ABSTRACT_DF[cn.ID]
    ABSTRACT_DF = util.cleanDF(ABSTRACT_DF)
else:
    ABSTRACT_DF = None


class Searcher(object):

    def __init__(self, api_key=API_KEY):
        self.api_key = api_key
        openai.api_key = self.api_key

    def get(self, citation_str):
        """
        Returns a summary of the article based on its citation.

        Parameters
        ----------
        citation_str: str

        Returns
        -------
        str
        """
        query_str = "Summarize the paper %s" % citation_str
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system",
                      "content": "You are a helpful assistant."},
                {"role": "user", "content": query_str},
            ])
        return response.choices[0]['message']["content"]

    def search(self, query, index_dir=cn.INDEX_DIR):
        """
        Searches the index for the terms. Searching includes
            OR, AND, ~<n> (number of replacement terms)

        Parameters
        ----------
        query: str
        index_dir: str (path to index directory)

        Returns
        -------
        list-str (list of project ids)
        """
        if ABSTRACT_DF is None:
            raise ValueError("Must build %s before doing search" % cn.ABSTRACT_FILE)
        schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
        indexer = index.open_dir(index_dir)
        with indexer.searcher() as searcher:
            query = QueryParser("content", indexer.schema).parse(query)
            results = searcher.search(query, limit=None)  # Get all search results
            parser.add_plugin(qparser.FuzzyTermPlugin())  # Allow fuzzy search
        #
        project_ids = [r.loc[i, cn.ID] for i, r in ABSTRACT_DF.iterrows()
              if i in results.docs()]
        return project_ids

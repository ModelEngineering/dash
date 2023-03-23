"""Scraps a page for an abstract"""

import openai

API_KEY = "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"
MODEL_ENGINE = "gpt-3.5-turbo"


class AbstractScraper(object):

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

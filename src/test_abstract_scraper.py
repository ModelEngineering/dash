from src.abstract_scraper import AbstractScraper

import json
import os
import unittest


IGNORE_TEST = False
IS_PLOT = False
CITATION_STR = """
summarize the paper
Ana Bulovi\u0107, Stephan Fischer, Marc Dinh, Felipe Golib, Wolfram\
\ Liebermeister, Christian Poirier, Laurent Tournier, Edda Klipp, Vincent\
\ Fromion & Anne Goelzer. Automated generation of bacterial resource allocation\
\ models. Metabolic Engineering 55 (2019): 12-22
"""


#############################
# Tests
#############################
class TestAbstractScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = AbstractScraper()

    def testGet(self):
        abstract_str = self.scraper.get(CITATION_STR)
        self.assertGreater(len(abstract_str), 20)
        self.assertTrue("models" in abstract_str)


if __name__ == '__main__':
  unittest.main()

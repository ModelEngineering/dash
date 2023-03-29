import src.util as util
import src.constants as cn

import os
import unittest


IGNORE_TEST = False
IS_PLOT = False


#############################
# Tests
#############################
class TestFunctions(unittest.TestCase):

    def testindexNested(self):
        if IGNORE_TEST:
            return
        struct = [dict(a=[1, 2, 3], b=4), 3]
        #
        result = util.indexNested(struct, [0, "b"])
        self.assertEqual(result, 4)
        #
        result = util.indexNested(struct, [0, "a", 0])
        self.assertEqual(result, 1)
        #
        result = util.indexNested(struct, ["a", 0])
        self.assertIsNone(result)


if __name__ == '__main__':
  unittest.main()

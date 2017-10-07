
import unittest
from appurl.test.test_basic import BasicTests
from appurl.test.test_issues import TestIssues
from appurl.test.test_parse_url import TestUrlParse


def suite():

    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(BasicTests))
    test_suite.addTest(unittest.makeSuite(TestIssues))
    test_suite.addTest(unittest.makeSuite(TestUrlParse))

    return test_suite


if __name__ == '__main__':
    mySuit=suite()
    runner=unittest.TextTestRunner()
    runner.run(mySuit)
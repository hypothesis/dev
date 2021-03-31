# Just enough to trigger coverage
from dev import *  # pylint: disable=wildcard-import


class TestSanity:
    def tests_are_working(self):
        print("Ok!")

import math
import attune
import pytest
import json


def test_fromTopas4():
    testobj = attune.from_topas4("c:/Users/kamey/work/python/attune/tests/io")

    assert isinstance(testobj, attune.Instrument)
    return


if __name__ == "__main__":
    test_fromTopas4()

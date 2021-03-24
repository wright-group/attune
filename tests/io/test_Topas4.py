import math
import attune
import pytest
import json


def test_fromTopas4():
    testobj=attune.fromTopas4('OpticalDevicesTest.json')
    #print(testobj)
    assert isinstance(testobj,attune.Instrument)
    return

'''
def test_toTopas4():

    return
'''



if __name__ == "__main__":
    #test_toTopas4()
    test_fromTopas4()
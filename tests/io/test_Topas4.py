import math
import attune
import pytest
import json
from pathlib import Path

script_dir=Path(__file__).parent

def test_fromTopas4():
<<<<<<< HEAD
    testobj = attune.from_topas4(script_dir)
    
=======
    testobj = attune.from_topas4("c:/Users/kamey/work/python/attune/tests/io")

>>>>>>> 2258fc071b9eb1a7e808c4b49a90968a49d97407
    assert isinstance(testobj, attune.Instrument)
    return


if __name__ == "__main__":
    test_fromTopas4()

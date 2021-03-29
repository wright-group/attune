import math
import attune
import pytest
import json
from pathlib import Path

script_dir=Path(__file__).parent

def test_fromTopas4():
    testobj = attune.from_topas4(script_dir)
    
    assert isinstance(testobj, attune.Instrument)
    return



if __name__ == "__main__":
    test_fromTopas4()

__all__ = ["open"]

import json

from ._arrangement import Arrangement
from ._instrument import Instrument
from ._motor import Motor
from ._tune import Tune

open_ = open


def open(path):
    if hasattr(path, "read"):
        d = json.load(path)
    else:
        with open_(path, "r") as f:
            d = json.load(f)
    # arrangements
    arrangements = {}
    for arrangement_name in d["arrangements"].keys():
        tunes = {k: Tune(**v) for k, v in d["arrangements"][arrangement_name]["tunes"].items()}
        arrangements[arrangement_name] = Arrangement(name=arrangement_name, tunes=tunes)
    # motors
    motors = {k: Motor(**v) for k, v in d["motors"].items()}
    return Instrument(name=d["name"], arrangements=arrangements, motors=motors)

__all__ = ["open"]

import json

from ._arrangement import Arrangement
from ._instrument import Instrument
from ._setable import Setable
from ._transition import Transition
from ._tune import Tune

open_ = open


def open(path, *, load=False):
    """Open an instrument stored in a JSON file.

    Parameters
    ----------

    path: PathLike or FileLike
        The path to a file which contains an instrument
    load: datetime
        Allows this method to be used for loading by providing its associated store time
        Should generally be avoided when used directly

    Returns
    -------
    Instrument
        The instrument that was stored in the file
    """
    if hasattr(path, "read"):
        d = json.load(path)
    else:
        with open_(path, "r") as f:
            d = json.load(f)

    arrangements = {}
    for arrangement_name in d["arrangements"].keys():
        tunes = {k: Tune(**v) for k, v in d["arrangements"][arrangement_name]["tunes"].items()}
        arrangements[arrangement_name] = Arrangement(name=arrangement_name, tunes=tunes)

    setables = {k: Setable(**v) for k, v in d["setables"].items()}

    transition = Transition(**d["transition"])

    return Instrument(
        name=d["name"],
        arrangements=arrangements,
        setables=setables,
        transition=transition,
        load=load,
    )

__all__ = ["open"]

import json

from ._instrument import Instrument

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

    return Instrument(**d, load=load)

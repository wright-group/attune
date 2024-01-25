"""Define Attune version."""


# --- import --------------------------------------------------------------------------------------


import pathlib
import os


# ---- define -------------------------------------------------------------------------------------


here = pathlib.Path(__file__).resolve().parent


__all__ = ["__version__", "__branch__"]


# --- version -------------------------------------------------------------------------------------


# read from VERSION file
with open(here / "VERSION") as f:
    __version__ = f.read().strip()


# add git branch, if appropriate
p = here.parent / ".git" / "HEAD"
if os.path.isfile(p):
    with open(p) as f:
        __branch__ = f.readline().rstrip().split(r"/")[-1]
    if __branch__ != "master":
        __version__ += "+" + __branch__
else:
    __branch__ = None

import os
import pathlib
import shutil
import tempfile

import attune
import pytest

here = pathlib.Path(__file__).parent


def temp_store(func):
    def inner():
        with tempfile.TemporaryDirectory() as tdir:
            shutil.copytree(here / "example_store", tdir + "/example_store")
            os.environ["ATTUNE_STORE"] = tdir + "/example_store"
            func()

    return inner


@temp_store
def test_normal_load_store():
    instr = attune.load("test")
    assert instr.arrangements["arr"].ind_min == 0.25
    assert instr.arrangements["arr"].ind_max == 1.0
    instr = attune.map_ind_limits(instr, "arr", "tune", 0.25, 0.5)
    attune.store(instr)
    instr = attune.load("test")
    assert instr.arrangements["arr"].ind_min == 0.25
    assert instr.arrangements["arr"].ind_max == 0.5


@temp_store
def test_load_old():
    instr = attune.load("test", "2020-10-19T22:42:32.700+0000")
    assert instr.arrangements["arr"].ind_min == 0.0
    instr = attune.map_ind_limits(instr, "arr", "tune", 0.25, 0.5)
    attune.store(instr)
    instr = attune.load("test")
    assert instr.arrangements["arr"].ind_min == 0.25


@temp_store
def test_load_store():
    instr = attune.load("test")
    with pytest.warns(UserWarning, match="Attempted to store instrument equivalent"):
        attune.store(instr)

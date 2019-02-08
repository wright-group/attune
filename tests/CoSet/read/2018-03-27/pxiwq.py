import pathlib
import tempfile
from glob import glob

import pytest
import numpy as np

import attune


__here__ = pathlib.Path(__file__).parent


def test_is_instance():
    coset = attune.CoSet.read(__here__ / "test.coset")
    assert isinstance(coset, attune.CoSet)


def test_round_trip():
    coset = attune.CoSet.read(__here__ / "test.coset")
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        coset.save(save_directory=td)
        read_coset = attune.CoSet.read(next(td.glob("*.coset")))
        assert np.allclose(coset.setpoints, read_coset.setpoints)
        assert coset.dependent_names == read_coset.dependent_names
        for d1, d2 in zip(coset.dependents, read_coset.dependents):
            assert np.allclose(d1[:], d2[:])

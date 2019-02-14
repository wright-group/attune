import pathlib
import tempfile
from glob import glob

import pytest
import numpy as np

import attune


__here__ = pathlib.Path(__file__).parent


def test_is_instance():
    curve = attune.Curve.read(__here__ / "test.curve")
    assert isinstance(curve, attune.Curve)


def test_round_trip():
    curve = attune.Curve.read(__here__ / "test.curve")
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        curve.save(save_directory=td)
        read_curve = attune.Curve.read(next(td.glob("*.curve")))
        assert np.allclose(curve.setpoints[:], read_curve.setpoints[:])
        assert curve.dependent_names == read_curve.dependent_names
        for d1, d2 in zip(curve.dependents, read_curve.dependents):
            assert np.allclose(curve[d1][:], read_curve[d2][:])

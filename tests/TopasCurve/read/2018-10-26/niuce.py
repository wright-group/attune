import pathlib
import pytest
import attune
import tempfile
import numpy as np


__here__ = pathlib.Path(__file__).parent


def test_is_instance():
    paths = [
        __here__ / "OPA1 (10743) base - 2018-10-26 40490.crv",
        __here__ / "OPA1 (10743) mixer1 - 2018-09-07 66539.crv",
        __here__ / "OPA1 (10743) mixer2 - 2018-10-07 47923.crv",
        __here__ / "OPA1 (10743) mixer3 - 2013.06.01.crv",
    ]
    curve = attune.TopasCurve.read(paths, interaction_string="NON-NON-NON-Sig")
    assert isinstance(curve, attune.TopasCurve)


def test_round_trip():
    paths = [
        __here__ / "OPA1 (10743) base - 2018-10-26 40490.crv",
        __here__ / "OPA1 (10743) mixer1 - 2018-09-07 66539.crv",
        __here__ / "OPA1 (10743) mixer2 - 2018-10-07 47923.crv",
        __here__ / "OPA1 (10743) mixer3 - 2013.06.01.crv",
    ]
    curve = attune.TopasCurve.read(paths, interaction_string="NON-SH-NON-Sig")
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        paths = curve.save(save_directory=td)
        read_curve = attune.TopasCurve.read(paths, interaction_string="NON-SH-NON-Sig")
        assert np.allclose(curve.setpoints[:], read_curve.setpoints[:])
        assert curve.dependent_names == read_curve.dependent_names
        for d1, d2 in zip(curve.dependents, read_curve.dependents):
            assert np.allclose(curve[d1][:], read_curve[d2][:])


if __name__ == "__main__":
    test_is_instance()

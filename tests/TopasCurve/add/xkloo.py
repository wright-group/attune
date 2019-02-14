import pathlib
import pytest
import attune
import numpy as np


__here__ = pathlib.Path(__file__).parent


def test_add_differential():
    paths = [
        __here__ / "OPA1 (10743) base - 2018-10-26 40490.crv",
        __here__ / "OPA1 (10743) mixer1 - 2018-09-07 66539.crv",
        __here__ / "OPA1 (10743) mixer2 - 2018-10-07 47923.crv",
        __here__ / "OPA1 (10743) mixer3 - 2013.06.01.crv",
    ]
    curve = attune.TopasCurve.read(paths, kind="TOPAS-C", interaction_string="NON-NON-NON-Sig")

    d = attune.Dependent(np.ones(len(curve["Crystal_1"][:])), "Crystal_1", differential=True)
    s = curve.setpoints
    diff = attune.Curve(s, [d], "diff")

    c = curve + diff

    assert isinstance(c, attune.TopasCurve)
    assert np.allclose(curve["Crystal_1"][:], c["Crystal_1"][:] - 1)

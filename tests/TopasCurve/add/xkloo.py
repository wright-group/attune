import pathlib
import pytest
import attune
import numpy as np


__here__ = pathlib.Path(__file__).parent


@pytest.mark.xfail
def test_add_differential():
    paths = [
        __here__ / "OPA1 (10743) base - 2018-10-26 40490.crv",
        __here__ / "OPA1 (10743) mixer1 - 2018-09-07 66539.crv",
        __here__ / "OPA1 (10743) mixer2 - 2018-10-07 47923.crv",
        __here__ / "OPA1 (10743) mixer3 - 2013.06.01.crv",
    ]
    curve = attune.TopasCurve.read(paths, interaction_string="NON-NON-NON-Sig")

    d = attune.Dependent(np.ones(len(curve["0"][:])), "0", differential=True)
    s = curve.setpoints
    diff = attune.Curve(s, [d], "diff")

    c = curve + diff

    assert isinstance(c, attune.TopasCurve)
    assert np.allclose(curve["0"][:], c["0"][:] - 1)

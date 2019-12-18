import attune
import numpy as np
import pytest


def test_rename():
    d = attune.Dependent(np.linspace(0, 10, 21), "d1")
    s = attune.Setpoints(np.linspace(120, 240, 21), "s1")
    c = attune.Curve(s, d, "c")

    c.rename_dependent("d1", "d2")

    assert "d2" in c.dependents
    assert "d1" not in c.dependents
    assert np.allclose(c["d2"][:], d[:])
    assert c["d2"].name == "d2"


def test_rename_not_present():
    d = attune.Dependent(np.linspace(0, 10, 21), "d1")
    s = attune.Setpoints(np.linspace(120, 240, 21), "s1")
    c = attune.Curve(s, d, "c")

    with pytest.raises(ValueError):
        c.rename_dependent("d2", "d1")

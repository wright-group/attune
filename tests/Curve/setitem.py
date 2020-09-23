import attune
import numpy as np
import pytest


@pytest.mark.xfail
def test_set_new():
    d = attune.Dependent(np.linspace(0, 10, 21), "d1")
    s = attune.Setpoints(np.linspace(120, 240, 21), "s1")
    c = attune.Curve(s, d, "c")
    d = attune.Dependent(np.linspace(10, 100, 21), "d2")

    c["d3"] = d

    assert "d3" in c.dependents
    assert "d2" not in c.dependents
    assert np.allclose(c["d3"][:], d[:])
    assert c["d3"].name == "d3"


@pytest.mark.xfail
def test_set_incompatable():
    d = attune.Dependent(np.linspace(0, 10, 21), "d1")
    s = attune.Setpoints(np.linspace(120, 240, 21), "s1")
    c = attune.Curve(s, d, "c")
    d = attune.Dependent(np.linspace(10, 100, 25), "d2")

    with pytest.raises(ValueError):
        c["d3"] = d


@pytest.mark.xfail
def test_set_from_outside_curve():
    d = attune.Dependent(np.linspace(0, 10, 21), "d1")
    s = attune.Setpoints(np.linspace(120, 240, 21), "s1")
    c = attune.Curve(s, d, "c")
    d = attune.Dependent(np.linspace(10, 100, 30), "d2")
    s = attune.Setpoints(np.linspace(100, 250, 30), "s2")
    c2 = attune.Curve(s, d, "c")

    c["d3"] = c2["d2"]

    assert "d3" in c.dependents
    assert "d2" not in c.dependents
    assert np.allclose(c["d3"][:], d(c.setpoints[:]))
    assert c["d3"].name == "d3"

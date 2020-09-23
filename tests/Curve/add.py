import attune
import pytest

import numpy as np
import pathlib


@pytest.mark.xfail
def test_add_differential():
    d0 = attune.Dependent(np.linspace(-5, 5, 20), "d1", differential=True)
    d1 = attune.Dependent(np.linspace(-4, 0, 20), "d1", differential=True)
    s0 = attune.Setpoints(np.linspace(1300, 1400, 20), "s", "wn")
    s1 = attune.Setpoints(np.linspace(1300, 1400, 20), "s", "wn")
    c0 = attune.Curve(s0, [d0], "c1")
    c1 = attune.Curve(s1, [d1], "c1")

    sum_ = c0 + c1

    assert "d1" in sum_.dependents
    assert np.isclose(sum_["d1"][:].min(), -9)
    assert np.isclose(sum_["d1"][:].max(), 5)
    assert len(sum_["d1"][:]) == 20
    assert sum_["d1"].differential
    assert np.allclose(sum_.get_limits(), (1300, 1400))


@pytest.mark.xfail
def test_add_differential_units():
    d0 = attune.Dependent(np.linspace(-5, 5, 20), "d1", "mm_delay", differential=True)
    d1 = attune.Dependent(np.linspace(-4, 0, 20), "d1", "ps", differential=True)
    s0 = attune.Setpoints(np.linspace(1300, 1400, 20), "s", "wn")
    s1 = attune.Setpoints(np.linspace(1300, 1400, 20), "s", "wn")
    c0 = attune.Curve(s0, [d0], "c1")
    c1 = attune.Curve(s1, [d1], "c1")

    sum_ = c0 + c1

    assert "d1" in sum_.dependents
    assert np.isclose(sum_["d1"][:].min(), -5.599520383693045)
    assert np.isclose(sum_["d1"][:].max(), 5)
    assert len(sum_["d1"][:]) == 20
    assert sum_["d1"].differential
    assert sum_["d1"].units == "mm_delay"
    assert np.allclose(sum_.get_limits(), (1300, 1400))


@pytest.mark.xfail
def test_add_one_absolute():
    d0 = attune.Dependent(np.linspace(-5, 5, 20), "d1", differential=True)
    d1 = attune.Dependent(np.linspace(-4, 0, 20), "d1", differential=False)
    s0 = attune.Setpoints(np.linspace(1300, 1400, 20), "s", "wn")
    s1 = attune.Setpoints(np.linspace(1300, 1400, 20), "s", "wn")
    c0 = attune.Curve(s0, [d0], "c1")
    c1 = attune.Curve(s1, [d1], "c1")

    sum_ = c0 + c1

    assert "d1" in sum_.dependents
    assert np.isclose(sum_["d1"][:].min(), -9)
    assert np.isclose(sum_["d1"][:].max(), 5)
    assert len(sum_["d1"][:]) == 20
    assert not sum_["d1"].differential
    assert np.allclose(sum_.get_limits(), (1300, 1400))


@pytest.mark.xfail
def test_add_two_absolute():
    d0 = attune.Dependent(np.linspace(-5, 5, 20), "d1", differential=False)
    d1 = attune.Dependent(np.linspace(-4, 0, 20), "d1", differential=False)
    s0 = attune.Setpoints(np.linspace(1300, 1400, 20), "s", "wn")
    s1 = attune.Setpoints(np.linspace(1300, 1400, 20), "s", "wn")
    c0 = attune.Curve(s0, [d0], "c1")
    c1 = attune.Curve(s1, [d1], "c1")

    with pytest.raises(ValueError):
        sum_ = c0 + c1


@pytest.mark.xfail
def test_add_non_overlap():
    d0 = attune.Dependent(np.linspace(-5, 5, 20), "d1", differential=True)
    d1 = attune.Dependent(np.linspace(-4, 0, 20), "d1", differential=True)
    s0 = attune.Setpoints(np.linspace(1300, 1400, 20), "s", "wn")
    s1 = attune.Setpoints(np.linspace(1500, 1600, 20), "s", "wn")
    c0 = attune.Curve(s0, [d0], "c1")
    c1 = attune.Curve(s1, [d1], "c1")

    with pytest.raises(ValueError):
        sum_ = c0 + c1


@pytest.mark.xfail
def test_add_extra_deps():
    d0 = attune.Dependent(np.linspace(-5, 5, 20), "d1", differential=True)
    d2 = attune.Dependent(np.linspace(-5, 5, 20), "d2", differential=True)
    d1 = attune.Dependent(np.linspace(-4, 0, 20), "d1", differential=True)
    d3 = attune.Dependent(np.linspace(-4, 0, 20), "d3", differential=True)
    s0 = attune.Setpoints(np.linspace(1300, 1400, 20), "s", "wn")
    s1 = attune.Setpoints(np.linspace(1300, 1400, 20), "s", "wn")
    c0 = attune.Curve(s0, [d0, d2], "c1")
    c1 = attune.Curve(s1, [d1, d3], "c1")

    sum_ = c0 + c1

    assert "d1" in sum_.dependents
    assert "d2" in sum_.dependents
    assert "d3" in sum_.dependents
    assert np.allclose(sum_["d2"][:], c0["d2"][:])
    assert np.allclose(sum_["d3"][:], c1["d3"][:])
    assert np.isclose(sum_["d1"][:].min(), -9)
    assert np.isclose(sum_["d1"][:].max(), 5)
    assert len(sum_["d1"][:]) == 20
    assert sum_["d1"].differential
    assert np.allclose(sum_.get_limits(), (1300, 1400))


@pytest.mark.xfail
def test_add_different_inp_range():
    d0 = attune.Dependent(np.linspace(-5, 5, 20), "d1", differential=True)
    d1 = attune.Dependent(np.linspace(-4, 0, 25), "d1", differential=True)
    s0 = attune.Setpoints(np.linspace(1300, 1500, 20), "s", "wn")
    s1 = attune.Setpoints(np.linspace(1200, 1400, 25), "s", "wn")
    c0 = attune.Curve(s0, [d0], "c1")
    c1 = attune.Curve(s1, [d1], "c1")

    sum_ = c0 + c1

    assert "d1" in sum_.dependents
    assert len(sum_["d1"][:]) == 25
    assert sum_["d1"].differential
    assert np.allclose(sum_.get_limits(), (1300, 1400))

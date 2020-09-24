import attune
import numpy as np

import pytest


@pytest.mark.xfail
def test_offset_by():
    d0 = attune.Dependent(np.linspace(-5, 5, 20), "d1")
    s0 = attune.Setpoints(np.linspace(1300, 1400, 20), "s", "wn")
    c0 = attune.Curve(s0, [d0], "c1")
    c1 = c0.copy()

    c1.offset_by("d1", 1.0)

    np.testing.assert_allclose(c1["d1"][:], c0["d1"][:] + 1.0)
    np.testing.assert_allclose(c1.setpoints[:], c0.setpoints[:])


@pytest.mark.xfail
def test_offset_to():
    d0 = attune.Dependent(np.linspace(-5, 5, 20), "d1")
    s0 = attune.Setpoints(np.linspace(1300, 1400, 20), "s", "wn")
    c0 = attune.Curve(s0, [d0], "c1")
    c1 = c0.copy()

    c1.offset_to("d1", 1.0, 1300)

    np.testing.assert_allclose(c1["d1"][:], np.linspace(1, 11, 20))
    np.testing.assert_allclose(c1.setpoints[:], c0.setpoints[:])

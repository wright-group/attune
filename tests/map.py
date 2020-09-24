import attune
import numpy as np

import pytest


def test_map_ind_points():
    tune = attune.Tune(np.linspace(1300, 1400, 20), np.linspace(-5, 5, 20))
    arr = attune.Arrangement("test_map", {"test": tune})
    inst0 = attune.Instrument({"test_map": arr}, {"test": attune.Motor("tune")})

    inst1 = attune.map_ind_points(inst0, "test_map", "test", np.linspace(1310, 1450, 25))

    test_points = np.linspace(1310, 1400, 14)
    np.testing.assert_allclose(
        inst1["test_map"]["test"](test_points), inst0["test_map"]["test"](test_points)
    )
    assert len(inst1["test_map"]["test"]) == 25


def test_map_ind_limits():
    tune = attune.Tune(np.linspace(1300, 1400, 20), np.linspace(-5, 5, 20))
    arr = attune.Arrangement("test_map", {"test": tune})
    inst0 = attune.Instrument({"test_map": arr}, {"test": attune.Motor("tune")})

    inst1 = attune.map_ind_limits(inst0, "test_map", "test", 1310, 1450)

    test_points = np.linspace(1310, 1400, 14)
    np.testing.assert_allclose(
        inst1["test_map"]["test"](test_points), inst0["test_map"]["test"](test_points)
    )
    assert len(inst1["test_map"]["test"]) == len(inst0["test_map"]["test"])

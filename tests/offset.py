import attune
import numpy as np

import pytest


def test_offset_by():
    tune = attune.Tune(np.linspace(1300, 1400, 20), np.linspace(-5, 5, 20))
    arr = attune.Arrangement("test_offset", {"test": tune})
    inst0 = attune.Instrument({"test_offset": arr}, {"test": attune.Setable("tune")})

    inst1 = attune.offset_by(inst0, "test_offset", "test", 1.0)

    np.testing.assert_allclose(
        inst1["test_offset"]["test"].dependent, inst0["test_offset"]["test"].dependent + 1.0
    )
    np.testing.assert_allclose(
        inst1["test_offset"]["test"].independent, inst0["test_offset"]["test"].independent
    )


def test_offset_to():
    tune = attune.Tune(np.linspace(1300, 1400, 20), np.linspace(-5, 5, 20))
    arr = attune.Arrangement("test_offset", {"test": tune})
    inst0 = attune.Instrument({"test_offset": arr}, {"test": attune.Setable("tune")})

    inst1 = attune.offset_to(inst0, "test_offset", "test", 1.0, 1300)

    np.testing.assert_allclose(inst1["test_offset"]["test"].dependent, np.linspace(1, 11, 20))
    np.testing.assert_allclose(
        inst1["test_offset"]["test"].independent, inst0["test_offset"]["test"].independent
    )

import math

import attune
import pytest


def test_overlap():
    tune = attune.Tune([0, 1], [0, 1])
    tune1 = attune.Tune([0.5, 1.5], [0, 1])
    first = attune.Arrangement("first", {"tune": tune})
    second = attune.Arrangement("second", {"tune": tune1})
    inst = attune.Instrument({"first": first, "second": second}, {"tune": attune.Setable("tune")})
    # first
    assert math.isclose(inst(0.25)["tune"], 0.25)
    # second
    assert math.isclose(inst(1.25)["tune"], 0.75)
    # overlap unspecified
    with pytest.raises(ValueError):
        inst(0.75)
    # overlap first
    assert math.isclose(inst(0.75, "first")["tune"], 0.75)
    # overlap second
    assert math.isclose(inst(0.75, "second")["tune"], 0.25)


def test_nested():
    tune = attune.Tune([0, 1], [0, 1])
    tune1 = attune.Tune([0.5, 1.5], [0, 1])
    first = attune.Arrangement("first", {"tune": tune})
    second = attune.Arrangement("second", {"first": tune1})
    inst = attune.Instrument({"first": first, "second": second}, {"tune": attune.Setable("tune")})
    assert math.isclose(inst(0.75, "second")["tune"], 0.25)

import attune
import numpy as np

import pytest


def test_equality():
    x1 = np.linspace(0, 1, 5)
    y1 = np.linspace(3, 5, 5)
    t1 = attune.Tune(x1, y1)
    t2 = attune.Tune(x1, y1 + 0.1)
    t3 = attune.Tune(x1[:-1], y1[:-1])

    assert t1 == t1
    assert t1 != t2
    assert t1 != t3

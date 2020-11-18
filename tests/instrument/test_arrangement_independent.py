import attune
import pytest
import numpy as np


def test_basic():
    a = attune.Tune(independent=[0, 1], dependent=[0, 1])
    b = attune.Tune(independent=[0, 0.5, 1], dependent=[0, 0.5, 1])
    arrangement = attune.Arrangement(name="test", tunes={"a": a, "b": b})
    assert np.allclose(arrangement.independent, np.array([0, 0.5, 1]))


def test_different_ranges():
    a = attune.Tune(independent=[-1, -0.5, 0, 0.5, 1], dependent=[0] * 5)
    b = attune.Tune(independent=[-0.5, -0.25, 0, 0.25, 0.5], dependent=[0] * 5)
    arrangement = attune.Arrangement(name="test", tunes={"a": a, "b": b})
    assert np.allclose(arrangement.independent, np.array([-0.5, -0.25, 0, 0.25, 0.5]))


def test_close():
    a = attune.Tune(independent=[0, 0.5, 1], dependent=[0, 0.5, 1])
    b = attune.Tune(independent=[0, 0.5001, 1], dependent=[0, 0.5, 1])
    arrangement = attune.Arrangement(name="test", tunes={"a": a, "b": b})
    assert np.allclose(arrangement.independent, np.array([0, 0.5, 1]))


if __name__ == "__main__":
    test_basic()
    test_different_ranges()
    test_close()

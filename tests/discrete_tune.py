import attune
import numpy as np


def test_discrete():
    dt = attune.DiscreteTune({"hi": (100, 200), "lo": (10, 20), "med": (20, 100)}, default="def")
    x = [150, 20, 15, 100, 70, 5, 500]
    y = ["hi", "lo", "lo", "hi", "med", "def", "def"]
    assert dt(x) == np.asarray(y)
    for xi, yi in zip(x,y):
        assert dt(xi).item() == yi

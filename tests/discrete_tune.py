import attune


def test_discrete():
    dt = attune.DiscreteTune({"hi": (100, 200), "lo": (10, 20), "med": (20, 100)}, default="def")
    assert dt(150) == "hi"
    assert dt(20) == "lo"
    assert dt(15) == "lo"
    assert dt(100) == "hi"
    assert dt(70) == "med"
    assert dt(5) == "def"
    assert dt(500) == "def"

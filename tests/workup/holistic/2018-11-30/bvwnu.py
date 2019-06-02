import tempfile
import attune
import WrightTools as wt
import numpy as np
import pathlib


__here__ = pathlib.Path(__file__).parent


def test_tune_test():
    d = wt.open(__here__ / "data.wt5")
    print(d, d.shape)


if __name__ == '__main__':
    test_tune_test()

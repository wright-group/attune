import pathlib
import pytest
import attune


__here__ = pathlib.Path(__file__).parent


def test_is_instance():
    paths = [
        __here__ / "OPA1 (10743) base - 2018-10-26 40490.crv",
        __here__ / "OPA1 (10743) mixer1 - 2018-09-07 66539.crv",
        __here__ / "OPA1 (10743) mixer2 - 2018-10-07 47923.crv",
        __here__ / "OPA1 (10743) mixer3 - 2013.06.01.crv",
    ]
    curve = attune.TopasCurve.read(paths, kind="TOPAS-C", interaction_string="NON-NON-NON-Sig")
    assert isinstance(curve, attune.TopasCurve)


if __name__ == "__main__":
    test_is_instance()

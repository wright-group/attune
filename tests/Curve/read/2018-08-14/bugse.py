import pathlib
import pytest
import attune


__here__ = pathlib.Path(__file__).parent


def test_is_instance():
    curve = attune.Curve.read(__here__ / 'test.curve')
    assert isinstance(curve, attune.Curve)

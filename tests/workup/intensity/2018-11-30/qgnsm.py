import attune
import pathlib
import pytest
import WrightTools as wt


__here__ = pathlib.Path(__file__).parent


def test():
    data = wt.open(__here__ / 'data.wt5')
    old = attune.TopasCurve.read([__here__ / 'old.crv' , None, None, None],
                                 kind='TOPAS-C',
                                 interaction_string='NON-NON-NON-Sig')
    new = attune.workup.intensity(data, old, 0)
    print(new)


if __name__ == '__main__':
    test()

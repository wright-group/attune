import attune
import pathlib
import pytest

import numpy as np
import WrightTools as wt


__here__ = pathlib.Path(__file__).parent


def test():
    data = wt.open(__here__ / "data.wt5")
    data.print_tree()
    data.transform("w1=wm", "w1_Delay_2", "wa_points")
    data.moment("wa_points", moment=0)
    data.transform("w1=wm", "w1_Delay_2_points")
    old = attune.TopasCurve.read([__here__ / "old.crv"], interaction_string="NON-NON-NON-Sig")
    new = attune.workup.intensity(data, -1, "3", autosave=False, curve=old)
    print(new)


def test_ltol_with_gtol():
    data = wt.open(__here__ / "data.wt5")
    data.print_tree()
    data.transform("w1=wm", "w1_Delay_2", "wa_points")
    data.moment("wa_points", moment=0)
    data.transform("w1=wm", "w1_Delay_2_points")
    old = attune.TopasCurve.read([__here__ / "old.crv"], interaction_string="NON-NON-NON-Sig")
    new = attune.workup.intensity(
        data, -1, "3", gtol=0.1, ltol=0.99999, spline=False, autosave=False, curve=old
    )
    correct = attune.TopasCurve.read(
        [__here__ / "gtol_ltol.crv"], interaction_string="NON-NON-NON-Sig"
    )
    correct.convert("wn")
    assert np.allclose(new["3"][::-1], correct["3"][:])


if __name__ == "__main__":
    test()
    test_ltol_with_gtol()

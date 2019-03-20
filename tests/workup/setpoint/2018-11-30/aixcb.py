import attune
import pathlib
import pytest
import WrightTools as wt

import matplotlib.pyplot as plt


__here__ = pathlib.Path(__file__).parent


def test():
    global data, old
    data = wt.open(__here__ / "data.wt5")
    data.convert("wn", convert_variables=True)
    data.print_tree()
    data.transform("w1=wm", "w1_Crystal_2_points", "wa-w1")
    data.level(0,2,5)
    wt.artists.interact2D(data, "w1__e__wm", "wa__m__w1")
    data.transform("w1=wm", "w1_Crystal_2_points", "wa")
    data.moment("wa", moment=1, resultant=wt.kit.joint_shape(data.w1, data.w1_Crystal_2))
    data.transform("w1=wm", "w1_Crystal_2_points")
    data.channels[-1].clip(min=data.w1.min()-1000, max=data.w1.max()+1000)
    data.channels[-1].null = data.wa.min()
    wt.artists.quick2D(data, channel=-1)
    old = attune.TopasCurve.read(
        [__here__ / "old.crv"],
        interaction_string="NON-NON-NON-Sig",
    )
    new = attune.workup.setpoint(data, -1, "2", curve=old)
    print(new)


if __name__ == "__main__":
    test()

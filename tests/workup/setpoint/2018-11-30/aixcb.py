import attune
import pathlib
import pytest
import WrightTools as wt


__here__ = pathlib.Path(__file__).parent


def test():
    data = wt.open(__here__ / "data.wt5")
    data.print_tree()
    data.transform("w1=wm", "w1_Crystal_2", "wa")
    data.moment("wa", moment=0, resultant=wt.kit.joint_shape(data.w1, data.w1_Crystal_2))
    data.transform("w1=wm", "w1_Crystal_2")
    old = attune.TopasCurve.read(
        [__here__ / "old.crv"],
        interaction_string="NON-NON-NON-Sig",
    )
    new = attune.workup.intensity(setpoint, -1, "3", curve=old)
    print(new)


if __name__ == "__main__":
    test()

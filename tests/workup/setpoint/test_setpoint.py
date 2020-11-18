import attune
import pathlib
import WrightTools as wt

import matplotlib.pyplot as plt


__here__ = pathlib.Path(__file__).parent


def test():
    data = wt.open(__here__ / "data.wt5")

    data.transform("w1=wm", "w1_Crystal_2_points", "wa-w1")
    data.level(0, 2, 5)
    data.array_signal.clip(min=0)
    data.transform("w1=wm", "w1_Crystal_2_points", "wa")
    data.moment("wa", moment=1, resultant=wt.kit.joint_shape(data.w1, data.w1_Crystal_2))
    data.transform("w1=wm", "w1_Crystal_2_points")
    data.channels[-1].clip(min=data.w1.min() - 1000, max=data.w1.max() + 1000)
    data.channels[-1].null = data.wa.min()

    old = attune.open(__here__ / "old_instr.json")
    reference = attune.open(__here__ / "ref_instr.json")

    new = attune.setpoint(data, -1, "sig", "c2", autosave=False, instrument=old)
    assert new == reference


if __name__ == "__main__":
    test()

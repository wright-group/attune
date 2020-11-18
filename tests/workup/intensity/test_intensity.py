import attune
import pathlib

import numpy as np
import WrightTools as wt


__here__ = pathlib.Path(__file__).parent


def test():
    data = wt.open(__here__ / "data.wt5")
    data.transform("w1=wm", "w1_Delay_2", "wa_points")
    data.moment("wa_points", moment=0)
    data.transform("w1=wm", "w1_Delay_2_points")
    old = attune.open(__here__ / "input_instr.json")
    new = attune.intensity(
        data=data, channel=-1, arrangement="sig", tune="d2", instrument=old, autosave=False
    )


def test_ltol_with_gtol():
    data = wt.open(__here__ / "data.wt5")
    data.print_tree()
    data.transform("w1=wm", "w1_Delay_2", "wa_points")
    data.moment("wa_points", moment=0)
    data.transform("w1=wm", "w1_Delay_2_points")
    old = attune.open(__here__ / "input_instr.json")
    new = attune.intensity(
        data=data,
        channel=-1,
        arrangement="sig",
        tune="d2",
        gtol=0.1,
        ltol=0.99999,
        spline=False,
        autosave=False,
        instrument=old,
    )
    correct = attune.open(__here__ / "gtol_ltol_instr.json")
    assert np.allclose(new["sig"]["d2"].dependent, correct["sig"]["d2"].dependent, atol=0.01)
    assert np.allclose(new["sig"]["d2"].independent, correct["sig"]["d2"].independent)


if __name__ == "__main__":
    test()
    test_ltol_with_gtol()

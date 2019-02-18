import attune
import pathlib
import pytest
import WrightTools as wt


__here__ = pathlib.Path(__file__).parent


def test():
    data = wt.open(__here__ / "data.wt5")
    data.print_tree()
    data.transform("w1=wm", "w1_Delay_2", "wa_points")
    data.moment("wa_points", moment=0)
    data.transform("w1=wm", "w1_Delay_2_points")
    old = attune.TopasCurve.read(
        [__here__ / "old.crv", None, None, None],
        kind="TOPAS-C",
        interaction_string="NON-NON-NON-Sig",
    )
    new = attune.workup.intensity(data, -1, "Delay_2", curve=old)
    print(new)


if __name__ == "__main__":
    test()

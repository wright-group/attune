import attune
import WrightTools as wt
import numpy as np
import pathlib


__here__ = pathlib.Path(__file__).parent


def test_tune_test():
    d = wt.open(__here__ / "tunetest.wt5")
    instr = attune.open(__here__ / "instrument_in.json")
    d.transform("w3", "wm-w3")
    out = attune.tune_test(
        data=d, channel="signal_mean", arrangement="sfs", instrument=instr, autosave=False
    )

    correct_out = attune.open(__here__ / "instrument_out.json")

    for tune, correct in zip(out["sfs"].values(), correct_out["sfs"].values()):
        assert np.allclose(tune.dependent, correct.dependent, atol=0.01)
        assert np.allclose(tune.independent, correct.independent, atol=0.01)

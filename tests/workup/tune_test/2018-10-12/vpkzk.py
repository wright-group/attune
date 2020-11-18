import tempfile
import attune
import WrightTools as wt
import numpy as np
import pathlib

import pytest

__here__ = pathlib.Path(__file__).parent


@pytest.mark.xfail
def test_tune_test():
    d = wt.open(__here__ / "tunetest.wt5")
    instr = attune.open(__here__ / "instrument_in.json")
    d.transform("w3", "w3-wm")
    out = attune.tune_test(d, "signal_mean", "sfs", instr, autosave=False)

    # out = attune.Curve.read(__here__ / "out.curve")

    # assert np.allclose(out_tt.setpoints[:], out.setpoints[:])
    # for d in out.dependents:
    #    assert np.allclose(out_tt[d][:], out[d][:], atol=0.01)

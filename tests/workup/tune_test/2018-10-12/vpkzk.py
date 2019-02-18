import tempfile
import attune
import WrightTools as wt
import numpy as np
import pathlib

__here__ = pathlib.Path(__file__).parent

def test_tune_test():
    d = wt.open(__here__ / "tunetest.wt5")
    c = attune.Curve.read(__here__ / "in.curve")
    d.transform("w3", "wm_points")
    d.wm_points.units = d.wm.units
    d.print_tree()
    #out_int = attune.workup.intensity(d, c, "signal_mean")
    with tempfile.TemporaryDirectory() as td:
        out_tt = attune.workup.tune_test(d, "signal_mean", c, save_directory=td)

    out = attune.Curve.read(__here__ / "out.curve")

    assert np.allclose(out_tt.setpoints[:], out.setpoints[:])
    for d in out.dependents:
        assert np.allclose(out_tt[d][:], out[d][:])
    

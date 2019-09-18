import matplotlib
matplotlib.use("TkAgg")

import tempfile
import attune
import WrightTools as wt
import numpy as np
import pathlib


__here__ = pathlib.Path(__file__).parent


def test_holistic():
    # collect
    d = wt.open(__here__ / "data.wt5")

    curve_paths = [__here__ / "old" / "OPA1 (10743) base - 2018-10-26 40490.crv"]
    old = attune.TopasCurve.read(curve_paths, interaction_string='NON-NON-NON-Sig')

    curve_paths = [__here__ / "out" / "OPA- 2019-09-18 53345.crv"]
    reference = attune.TopasCurve.read(curve_paths, interaction_string='NON-NON-NON-Sig')

    # do calculation
    d.transform("w1_Crystal_1", "w1_Delay_1", "wa")
    new = attune.workup.holistic(d, "array_signal", ["0", "1"], old, gtol=.05, level=True, autosave=False, save_directory=__here__/"out")

    # check
    for r, n in zip(reference.dependents.values(), new.dependents.values()):
        print(r[:].dtype, n[:].dtype)
        np.testing.assert_allclose(r[:], n[:], rtol=0.01)

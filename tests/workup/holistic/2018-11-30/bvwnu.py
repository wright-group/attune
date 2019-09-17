import matplotlib
matplotlib.use("TkAgg")

import tempfile
import attune
import WrightTools as wt
import numpy as np
import pathlib


__here__ = pathlib.Path(__file__).parent


# collect
d = wt.open(__here__ / "data.wt5")
curve_paths = [__here__ / "old" / "OPA1 (10743) base - 2018-10-26 40490.crv",
                __here__ / "old" / "OPA1 (10743) mixer1 - 2018-09-07 66539.crv",
                __here__ / "old" / "OPA1 (10743) mixer2 - 2018-10-07 47923.crv",
                __here__ / "old" / "OPA1 (10743) mixer3 - 2013.06.01.crv",
                ]
old = attune.TopasCurve.read(curve_paths, interaction_string='NON-NON-NON-Sig')
# do calculation
d.transform("w1_Crystal_1", "w1_Delay_1", "wa")
new = attune.workup.holistic(d, "array_signal", [], old, gtol=.000, level=True)
# check

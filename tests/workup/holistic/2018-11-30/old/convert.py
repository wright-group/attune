import attune
import numpy as np


arr = np.genfromtxt("./OPA1 (10743) base - 2018-10-26 40490.crv").T

independent = arr[1]

c1 = attune.Tune(independent=independent, dependent=arr[3])
d1 = attune.Tune(independent=independent, dependent=arr[4])
c2 = attune.Tune(independent=independent, dependent=arr[5])
d2 = attune.Tune(independent=independent, dependent=arr[6])

arrangement = attune.Arrangement(
    tunes={"c1": c1, "d1": d1, "c2": c2, "d2": d2}, name="NON-NON-NON-Sig"
)

instrument = attune.Instrument(
    name="old", arrangements={"NON-NON-NON-Sig": arrangement}, setables={}
)

with open("out.json", "w") as f:
    instrument.save(f)

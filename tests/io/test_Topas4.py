import math
import attune
import pytest
import json
from pathlib import Path
from attune import Tune, DiscreteTune
import numpy as np

test_dir = Path(__file__).parent / "twin_test_data"


def test_from_topas4():
    instr = attune.from_topas4(test_dir)

    TOTAL_ARRANGEMENTS = 3
    TOTAL_MINS_MAXES = 7
    MIN_DEPS_REF = [
        2.230625,
        -2.2662695266462407,
        2.44375,
        0.29442646838236897,
        2500.0,
        1640.7,
        145.44583333333333,
    ]
    MIN_INDEPS_REF = [1300.0, 1300.0, 1300.0, 1300.0, 1757.493188010899, 4000.0, 4000.0]
    MAX_DEPS_REF = [
        4.9759375,
        8.030085499389287,
        2.65625,
        -26.225919814858464,
        1300.0,
        1952.081,
        124.17083333333333,
    ]
    MAX_INDEPS_REF = [2500.0, 2500.0, 2500.0, 2500.0, 5005.9701492537315, 18000.0, 18000.0]

    arrangements = {"SIG", "IDL", "DFG-SIG"}

    assert isinstance(instr, attune.Instrument)

    min_deps = []
    min_indeps = []
    max_deps = []
    max_indeps = []

    assert set(instr.arrangements.keys()) == arrangements

    for key in instr.arrangements:
        for tune in instr.arrangements[key].tunes.values():
            if isinstance(tune, Tune):
                min_deps.append(tune.dependent[0])
                min_indeps.append(tune.independent[0])
                max_deps.append(tune.dependent[-1])
                max_indeps.append(tune.independent[-1])

    assert len(min_deps) == TOTAL_MINS_MAXES
    assert len(min_indeps) == TOTAL_MINS_MAXES
    assert len(max_deps) == TOTAL_MINS_MAXES
    assert len(max_indeps) == TOTAL_MINS_MAXES

    for i in range(len(min_deps)):
        assert np.isclose(min_deps[i], MIN_DEPS_REF[i])
        assert np.isclose(min_indeps[i], MIN_INDEPS_REF[i])
        assert np.isclose(max_deps[i], MAX_DEPS_REF[i])
        assert np.isclose(max_indeps[i], MAX_INDEPS_REF[i])

    assert isinstance(instr["DFG-SIG"]["RP Stage"], DiscreteTune)
    assert instr(10000)["RP Stage"] == "IN"


if __name__ == "__main__":
    test_from_topas4()

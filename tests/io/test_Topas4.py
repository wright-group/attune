import math
import attune
import pytest
import json
from pathlib import Path

script_dir = Path(__file__).parent


def test_from_topas4():
    testobj = attune.from_topas4(script_dir)

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

    assert isinstance(testobj, attune.Instrument)

    instr = testobj.as_dict()

    min_deps = []
    min_indeps = []
    max_deps = []
    max_indeps = []

    length_arrange = len(instr["arrangements"])
    assert length_arrange == TOTAL_ARRANGEMENTS

    for key in instr["arrangements"]:
        for tune in instr["arrangements"][key]["tunes"].values():
            lentune = len(tune["independent"])

            min_deps.append(tune["dependent"][0])
            min_indeps.append(tune["independent"][0])
            max_deps.append(tune["dependent"][lentune - 1])
            max_indeps.append(tune["independent"][lentune - 1])

    assert len(min_deps) == TOTAL_MINS_MAXES
    assert len(min_indeps) == TOTAL_MINS_MAXES
    assert len(max_deps) == TOTAL_MINS_MAXES
    assert len(max_indeps) == TOTAL_MINS_MAXES

    for i in range(len(min_deps)):
        assert min_deps[i] == MIN_DEPS_REF[i]
        assert min_indeps[i] == MIN_INDEPS_REF[i]
        assert max_deps[i] == MAX_DEPS_REF[i]
        assert max_indeps[i] == MAX_INDEPS_REF[i]

    return


if __name__ == "__main__":
    test_from_topas4()

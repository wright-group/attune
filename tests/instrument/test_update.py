import math
import tempfile

import attune


def test_update_new_tune():
    tune = attune.Tune([0, 1], [0, 1])
    discrete_tune = attune.DiscreteTune({"hi": (0.8, 1.0), "lo": (0.1, 0.2)}, default="med")
    arr = attune.Arrangement("arr", {"tune": tune, "discrete": discrete_tune})
    inst = attune.Instrument(
        {"arr": arr}, {"tune": attune.Setable("tune"), "discrete": attune.Setable("discrete")}
    )
    arr_new = attune.Arrangement("arr", {"tune_new": tune})
    inst2 = attune.Instrument({"arr": arr_new}, {"tune_new": attune.Setable("tune_new")})
    inst_new = attune.update_merge(inst, inst2)
    assert math.isclose(inst_new(0.5)["tune"], 0.5)
    assert math.isclose(inst_new(0.5)["tune_new"], 0.5)
    assert inst_new.transition.type == "update_merge"


def test_update_new_arrangement():
    tune = attune.Tune([0, 1], [0, 1])
    discrete_tune = attune.DiscreteTune({"hi": (0.8, 1.0), "lo": (0.1, 0.2)}, default="med")
    arr = attune.Arrangement("arr", {"tune": tune, "discrete": discrete_tune})
    inst = attune.Instrument(
        {"arr": arr}, {"tune": attune.Setable("tune"), "discrete": attune.Setable("discrete")}
    )
    arr_new = attune.Arrangement("arr_new", {"tune_new": tune})
    inst2 = attune.Instrument({"arr_new": arr_new}, {"tune_new": attune.Setable("tune_new")})
    inst_new = attune.update_merge(inst, inst2)
    assert math.isclose(inst_new(0.5, "arr")["tune"], 0.5)
    assert math.isclose(inst_new(0.5, "arr_new")["tune_new"], 0.5)
    assert inst_new.transition.type == "update_merge"


def test_update_existing():
    tune = attune.Tune([0, 1], [0, 1])
    discrete_tune = attune.DiscreteTune({"hi": (0.8, 1.0), "lo": (0.1, 0.2)}, default="med")
    arr = attune.Arrangement("arr", {"tune": tune, "discrete": discrete_tune})
    inst = attune.Instrument(
        {"arr": arr}, {"tune": attune.Setable("tune"), "discrete": attune.Setable("discrete")}
    )
    tune = attune.Tune([0, 1], [1, 2])
    arr_new = attune.Arrangement("arr", {"tune": tune})
    inst2 = attune.Instrument({"arr": arr_new}, {"tune": attune.Setable("tune")})
    inst_new = attune.update_merge(inst, inst2)
    assert math.isclose(inst_new(0.5)["tune"], 1.5)
    assert inst_new(0.5)["discrete"] == "med"
    assert inst_new.transition.type == "update_merge"


if __name__ == "__main__":
    test_construct_simple()
    test_asdict_smoke()

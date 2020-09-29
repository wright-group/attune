import math
import tempfile

import attune


def test_construct_simple():
    tune = attune.Tune([0, 1], [0, 1])
    arr = attune.Arrangement("arr", {"tune": tune})
    inst = attune.Instrument({"arr": arr}, {"tune": attune.Setable("tune")})
    assert math.isclose(inst(0.5)["tune"], 0.5)
    with tempfile.TemporaryFile("w+t", suffix=".json") as tmp:
        inst.save(tmp)
        tmp.seek(0)
        reopened = attune.open(tmp)
        assert inst == reopened


def test_asdict_smoke():
    tune = attune.Tune([0, 1], [0, 1])
    arr = attune.Arrangement("arr", {"tune": tune})
    inst = attune.Instrument({"arr": arr}, {"tune": attune.Setable("tune")})
    print(inst.as_dict())


if __name__ == "__main__":
    test_construct_simple()
    test_asdict_smoke()

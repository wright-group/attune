import attune


def test_rename():
    i = attune.Instrument({}, name="old")
    new = attune.rename(i, "new")
    assert new.name == "new"
    assert new.transition.metadata["old_name"] == "old"

__all__ = ["load", "store"]


import appdirs
import json
import pathlib
import maya


def load(name, time):
    pass


def store(instrument, *, transaction=None, data=None, old=None):
    # make datadir
    datadir = pathlib.Path(appdirs.user_data_dir("attune", "attune"))
    datadir /= instrument.name
    datadir /= instrument.datetime.strftime("%Y%m%dT%H%M%S%z")
    assert not datadir.exists()
    datadir.mkdir(parents=True, exist_ok=True)
    # store instrument
    with open(datadir / "instrument.json", "w") as f:
        instrument.save(f)
        f.write("\n")
    # store transaction
    if transaction is None:
        transaction = {"type": "store"}
    assert "type" in transaction
    with open(datadir / "transaction.json", "w") as f:
        json.dump(transaction, f)
        f.write("\n")
    # store data
    if data is not None:
        data.save(datadir / "data.wt5")
    # store old instrument
    if old is not None:
        with open(datadir / "old_instrument.json", "w") as f:
            old.save(f)

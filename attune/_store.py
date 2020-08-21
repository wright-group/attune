__all__ = ["load", "restore", "redo", "store", "undo"]


import appdirs
import attune
from datetime import datetime
import json
import pathlib
import maya


def load(name, time=None):
    if time is None:
        time = datetime.utcnow()
    if hasattr(time, "datetime"):
        time = time.datetime()

    def find(name, time):
        iso8061 = time.strftime("%Y%m%dT%H%M%S%z")
        year = time.year
        month = time.month

        while True:
            datadir = pathlib.Path(appdirs.user_data_dir("attune", "attune"))
            datadir /= name
            datadir /= str(year)
            datadir /= str(month).zfill(2)
            if datadir.exists():
                for d in sorted(datadir.iterdir(), reverse=True):
                    if d.name <= iso8061:
                        return datadir / d.name
            if month == 1:
                year -= 1
                month = 12
            else:
                month -= 1
            continue

    datadir = find(name, time)
    return attune.open(datadir / "instrument.json")


def restore(instrument, time):
    raise NotImplementedError


def redo(instrument):
    raise NotImplementedError


def store(instrument, *, transaction=None, data=None, old=None):
    now = datetime.utcnow()
    # make datadir
    datadir = pathlib.Path(appdirs.user_data_dir("attune", "attune"))
    datadir /= instrument.name
    datadir /= now.strftime("%Y")
    datadir /= now.strftime("%m")
    datadir /= now.strftime("%Y%m%dT%H%M%S%z")
    datadir.mkdir(parents=True)
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


def undo(instrument):
    raise NotImplementedError

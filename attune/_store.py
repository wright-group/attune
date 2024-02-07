"""Tools to interact with the attune store."""

__all__ = ["catalog", "load", "restore", "store", "undo", "print_history", "WalkHistory"]


from datetime import datetime, timedelta, timezone
from dateparser import parse
import pathlib
import os
import warnings

import appdirs
import dateutil

from ._transition import Transition, TransitionType
from ._open import open as open_


def catalog(full=False):
    """Access a catalog of instruments.

    By default returns a list of keys available.
    If full is True, loads each instrument as a dictionary of keys to Instrument objects.
    """
    if "ATTUNE_STORE" in os.environ and os.environ["ATTUNE_STORE"]:
        attune_dir = pathlib.Path(os.environ["ATTUNE_STORE"])
    else:
        attune_dir = pathlib.Path(appdirs.user_data_dir("attune", "attune"))
    instrument_names = os.listdir(attune_dir)
    if full:
        return {name: load(name) for name in instrument_names}
    else:
        return instrument_names


def load(name: str, time=None, reverse: bool = True):
    """Load an istrument of the given name.

    Parameters
    ----------
    name: str
        The key of the instrument to load
    time: str, datetime, optional
        The time for which to load the instrument.
        Allows loading previous instruments in the catalog.
        Allows for some natural language descriptions e.g. "5 minutes ago".
        By default uses the current timestamp.
    reverse: boolean, optional
        Direction to search, by default looks for a previous curve.
        If given as False, looks forward in time from the given timestamp.
    """
    if isinstance(time, str):
        time = parse(
            time,
            settings=dict(
                TIMEZONE="UTC",
                PREFER_DATES_FROM="current_period",
                TO_TIMEZONE="UTC",
                RETURN_AS_TIMEZONE_AWARE=True,
            ),
        )
        if time is None:
            raise ValueError("invalid datetime")
    if time is None:
        time = datetime.now(timezone.utc)
    if hasattr(time, "datetime"):
        time = time.datetime()

    def find(name, time, reverse):
        year = time.year
        month = time.month

        if "ATTUNE_STORE" in os.environ and os.environ["ATTUNE_STORE"]:
            attune_dir = pathlib.Path(os.environ["ATTUNE_STORE"])
        else:
            attune_dir = pathlib.Path(appdirs.user_data_dir("attune", "attune"))

        if not (attune_dir / name).exists():
            raise ValueError(f"No instrument found with name '{name}'")

        while True:
            datadir = attune_dir
            datadir /= name
            datadir /= str(year)
            datadir /= f"{month:02}"
            if datadir.exists():
                for d in sorted(
                    datadir.iterdir(),
                    key=lambda x: dateutil.parser.isoparse(x.name),
                    reverse=reverse,
                ):
                    if reverse:
                        if dateutil.parser.isoparse(d.name) <= time:
                            return datadir / d.name
                    else:
                        if dateutil.parser.isoparse(d.name) >= time:
                            return datadir / d.name

            if reverse:
                if month == 1:
                    year -= 1
                    month = 12
                else:
                    month -= 1
                if year < 1960:
                    raise ValueError(
                        f"Could not find an instrument earlier than {time}. Looked back all the way to the invention of the laser"
                    )
            else:
                if month == 12:
                    month = 1
                    year += 1
                else:
                    month += 1
                if year > datetime.now().year + 20:
                    raise ValueError(f"Could not find an instrument later than {time}.")

    datadir = find(name, time, reverse)
    return open_(datadir / "instrument.json", load=dateutil.parser.isoparse(datadir.name))


def restore(name, time, reverse=True):
    """Restore a previously applied instrument.


    Parameters
    ----------
    name: str
        The key of the instrument to load
    time: str, datetime
        The time for which to load the instrument.
        Allows loading previous instruments in the catalog.
        Allows for some natural language descriptions e.g. "5 minutes ago".
        By default uses the current timestamp.
    reverse: boolean, optional
        Direction to search, by default looks for a previous curve.
        If given as False, looks forward in time from the given timestamp.
    """
    instr = load(name, time, reverse)
    if load(name) == instr:
        warnings.warn("Attempted to restore instrument equivalent to current head, ignoring.")
        return
    instr._transition = Transition(
        TransitionType.restore, metadata={"time": instr.load.isoformat()}
    )
    _store_instr(instr)


class WalkHistory:
    """iterator for a instrument's history"""

    def __init__(self, name, start="now", reverse=True):
        self.name = name
        self.time = start
        self.reverse = reverse
        self.direction = -1 if reverse else 1

    def __iter__(self):
        return self

    def __next__(self):
        try:
            self.current = load(self.name, self.time, self.reverse)
        except ValueError:
            raise StopIteration
        self.time = self.current.load + self.direction * timedelta(milliseconds=1)
        return self.current


def print_history(name, n=10, start="now", reverse: bool = True):
    """
    Print the store's history of an instrument

    Parameters
    ----------
    name: str
        Name of the instrument.  The instrument name must be in the catalog
    n: int
        Number of change records to look up.  Default is 10.
    start: datetime.Datetime or str
        Date and time from which the records begin listing.  Default is "now".
    reverse: bool
        When false, history will search records forwards in time.

    Returns
    -------
    history: str
        a neatly formatted, multiline string overviewing the history of instrument changes
    """
    title_string = f"{name}, going {'backwards' if reverse else 'forwards'}"
    print(title_string + "-" * (80 - len(name)))
    for i, inst in enumerate(WalkHistory(name, start, reverse)):
        transition_type = None if inst.transition is None else inst.transition.type
        print(
            "{0:6} {1}{2} at {3}".format(
                -i if reverse else i,
                transition_type,
                "." * (20 - len(transition_type)),
                str(inst.load),
            )
        )
        if i == n:
            break
    print("<end of history>")


def store(instrument, warn=True):
    """Store an instrument into the catalog.

    Parameters
    ----------
    instrument: Instrument
        The instrument to store.
    warn: bool
        Whether or not to warn if the store is equivalent to the current head.
    """
    try:
        if load(instrument.name) == instrument:
            if warn:
                warnings.warn(
                    "Attempted to store instrument equivalent to current head, ignoring."
                )
            return
    except ValueError:
        pass  # Could mean it is not yet in store at all

    if instrument.load is None and instrument.transition.previous is not None:
        store(instrument.transition.previous, warn=False)

    if instrument.load is not None:
        restore(instrument.name, instrument.load)
        return

    _store_instr(instrument)


def _store_instr(instrument):
    if "ATTUNE_STORE" in os.environ and os.environ["ATTUNE_STORE"]:
        attune_dir = pathlib.Path(os.environ["ATTUNE_STORE"])
    else:
        attune_dir = pathlib.Path(appdirs.user_data_dir("attune", "attune"))

    while True:
        now = datetime.now(timezone.utc)
        # make datadir
        datadir = attune_dir
        datadir /= instrument.name
        datadir /= f"{now.year}"
        datadir /= f"{now.month:02}"
        datadir /= now.isoformat(timespec="milliseconds").replace("-", "").replace(":", "")
        try:
            datadir.mkdir(parents=True)
        except FileExistsError:
            continue
        else:
            break
    # store instrument
    with open(datadir / "instrument.json", "w") as f:
        instrument.save(f)
        f.write("\n")
    # store data
    if instrument.transition.data is not None:
        instrument.transition.data.save(datadir / "data.wt5")
    # store old instrument
    if instrument.transition.previous is not None:
        with open(datadir / "previous_instrument.json", "w") as f:
            instrument.transition.previous.save(f)


def undo(instrument):
    """Undo one transition."""
    if instrument.load is not None:
        return load(instrument.name, instrument.load - timedelta(milliseconds=1))
    elif instrument.transition.previous is not None:
        return instrument.transition.previous
    raise ValueError("Nothing to undo")

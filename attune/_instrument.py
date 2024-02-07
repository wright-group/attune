__all__ = ["Instrument"]


from datetime import datetime as _datetime
from typing import Dict, Optional, Union
import json

from ._arrangement import Arrangement
from ._setable import Setable
from ._note import Note
from ._transition import Transition, TransitionType


class Instrument(object):
    def __init__(
        self,
        arrangements: Dict[str, Union[Arrangement, dict]],
        setables: Dict[str, Optional[Union[Setable, dict]]] = None,
        *,
        name: Optional[str] = None,
        transition: Optional[Union[Transition, dict]] = None,
        load: Optional[float] = None,
    ):
        """Representation of a system of arrangements for an instrument.

        Parameters
        ----------
        arrangements: Dict[str, Union[Arrangement, dict]
            Dictionary of arrangements in the instrument
        setables: Dict[str, Optional[Union[Setable, dict]]]
            Default values for the instrument. Can be ignored unless you
            require your instrument to have default positions.
        name: Optional[str]
            The name of the instrument, used to store/retrieve the instrument.
        transition: Optional[Union[Transition, dict]]
            The operation which creates this instrument.
            transitions are concise records for instrument changes.
            If not given, a blank Transition (TransitionType "create") will be
            made.
        load: Optional[float]
            POSIX timestamp of the tune when retrieved from the store.
            Ignore for instruments not retrieved from the store.
        """
        self._name: Optional[str] = name
        self._arrangements: Dict["str", Arrangement] = {
            k: Arrangement(**v) if isinstance(v, dict) else v for k, v in arrangements.items()
        }
        if setables is None:
            setables = {}
        self._setables: Dict["str", Setable] = {
            k: Setable(**v) if isinstance(v, dict) else v for k, v in setables.items()
        }
        if transition is None:
            self._transition = Transition(TransitionType.create)
        elif isinstance(transition, dict):
            self._transition = Transition(**transition)
        else:
            self._transition = transition
        self._load: Optional[float] = load

    def __repr__(self):
        ret = f"Instrument({repr(self.arrangements)}, {repr(self.setables)}"
        if self.name is not None:
            ret += f", name={repr(self.name)}"
        if self.transition.type != TransitionType.create:
            ret += f", transition={repr(self.transition)}"
        return ret + ")"

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self._setables != other._setables:
            return False
        if self._arrangements != other._arrangements:
            return False
        return True

    def __call__(self, ind_value, arrangement_name=None) -> Note:
        # get correct arrangement
        valid = []
        for arrangement in self._arrangements.values():
            # we should probably do "close enough" for floating point on the edges...
            try:
                if arrangement.ind_min <= ind_value <= arrangement.ind_max:
                    valid.append(arrangement)
            except ValueError:
                if (arrangement.ind_min <= ind_value).all() and (
                    ind_value <= arrangement.ind_max
                ).all():
                    valid.append(arrangement)
        if arrangement_name is not None:
            assert arrangement_name in [v.name for v in valid]
            arrangement = self._arrangements[arrangement_name]
        elif len(valid) == 1:
            arrangement = valid[0]
        elif len(valid) == 0:
            raise ValueError(f"There are no valid arrangements at {ind_value}.")
        else:
            raise ValueError("There are multiple valid arrangements! You must specify one.")
        # call arrangement
        setable_positions = {}
        setables = self._setables.copy()
        todo = [(ind_value, tune) for tune in arrangement.tunes.items()]
        while todo:
            v, t = todo.pop(0)
            tune_name, tune = t
            if tune_name in self._arrangements:
                new = [
                    (tune(v), subtune) for subtune in self._arrangements[tune_name].tunes.items()
                ]
                todo += new
            else:
                # Since todos are appended for any subarrangement, the top-most (eg idl in idl>sig)
                # Arrangment should be used, so skip setting if it is defined in inner arrangments
                if tune_name in setable_positions:
                    continue
                setable_positions[tune_name] = tune(v)
                setables[tune_name] = Setable(tune_name)
        for setable in self._setables:
            if setable not in setable_positions and self._setables[setable].default is not None:
                setable_positions[setable] = self._setables[setable].default
        # finish
        note = Note(
            setables=self._setables,
            setable_positions=setable_positions,
            arrangement_name=arrangement.name,
        )
        return note

    def print_tree(self):
        """Print a ascii-formatted tree representation of the instrument contents."""
        print("{0}".format(self.name))
        self._print_arrangements("")

    def _print_arrangements(self, prefix):
        for i, (name, arrangement) in enumerate(self.arrangements.items()):
            if i + 1 == len(self.arrangements):
                b = "└── "
                add_prefix = "    "
            else:
                b = "├── "
                add_prefix = "│   "
            s = prefix + b + "{0}".format(name)
            print(s)
            arrangement._print_tunes(prefix + add_prefix)

    def __getitem__(self, item):
        return self._arrangements[item]

    def as_dict(self):
        """Dictionary representation for this Instrument."""
        out = {}
        out["name"] = self.name
        out["arrangements"] = {k: v.as_dict() for k, v in self._arrangements.items()}
        out["setables"] = {k: v.as_dict() for k, v in self._setables.items()}
        out["transition"] = self.transition.as_dict()
        return out

    @property
    def name(self):
        """The name of the instrument.

        This is the key that is used to store/retrieve the instrument.
        """
        return self._name

    @property
    def transition(self):
        """The transition operation that generated this instrument."""
        return self._transition

    @property
    def setables(self):
        """The setables associated with this instrument."""
        return self._setables

    @property
    def arrangements(self):
        """The arrangements associated with this instrument."""
        return self._arrangements

    @property
    def load(self):
        """The POSIX timestamp for when this instrument was created, if it was stored."""
        return self._load

    def save(self, file):
        """Save the JSON representation into an open file."""

        class NdarrayEncoder(json.JSONEncoder):
            def default(self, obj):
                if hasattr(obj, "tolist"):
                    return obj.tolist()
                return json.JSONEncoder.default(self, obj)

        json.dump(self.as_dict(), file, cls=NdarrayEncoder)
